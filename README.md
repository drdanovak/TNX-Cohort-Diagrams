# TriNetX Cohort Diagram Builder

A Streamlit app for building cohort construction diagrams for TriNetX retrospective cohort studies. Designed to accompany *Extraordinary Evidence: A Project-Based Guide to Clinical Research with Real-World Data* (Novak, 2026).

Replaces the GoogleDrawings template workflow with a structured, validation-aware builder that exports to PNG, PDF, and JSON.

## What it does

- Build a cohort diagram from a palette of TriNetX-aware node kinds (source population, inclusion, pool, index event, pre-PSM cohort, PSM characteristics, post-PSM cohort, outcome, terminal cohort, exclusion panel, exposure panel, custom).
- Drag-to-reorder or use ↑ ↓ buttons.
- Auto-generate a vertical spine of edges, then add side-panel arrows manually.
- Live preview that re-renders on every keystroke (with a manual-refresh toggle for big diagrams).
- Automated validation: catches non-monotonic cohort sizes, unequal post-PSM Ns, outcome counts exceeding cohort totals, sparse PSM covariate lists, orphan nodes, and other reviewer-flag risks.
- Export to PNG (posters, Word), PDF (manuscript figures), or JSON (save/reload, share with mentor).
- Load the statin/AD worked example with one click.

## File structure

```
tnx-cohort-builder/
├── app.py                 # Streamlit UI (tabs: Builder, Validation, Export)
├── models.py              # Pydantic data model: CohortDiagram, Node, Edge
├── palette.py             # Defaults per NodeKind (label, body, position, colors)
├── renderer.py            # CohortDiagram → graphviz.Digraph
├── validation.py          # Arithmetic and structural checks
├── examples/
│   └── statin_ad.json     # Statin/Alzheimer's worked example
├── requirements.txt       # Python deps
├── packages.txt           # System deps for Streamlit Cloud (graphviz binary)
├── .streamlit/
│   └── config.toml        # Book-aligned theme (navy/gold)
└── README.md
```

## Running locally

```bash
# 1. Install the graphviz system binary
#    macOS:        brew install graphviz
#    Ubuntu/Debian: sudo apt install graphviz
#    Windows:       https://graphviz.org/download/

# 2. Install Python deps
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Deploying to Streamlit Cloud

1. Push the directory to a GitHub repo (public or private).
2. Go to [share.streamlit.io](https://share.streamlit.io), click "New app", point it at the repo, and set `app.py` as the entry point.
3. `packages.txt` ensures the graphviz binary is installed in the Cloud environment; `requirements.txt` handles the Python dependencies. Both are picked up automatically.
4. The free tier is sufficient for class use.

You can then link the deployed URL from the book and the HSSP course materials.

### Streamlit Cloud gotchas

If you see `xargs: unmatched double quote` or `installer returned a non-zero exit code` during deploy, the cause is usually content in `packages.txt` or `requirements.txt` that confuses Streamlit Cloud's shell-based installer pipeline. The files in this repo are intentionally minimal — ASCII names only, one per line, no version constraints with `<` or `>` characters, no trailing whitespace. If you fork and modify, keep them simple.

## Data model

The whole app is a UI over a single JSON spec:

```json
{
  "meta": { "title": "...", "network": "...", "date": "...", "author": "..." },
  "nodes": [
    { "id": "...", "kind": "source", "label": "...", "body": "...", "n": 131075626, "position": "center" },
    ...
  ],
  "edges": [
    { "id": "...", "from_id": "...", "to_id": "...", "style": "solid" },
    ...
  ]
}
```

Students can save their JSON, share it with you, and you can render it without the UI:

```python
import json
from models import CohortDiagram
from renderer import render

with open("student_diagram.json") as f:
    d = CohortDiagram(**json.load(f))
g = render(d)
g.render("student_diagram", format="pdf", cleanup=True)
```

This also means the diagram spec doubles as a teaching artifact: students can share the JSON for feedback before they render the final figure.

## Design decisions

**Why Graphviz?** A cohort diagram is a directed acyclic graph. Auto-layout is the killer feature for a flexible builder — every node add/remove/reorder reflows automatically. Graphviz also exports natively to PNG, PDF, and SVG. The tradeoff is that pixel-perfect placement isn't possible.

**Why three tabs (Builder / Validation / Export)?** The Builder is fast-feedback (live preview, immediate edits). Validation is reflective (run the checks, address each issue). Export is final (download artifacts). Splitting them keeps each screen focused.

**Why flexible builder rather than strict template?** Selected for the dissertation use case — real studies have edge cases (multiple exposure panels, branching exclusions, non-PSM designs) that a strict template would force into ugly workarounds. The palette encodes the common case so the flexible builder is still easy to drive.

## Known issues

- **Index Event placement.** When the Index Event node has edges to both pre-PSM cohorts, Graphviz pulls it down to the same rank. The diagram is correct but reads with Index Event beside (rather than above) the pre-PSM row. Workarounds: use a Custom node instead, or accept the layout. A future version can use invisible spacer ranks to force vertical separation.
- **Long exclusion panels.** Very long exclusion lists (20+ items) cause vertical overflow that compresses neighbor nodes. Split into two panels if needed.
- **Edge routing.** With `splines=ortho`, complex graphs can produce occasional edge crossings. The diagram remains topologically correct; for the cleanest manuscript figure, export to PDF and edit in Illustrator/Inkscape if required.

## Extensions worth considering

- Auto-fill from a TriNetX CSV export (read the cohort/PSM/outcomes tables and pre-populate the node list).
- Compare two saved JSON specs side-by-side (useful for sensitivity analyses).
- Render directly to docx as an inline image (useful for the workbook integration).
- Pre-built templates for common TriNetX study designs beyond statin/AD (target trial emulation, new-user design, etc.).

## License

For use within the *Extraordinary Evidence* curriculum and HSSP program. Adapt freely for your own teaching contexts.
