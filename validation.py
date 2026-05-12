"""
Validation: arithmetic and structural checks on a CohortDiagram.

Returns a list of (severity, message) tuples; severity in {"error", "warning", "info"}.
"""
from __future__ import annotations

from typing import List, Tuple

from models import CohortDiagram, Node

Severity = str  # "error" | "warning" | "info"


def _center_nodes_with_n(diagram: CohortDiagram) -> List[Node]:
    return [n for n in diagram.nodes if n.position == "center" and n.n is not None]


def _by_kind(diagram: CohortDiagram, kind: str) -> List[Node]:
    return [n for n in diagram.nodes if n.kind == kind]


def validate(diagram: CohortDiagram) -> List[Tuple[Severity, str]]:
    issues: List[Tuple[Severity, str]] = []

    # 1. Successive center-spine Ns should be non-increasing.
    center_with_n = _center_nodes_with_n(diagram)
    for a, b in zip(center_with_n, center_with_n[1:]):
        if a.n is not None and b.n is not None and b.n > a.n:
            issues.append(
                (
                    "error",
                    f"Cohort N grows from '{a.label}' (n={a.n:,}) to '{b.label}' (n={b.n:,}). "
                    "Each successive pool should be at most the size of the prior.",
                )
            )

    # 2. Post-PSM cohorts should have equal Ns (TriNetX does 1:1 nearest-neighbor).
    post = _by_kind(diagram, "cohort_post_psm")
    post_ns = [n.n for n in post if n.n is not None]
    if len(post_ns) >= 2 and len(set(post_ns)) > 1:
        labels = ", ".join(f"'{n.label}' (n={n.n:,})" for n in post if n.n is not None)
        issues.append(
            (
                "error",
                f"Post-PSM cohort sizes differ: {labels}. TriNetX performs 1:1 "
                "nearest-neighbor matching, so both groups should have identical N.",
            )
        )

    # 3. Each post-PSM cohort N should be <= its pre-PSM counterpart.
    pre = _by_kind(diagram, "cohort_pre_psm")
    # Heuristic pairing: by position (left/right).
    for side in ("left", "right"):
        pre_side = [n for n in pre if n.position == side and n.n is not None]
        post_side = [n for n in post if n.position == side and n.n is not None]
        if pre_side and post_side:
            pre_n = pre_side[-1].n
            post_n = post_side[-1].n
            if pre_n is not None and post_n is not None and post_n > pre_n:
                issues.append(
                    (
                        "error",
                        f"Post-PSM {side} cohort (n={post_n:,}) is larger than its "
                        f"pre-PSM counterpart (n={pre_n:,}).",
                    )
                )

    # 4. Terminal cohort outcome N should not exceed total N (parsed from body).
    for term in _by_kind(diagram, "terminal"):
        total_n, outcome_n = _parse_terminal_counts(term)
        if total_n is not None and outcome_n is not None and outcome_n > total_n:
            issues.append(
                (
                    "error",
                    f"In terminal cohort '{term.label}', outcome count ({outcome_n:,}) "
                    f"exceeds total ({total_n:,}).",
                )
            )

    # 5. Warnings.
    if not _by_kind(diagram, "exclusion_panel"):
        issues.append(
            (
                "warning",
                "No exclusion criteria panel found. Most TriNetX studies require "
                "explicit exclusions to address confounding by indication.",
            )
        )

    psm_nodes = _by_kind(diagram, "psm")
    for p in psm_nodes:
        cov_count = sum(1 for line in p.body.split("\n") if line.strip())
        if cov_count < 5:
            issues.append(
                (
                    "warning",
                    f"PSM node '{p.label}' lists only {cov_count} covariates. Reviewers "
                    "typically expect at least demographics, key comorbidities, and "
                    "relevant medications.",
                )
            )

    # 6. Orphan nodes (no edges in or out).
    edge_endpoints = {e.from_id for e in diagram.edges} | {e.to_id for e in diagram.edges}
    for node in diagram.nodes:
        if node.id not in edge_endpoints and len(diagram.nodes) > 1:
            issues.append(
                (
                    "warning",
                    f"Node '{node.label or node.kind}' has no edges. It will float "
                    "disconnected in the diagram.",
                )
            )

    # 7. Structural info checks.
    if not _by_kind(diagram, "source"):
        issues.append(
            ("info", "No Source Population node found. Most diagrams start with one.")
        )
    if not _by_kind(diagram, "outcome") and not _by_kind(diagram, "terminal"):
        issues.append(
            ("info", "No Outcome or Terminal Cohort node found. The diagram ends mid-flow.")
        )

    return issues


def _parse_terminal_counts(node: Node) -> tuple[int | None, int | None]:
    """Best-effort parse of 'Total: N' and 'Outcome: N' from a terminal node body."""
    import re

    total = None
    outcome = None
    for line in node.body.split("\n"):
        line_lower = line.lower()
        nums = re.findall(r"[\d,]+", line)
        if "total" in line_lower and nums:
            try:
                total = int(nums[0].replace(",", ""))
            except ValueError:
                pass
        elif nums and outcome is None and "total" not in line_lower:
            try:
                outcome = int(nums[0].replace(",", ""))
            except ValueError:
                pass
    return total, outcome
