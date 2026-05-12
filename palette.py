"""
Palette: defaults for each NodeKind.

When the user adds a node from the palette, these defaults are applied.
The user can override any of them via the edit form.
"""
from typing import Dict, TypedDict

from models import NodeKind, Position

# Book-aligned palette
NAVY = "#1B3A5C"
GOLD = "#C9982E"
TEAL = "#4A8B8C"  # complementary teal
LIGHT_GRAY = "#E8E8E8"
WHITE = "#FFFFFF"


class PaletteDefaults(TypedDict):
    display_name: str
    default_label: str
    default_body: str
    default_position: Position
    fill_color: str
    border_color: str
    border_style: str
    text_color: str
    help_text: str


PALETTE: Dict[NodeKind, PaletteDefaults] = {
    "source": {
        "display_name": "Source Population",
        "default_label": "TriNetX [Network Name]",
        "default_body": "[Date of Study]",
        "default_position": "center",
        "fill_color": WHITE,
        "border_color": NAVY,
        "border_style": "bold",
        "text_color": NAVY,
        "help_text": "The source network and total patient count, typically the topmost node.",
    },
    "inclusion": {
        "display_name": "Inclusion Criterion",
        "default_label": "Age > 45",
        "default_body": "",
        "default_position": "center",
        "fill_color": WHITE,
        "border_color": NAVY,
        "border_style": "solid",
        "text_color": NAVY,
        "help_text": "A filter step in the inclusion sequence, with the N remaining after the filter.",
    },
    "pool": {
        "display_name": "Total Pool",
        "default_label": "Total pool meeting inclusion criteria",
        "default_body": "Control Group Event:\n[description] (n=...)\n\nTreatment Group Event:\n[description] (n=...)",
        "default_position": "center",
        "fill_color": LIGHT_GRAY,
        "border_color": NAVY,
        "border_style": "solid",
        "text_color": NAVY,
        "help_text": "The full pool meeting baseline inclusion, with per-cohort event definitions.",
    },
    "index_event": {
        "default_label": "Analysis Time Frame Relative to Index Event",
        "default_body": "[description of index event and time window]",
        "default_position": "center",
        "display_name": "Index Event / Time Frame",
        "fill_color": WHITE,
        "border_color": NAVY,
        "border_style": "solid",
        "text_color": NAVY,
        "help_text": "Defines when the index event occurs and the analysis time frame relative to it.",
    },
    "cohort_pre_psm": {
        "display_name": "Cohort (pre-PSM)",
        "default_label": "Total meeting inclusion criteria for [Group]",
        "default_body": "",
        "default_position": "left",
        "fill_color": WHITE,
        "border_color": NAVY,
        "border_style": "solid",
        "text_color": NAVY,
        "help_text": "Pre-matching cohort. Place left or right.",
    },
    "psm": {
        "display_name": "PSM Characteristics",
        "default_label": "Propensity Score Matching (PSM) Characteristics:",
        "default_body": "- Age at Index\n- Male\n- Female\n- [add covariates]",
        "default_position": "center",
        "fill_color": LIGHT_GRAY,
        "border_color": NAVY,
        "border_style": "solid",
        "text_color": NAVY,
        "help_text": "List of covariates included in propensity score matching.",
    },
    "cohort_post_psm": {
        "display_name": "Cohort (post-PSM)",
        "default_label": "[Group] After PSM",
        "default_body": "",
        "default_position": "left",
        "fill_color": LIGHT_GRAY,
        "border_color": NAVY,
        "border_style": "solid",
        "text_color": NAVY,
        "help_text": "Post-matching cohort. Place left or right to mirror the pre-PSM node.",
    },
    "outcome": {
        "display_name": "Outcome",
        "default_label": "Outcome: [Name] ([Code])",
        "default_body": "",
        "default_position": "center",
        "fill_color": WHITE,
        "border_color": NAVY,
        "border_style": "solid",
        "text_color": NAVY,
        "help_text": "The outcome of interest and its code.",
    },
    "terminal": {
        "display_name": "Terminal Cohort",
        "default_label": "[Group]",
        "default_body": "Total: ...\n[Outcome]: ... (...%)",
        "default_position": "left",
        "fill_color": LIGHT_GRAY,
        "border_color": NAVY,
        "border_style": "solid",
        "text_color": NAVY,
        "help_text": "Final cohort with total N and N with outcome.",
    },
    "exclusion_panel": {
        "display_name": "Exclusion Panel",
        "default_label": "Exclusion Criteria",
        "default_body": "[Condition] ([Code]): (n=...)\n[Condition] ([Code]): (n=...)",
        "default_position": "right",
        "fill_color": WHITE,
        "border_color": NAVY,
        "border_style": "dashed",
        "text_color": NAVY,
        "help_text": "Side panel listing exclusion criteria with codes and counts. Connects via dashed edge.",
    },
    "exposure_panel": {
        "display_name": "Exposure Panel",
        "default_label": "Received at least one of the following at any dosage:",
        "default_body": "[Drug] (RxNorm:[code]): (n=...)\n[Drug] (RxNorm:[code]): (n=...)",
        "default_position": "right",
        "fill_color": WHITE,
        "border_color": NAVY,
        "border_style": "dashed",
        "text_color": NAVY,
        "help_text": "Side panel listing the exposure drugs with RxNorm codes and counts.",
    },
    "custom": {
        "display_name": "Custom",
        "default_label": "Custom node",
        "default_body": "",
        "default_position": "center",
        "fill_color": WHITE,
        "border_color": NAVY,
        "border_style": "solid",
        "text_color": NAVY,
        "help_text": "A free-form node. Use when no other kind fits.",
    },
}


def kind_options() -> list[tuple[NodeKind, str]]:
    """Return (kind, display_name) pairs in palette display order."""
    return [(k, v["display_name"]) for k, v in PALETTE.items()]
