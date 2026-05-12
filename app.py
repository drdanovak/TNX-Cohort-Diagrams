"""
TriNetX Cohort Diagram Builder
A Streamlit app for building cohort construction diagrams.

Run locally:  streamlit run app.py
Deploy:       Streamlit Cloud, free tier
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
from streamlit_sortables import sort_items

from models import CohortDiagram, Node, Edge
from palette import PALETTE, kind_options, NAVY, GOLD
from renderer import render, auto_spine_edges
from validation import validate


# ---------------------------------------------------------------------------
# Page config and styles
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="TriNetX Cohort Diagram Builder",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    f"""
    <style>
      h1 {{ color: {NAVY}; }}
      .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {{
        font-size: 1.05rem;
        font-weight: 600;
      }}
      .node-card {{
        background: #F8F8F4;
        border-left: 4px solid {NAVY};
        padding: 0.6rem 0.8rem;
        margin-bottom: 0.5rem;
        border-radius: 4px;
      }}
      .node-card-label {{
        font-weight: 600;
        color: {NAVY};
      }}
      .node-card-kind {{
        font-size: 0.85rem;
        color: #666;
        font-style: italic;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def _empty_diagram() -> CohortDiagram:
    return CohortDiagram()


def _load_example() -> CohortDiagram:
    example_path = Path(__file__).parent / "examples" / "statin_ad.json"
    if example_path.exists():
        with open(example_path) as f:
            return CohortDiagram(**json.load(f))
    return _empty_diagram()


def get_diagram() -> CohortDiagram:
    if "diagram" not in st.session_state:
        st.session_state.diagram = _empty_diagram()
    return st.session_state.diagram


def set_diagram(d: CohortDiagram) -> None:
    st.session_state.diagram = d


def get_render_mode() -> str:
    """Return 'live' or 'manual' depending on user toggle."""
    return st.session_state.get("render_mode", "live")


# ---------------------------------------------------------------------------
# Sidebar: load, save, reset, render mode
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(f"### TriNetX Cohort Builder")
    st.caption("Build a cohort construction diagram for your TriNetX manuscript.")

    if st.button("📋 Load example: Statin/AD", use_container_width=True):
        set_diagram(_load_example())
        st.rerun()

    if st.button("🆕 New diagram", use_container_width=True):
        set_diagram(_empty_diagram())
        st.rerun()

    uploaded = st.file_uploader("Load from JSON", type=["json"], key="json_upload")
    if uploaded is not None:
        try:
            data = json.loads(uploaded.read().decode("utf-8"))
            set_diagram(CohortDiagram(**data))
            st.success("Diagram loaded.")
        except Exception as e:
            st.error(f"Could not load: {e}")

    st.divider()
    st.markdown("**Performance**")
    st.radio(
        "Preview update",
        options=["live", "manual"],
        index=0,
        key="render_mode",
        help=(
            "Live re-renders on every keystroke (snappy for small diagrams). "
            "Manual adds a Refresh button (better for 15+ node diagrams)."
        ),
        horizontal=True,
    )

    st.divider()
    st.caption(
        "Built to accompany *Extraordinary Evidence: A Project-Based Guide to "
        "Clinical Research with Real-World Data*."
    )


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_builder, tab_validate, tab_export = st.tabs(
    ["🧱 Builder", "✅ Validation", "💾 Export"]
)


# ---------------------------------------------------------------------------
# Builder tab
# ---------------------------------------------------------------------------

def render_node_editor(node: Node, index: int) -> bool:
    """Render the in-place edit form for a single node.

    Returns True if the user clicked Save (so the caller can rerun).
    """
    with st.expander(f"✏️ Edit: {node.label or node.kind}", expanded=False):
        new_label = st.text_input("Label (bold header)", value=node.label, key=f"label_{node.id}")
        new_body = st.text_area(
            "Body (one item per line)",
            value=node.body,
            key=f"body_{node.id}",
            height=120,
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            new_n_str = st.text_input(
                "Patient count (N)",
                value="" if node.n is None else str(node.n),
                key=f"n_{node.id}",
                help="Plain integer; commas will be added automatically when rendered.",
            )
        with col2:
            new_position = st.selectbox(
                "Column",
                options=["center", "left", "right"],
                index=["center", "left", "right"].index(node.position),
                key=f"pos_{node.id}",
            )
        with col3:
            kind_keys = [k for k, _ in kind_options()]
            new_kind = st.selectbox(
                "Kind",
                options=kind_keys,
                index=kind_keys.index(node.kind),
                format_func=lambda k: PALETTE[k]["display_name"],
                key=f"kind_{node.id}",
            )

        # Parse N
        try:
            new_n = int(new_n_str.replace(",", "").strip()) if new_n_str.strip() else None
        except ValueError:
            st.warning("Patient count must be an integer.")
            new_n = node.n

        # Detect change and update in-place; in live mode we update every rerun.
        if (
            new_label != node.label
            or new_body != node.body
            or new_n != node.n
            or new_position != node.position
            or new_kind != node.kind
        ):
            node.label = new_label
            node.body = new_body
            node.n = new_n
            node.position = new_position
            node.kind = new_kind

    return False


def render_builder_tab() -> None:
    diagram = get_diagram()

    col_left, col_right = st.columns([1, 1])

    # ---- LEFT: node list + add controls + edge editor ----
    with col_left:
        st.markdown("### Nodes")

        # Add-node row.
        add_col1, add_col2 = st.columns([3, 1])
        with add_col1:
            kind_keys = [k for k, _ in kind_options()]
            kind_to_add = st.selectbox(
                "Add new node",
                options=kind_keys,
                format_func=lambda k: PALETTE[k]["display_name"],
                key="kind_to_add",
                label_visibility="collapsed",
            )
        with add_col2:
            if st.button("➕ Add", use_container_width=True):
                defaults = PALETTE[kind_to_add]
                new_node = Node(
                    kind=kind_to_add,
                    label=defaults["default_label"],
                    body=defaults["default_body"],
                    position=defaults["default_position"],
                )
                diagram.nodes.append(new_node)
                st.rerun()

        if not diagram.nodes:
            st.info("No nodes yet. Add one from the palette above, or load the Statin/AD example from the sidebar.")
            return

        # Drag-to-reorder list. We use streamlit-sortables; if it's unavailable,
        # the up/down buttons below still work.
        st.caption("Drag node cards to reorder, or use ↑ ↓ buttons.")

        sortable_items = [
            f"{i}: {n.label or PALETTE[n.kind]['display_name']}"
            for i, n in enumerate(diagram.nodes)
        ]
        sorted_items = sort_items(sortable_items, key=f"sortable_{len(diagram.nodes)}")
        if sorted_items != sortable_items:
            # Map sorted display strings back to indices.
            new_order_indices = [int(s.split(":")[0]) for s in sorted_items]
            new_order_ids = [diagram.nodes[i].id for i in new_order_indices]
            diagram.reorder(new_order_ids)
            st.rerun()

        # Render each node card with edit/move/dup/delete.
        for i, node in enumerate(list(diagram.nodes)):
            with st.container():
                kind_name = PALETTE[node.kind]["display_name"]
                st.markdown(
                    f'<div class="node-card">'
                    f'<span class="node-card-label">{node.label or "(unlabeled)"}</span><br>'
                    f'<span class="node-card-kind">{kind_name} · {node.position}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
                with btn_col1:
                    if st.button("↑", key=f"up_{node.id}", use_container_width=True, disabled=(i == 0)):
                        diagram.move_node(node.id, -1)
                        st.rerun()
                with btn_col2:
                    if st.button("↓", key=f"down_{node.id}", use_container_width=True, disabled=(i == len(diagram.nodes) - 1)):
                        diagram.move_node(node.id, +1)
                        st.rerun()
                with btn_col3:
                    if st.button("📄 Dup", key=f"dup_{node.id}", use_container_width=True):
                        dup = node.model_copy(update={"id": Node().id})
                        diagram.nodes.insert(i + 1, dup)
                        st.rerun()
                with btn_col4:
                    if st.button("🗑️ Del", key=f"del_{node.id}", use_container_width=True):
                        diagram.remove_node(node.id)
                        st.rerun()

                render_node_editor(node, i)

        # Edge editor.
        st.markdown("### Edges")
        ec1, ec2 = st.columns([3, 1])
        with ec1:
            st.caption(
                "Hybrid mode: use the button to auto-connect center nodes in order, "
                "then add side-panel edges manually below."
            )
        with ec2:
            if st.button("🔗 Auto-connect spine", use_container_width=True):
                # Replace any existing auto-generated edges with a fresh spine.
                diagram.edges = auto_spine_edges(diagram)
                st.rerun()

        # Existing edges, one row each.
        node_id_to_label = {
            n.id: f"{n.label or PALETTE[n.kind]['display_name']}" for n in diagram.nodes
        }
        for edge in list(diagram.edges):
            ec_a, ec_b, ec_c, ec_d = st.columns([3, 3, 2, 1])
            with ec_a:
                st.text_input(
                    "From",
                    value=node_id_to_label.get(edge.from_id, edge.from_id),
                    key=f"edge_from_label_{edge.id}",
                    disabled=True,
                    label_visibility="collapsed",
                )
            with ec_b:
                st.text_input(
                    "To",
                    value=node_id_to_label.get(edge.to_id, edge.to_id),
                    key=f"edge_to_label_{edge.id}",
                    disabled=True,
                    label_visibility="collapsed",
                )
            with ec_c:
                new_style = st.selectbox(
                    "Style",
                    options=["solid", "dashed", "dotted", "bold"],
                    index=["solid", "dashed", "dotted", "bold"].index(edge.style),
                    key=f"edge_style_{edge.id}",
                    label_visibility="collapsed",
                )
                edge.style = new_style
            with ec_d:
                if st.button("✕", key=f"edge_del_{edge.id}"):
                    diagram.edges = [e for e in diagram.edges if e.id != edge.id]
                    st.rerun()

        # Add an edge.
        with st.expander("➕ Add edge"):
            options = list(node_id_to_label.items())
            if len(options) < 2:
                st.caption("Add at least two nodes first.")
            else:
                ae1, ae2, ae3 = st.columns([2, 2, 1])
                with ae1:
                    from_id = st.selectbox(
                        "From",
                        options=[i for i, _ in options],
                        format_func=lambda i: node_id_to_label[i],
                        key="new_edge_from",
                    )
                with ae2:
                    to_id = st.selectbox(
                        "To",
                        options=[i for i, _ in options],
                        format_func=lambda i: node_id_to_label[i],
                        key="new_edge_to",
                    )
                with ae3:
                    if st.button("Add", key="add_edge_btn"):
                        if from_id != to_id:
                            diagram.edges.append(Edge(from_id=from_id, to_id=to_id))
                            st.rerun()

    # ---- RIGHT: preview ----
    with col_right:
        st.markdown("### Preview")

        if get_render_mode() == "manual":
            if st.button("🔄 Refresh preview"):
                st.session_state["_force_refresh"] = st.session_state.get("_force_refresh", 0) + 1

        if diagram.nodes:
            try:
                g = render(diagram)
                st.graphviz_chart(g.source, use_container_width=True)
            except Exception as e:
                st.error(f"Could not render: {e}")
        else:
            st.info("Add nodes to see a preview.")


# ---------------------------------------------------------------------------
# Validation tab
# ---------------------------------------------------------------------------

def render_validation_tab() -> None:
    diagram = get_diagram()

    st.markdown("### Study metadata")
    mc1, mc2 = st.columns(2)
    with mc1:
        diagram.meta.title = st.text_input("Study title", value=diagram.meta.title)
        diagram.meta.network = st.text_input("TriNetX network", value=diagram.meta.network)
    with mc2:
        diagram.meta.date = st.text_input("Date / data cut", value=diagram.meta.date)
        diagram.meta.author = st.text_input("Author(s)", value=diagram.meta.author)

    st.divider()
    st.markdown("### Diagram checks")

    if not diagram.nodes:
        st.info("Build a diagram first.")
        return

    issues = validate(diagram)

    if not issues:
        st.success("No issues found. The diagram passes all automated checks.")
        return

    errors = [m for sev, m in issues if sev == "error"]
    warnings = [m for sev, m in issues if sev == "warning"]
    infos = [m for sev, m in issues if sev == "info"]

    if errors:
        st.markdown("#### 🔴 Errors")
        st.caption("These usually indicate the diagram doesn't add up arithmetically.")
        for m in errors:
            st.error(m)

    if warnings:
        st.markdown("#### 🟡 Warnings")
        st.caption("Reviewer-flag risks. Worth addressing before submission.")
        for m in warnings:
            st.warning(m)

    if infos:
        st.markdown("#### 🔵 Info")
        for m in infos:
            st.info(m)


# ---------------------------------------------------------------------------
# Export tab
# ---------------------------------------------------------------------------

def render_export_tab() -> None:
    diagram = get_diagram()

    if not diagram.nodes:
        st.info("Build a diagram first, then come back to export.")
        return

    st.markdown("### Download")
    st.caption("Choose your format. PNG for posters and Word; PDF for manuscript figures; JSON to save your work or share with a mentor.")

    g = render(diagram)
    base_name = (diagram.meta.title or "cohort_diagram").replace(" ", "_").lower()

    col1, col2, col3 = st.columns(3)
    with col1:
        png_bytes = g.pipe(format="png")
        st.download_button(
            "⬇️ PNG",
            data=png_bytes,
            file_name=f"{base_name}.png",
            mime="image/png",
            use_container_width=True,
        )
    with col2:
        pdf_bytes = g.pipe(format="pdf")
        st.download_button(
            "⬇️ PDF",
            data=pdf_bytes,
            file_name=f"{base_name}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with col3:
        json_bytes = diagram.model_dump_json(indent=2).encode("utf-8")
        st.download_button(
            "⬇️ JSON",
            data=json_bytes,
            file_name=f"{base_name}.json",
            mime="application/json",
            use_container_width=True,
        )

    st.divider()
    st.markdown("### Preview")
    st.graphviz_chart(g.source, use_container_width=True)


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

with tab_builder:
    render_builder_tab()
with tab_validate:
    render_validation_tab()
with tab_export:
    render_export_tab()
