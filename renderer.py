"""
Renderer: turns a CohortDiagram into a graphviz.Digraph.

Design notes:
- Each node renders as an HTML-like table label so we can control bold/body/N
  formatting independently.
- left/right positioned nodes are placed in rank=same subgraphs with their
  most-recent center-spine neighbor, so they sit alongside it rather than above
  or below.
- Edge style follows the source node's border style by default (dashed panels
  produce dashed edges) unless the user has explicitly chosen a style.
"""
from __future__ import annotations

import html
from typing import List

import graphviz

from models import CohortDiagram, Node, Edge
from palette import PALETTE


def _fmt_n(n: int | None) -> str:
    if n is None:
        return ""
    return f"(n={n:,})"


def _resolve_style(node: Node) -> dict:
    """Resolve node style by overlaying user overrides onto palette defaults."""
    defaults = PALETTE[node.kind]
    return {
        "fill_color": node.fill_color or defaults["fill_color"],
        "border_color": node.border_color or defaults["border_color"],
        "border_style": node.border_style or defaults["border_style"],
        "text_color": node.text_color or defaults["text_color"],
    }


def _node_html_label(node: Node) -> str:
    """Build an HTML-like Graphviz label for a node.

    Format:
      <b>LABEL</b>
      body line 1
      body line 2
      ...
      (n=12,345)
    """
    style = _resolve_style(node)
    text_color = style["text_color"]

    parts: List[str] = []
    if node.label:
        parts.append(
            f'<font color="{text_color}"><b>{html.escape(node.label)}</b></font>'
        )
    if node.body:
        body_lines = [html.escape(line) for line in node.body.split("\n")]
        body_html = "<br/>".join(body_lines)
        parts.append(f'<font color="{text_color}">{body_html}</font>')
    if node.n is not None:
        parts.append(f'<font color="{text_color}">{_fmt_n(node.n)}</font>')

    inner = "<br/>".join(parts) if parts else "&nbsp;"
    return f"<{inner}>"


def _node_attrs(node: Node) -> dict:
    style = _resolve_style(node)
    # Map our border_style to Graphviz style attribute.
    border_style_map = {
        "solid": "filled",
        "dashed": "filled,dashed",
        "dotted": "filled,dotted",
        "bold": "filled,bold",
    }
    return {
        "shape": "box",
        "style": border_style_map.get(style["border_style"], "filled"),
        "fillcolor": style["fill_color"],
        "color": style["border_color"],
        "fontname": "Arial",
        "fontsize": "10",
        "margin": "0.15,0.10",
    }


def _edge_attrs(edge: Edge, source_node: Node | None, target_node: Node | None) -> dict:
    # If user explicitly set a style, use it. Otherwise inherit from source node's
    # border style (dashed panel -> dashed edge looks correct).
    style = edge.style
    if source_node is not None and source_node.border_style:
        if edge.style == "solid" and source_node.border_style == "dashed":
            style = "dashed"

    attrs: dict = {
        "color": "#333333",
        "arrowsize": "0.7",
        "penwidth": "1.2",
    }
    if style != "solid":
        attrs["style"] = style
    if edge.label:
        attrs["label"] = edge.label
        attrs["fontname"] = "Arial"
        attrs["fontsize"] = "9"
    # If either endpoint is a side panel, don't let this edge influence ranking.
    # This keeps panels from pulling spine nodes off their proper row.
    side_kinds = {"exclusion_panel", "exposure_panel"}
    if (source_node and source_node.kind in side_kinds) or (
        target_node and target_node.kind in side_kinds
    ):
        attrs["constraint"] = "false"
    return attrs


def render(diagram: CohortDiagram) -> graphviz.Digraph:
    """Render the diagram to a graphviz.Digraph object.

    The caller controls output format via .pipe(format=...) or .render(...).
    """
    g = graphviz.Digraph("cohort_diagram", format="png")
    g.attr(
        rankdir="TB",
        splines="ortho",
        nodesep="0.4",
        ranksep="0.6",
        bgcolor="white",
        fontname="Arial",
        newrank="true",
    )
    g.attr("node", fontname="Arial")
    g.attr("edge", fontname="Arial")

    # Render every node.
    for node in diagram.nodes:
        g.node(node.id, label=_node_html_label(node), **_node_attrs(node))

    # Layout strategy:
    #
    # For each side-panel (left/right) node, find the spine node it points TO or
    # FROM via a user edge, and place them in the same rank. This respects user
    # intent: an exclusion panel that arrows into "Age > 45" sits beside it,
    # while an exposure panel that arrows into "Statin Group pre-PSM" sits
    # beside that one.
    #
    # Fallback: if no edge connects the side node to a spine node, pair it with
    # the most-recently-declared spine node in document order.
    spine_ids = {n.id for n in diagram.nodes if n.position == "center"}
    side_to_anchor: dict[str, str] = {}

    for node in diagram.nodes:
        if node.position == "center":
            continue
        anchor: str | None = None
        for e in diagram.edges:
            if e.from_id == node.id and e.to_id in spine_ids:
                anchor = e.to_id
                break
            if e.to_id == node.id and e.from_id in spine_ids:
                anchor = e.from_id
                break
        if anchor is None:
            prev_spine: str | None = None
            for n in diagram.nodes:
                if n.id == node.id:
                    break
                if n.position == "center":
                    prev_spine = n.id
            anchor = prev_spine
        if anchor is not None:
            side_to_anchor[node.id] = anchor

    rank_groups: dict[str, list[str]] = {}
    for side_id, anchor_id in side_to_anchor.items():
        rank_groups.setdefault(anchor_id, []).append(side_id)

    for anchor_id, side_ids in rank_groups.items():
        with g.subgraph() as s:
            s.attr(rank="same")
            anchor_node = diagram.node_by_id(anchor_id)
            if anchor_node is not None:
                s.node(
                    anchor_id,
                    label=_node_html_label(anchor_node),
                    **_node_attrs(anchor_node),
                )
            for sid in side_ids:
                node = diagram.node_by_id(sid)
                if node is not None:
                    s.node(sid, label=_node_html_label(node), **_node_attrs(node))

    # Also group same-kind cohort rows (pre-PSM left + pre-PSM right, etc.)
    # at the same rank so they sit horizontally.
    for kind in ("cohort_pre_psm", "cohort_post_psm", "terminal"):
        peer_nodes = [n for n in diagram.nodes if n.kind == kind]
        if len(peer_nodes) >= 2:
            with g.subgraph() as s:
                s.attr(rank="same")
                for n in peer_nodes:
                    s.node(n.id, label=_node_html_label(n), **_node_attrs(n))

    # Render edges.
    for edge in diagram.edges:
        source = diagram.node_by_id(edge.from_id)
        target = diagram.node_by_id(edge.to_id)
        g.edge(edge.from_id, edge.to_id, **_edge_attrs(edge, source, target))

    return g


def auto_spine_edges(diagram: CohortDiagram) -> List[Edge]:
    """Generate a vertical spine of edges connecting consecutive center nodes
    in document order. Side-panel nodes (left/right) are connected to the
    nearest preceding center node with a dashed edge.

    Does not mutate; returns a list of Edge objects.
    """
    edges: List[Edge] = []
    center_ids = [n.id for n in diagram.nodes if n.position == "center"]
    for a, b in zip(center_ids, center_ids[1:]):
        edges.append(Edge(from_id=a, to_id=b, style="solid"))

    # Side panels: connect from preceding center node.
    prev_center: str | None = None
    for node in diagram.nodes:
        if node.position == "center":
            prev_center = node.id
        elif prev_center is not None:
            # Panels typically receive an arrow INTO the spine, mimicking
            # "exclusion panel -> pool". Direction matches the statin/AD figure.
            edges.append(Edge(from_id=node.id, to_id=prev_center, style="dashed"))
    return edges
