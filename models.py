"""
Data models for the TriNetX cohort diagram spec.

The entire app is a thin UI over a single JSON document conforming to
CohortDiagram. The renderer and validator both consume this model.
"""
from __future__ import annotations

from typing import List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


NodeKind = Literal[
    "source",
    "inclusion",
    "pool",
    "index_event",
    "cohort_pre_psm",
    "psm",
    "cohort_post_psm",
    "outcome",
    "terminal",
    "exclusion_panel",
    "exposure_panel",
    "custom",
]

Position = Literal["center", "left", "right"]
EdgeStyle = Literal["solid", "dashed", "dotted", "bold"]


def _new_id() -> str:
    return f"n_{uuid4().hex[:8]}"


class Meta(BaseModel):
    title: str = ""
    network: str = ""
    date: str = ""
    author: str = ""


class Node(BaseModel):
    id: str = Field(default_factory=_new_id)
    kind: NodeKind = "custom"
    label: str = ""
    body: str = ""  # multiline; rendered with line breaks
    n: Optional[int] = None  # patient count; rendered with commas
    position: Position = "center"
    # Style overrides; if None, palette defaults are used at render time.
    fill_color: Optional[str] = None
    border_color: Optional[str] = None
    border_style: Optional[Literal["solid", "dashed", "dotted", "bold"]] = None
    text_color: Optional[str] = None


class Edge(BaseModel):
    id: str = Field(default_factory=_new_id)
    from_id: str
    to_id: str
    label: str = ""
    style: EdgeStyle = "solid"


class CohortDiagram(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    nodes: List[Node] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)

    def node_by_id(self, node_id: str) -> Optional[Node]:
        for n in self.nodes:
            if n.id == node_id:
                return n
        return None

    def remove_node(self, node_id: str) -> None:
        self.nodes = [n for n in self.nodes if n.id != node_id]
        self.edges = [
            e for e in self.edges if e.from_id != node_id and e.to_id != node_id
        ]

    def move_node(self, node_id: str, delta: int) -> None:
        idx = next((i for i, n in enumerate(self.nodes) if n.id == node_id), None)
        if idx is None:
            return
        new_idx = max(0, min(len(self.nodes) - 1, idx + delta))
        if new_idx == idx:
            return
        node = self.nodes.pop(idx)
        self.nodes.insert(new_idx, node)

    def reorder(self, new_order: List[str]) -> None:
        """Reorder nodes to match the given list of IDs."""
        by_id = {n.id: n for n in self.nodes}
        # Preserve any IDs missing from new_order at the end (defensive).
        new_nodes = [by_id[i] for i in new_order if i in by_id]
        remaining = [n for n in self.nodes if n.id not in set(new_order)]
        self.nodes = new_nodes + remaining
