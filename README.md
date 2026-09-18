# 📖 HR Intelligence System

**A dataset-agnostic HR analytics platform — upload any HR export and get a full analytics suite, automatically.**

🔗 **Live demo:** [hr-intelligence.streamlit.app](https://hr-intelligence.streamlit.app/)

---

## The Problem

Most "HR dashboard" projects are secretly built around one specific spreadsheet. Rename a column, and the whole thing breaks. This project was built to solve that specific problem: **the dashboard should adapt to the data, not the other way around.**

Swap the dataset — a different HR export, different column names, different structure — and the system re-maps itself, re-cleans itself, and every page that depends on data that isn't present simply adapts (hides a chart, hides a whole page, or shows what it can) instead of crashing.

## Key Features

### 🔄 Dataset-Agnostic Core
- **Canonical Schema** (`canonical_schema.py`) — 18 standard HR fields (`salary`, `department`, `performance_score`, etc.) that every other part of the system talks to, instead of raw column names.
- **Auto-Mapping** (`schema_mapper.py`) — matches any incoming file's real column names to the canonical schema via exact + fuzzy matching, and remembers the mapping for next time.
- **Upload Your Own Data** — a dedicated page lets you upload a CSV/XLSX, review the auto-detected column mapping, correct anything wrong, and load it. Every other page picks up the new dataset instantly, no code changes.
- **Graceful Degradation** — if an uploaded dataset is missing a whole category of data (e.g. no engagement scores), the relevant page or chart section hides itself instead of crashing or showing `NaN`.

### 🧹 Automated Data Cleaning
- Rule-based, transparent cleaning (`data_cleaner.py`) — no silent guesses:
  - A missing value is never blindly deleted or filled.
  - `termination_date` being empty means "still employed," not missing data.
  - Categorical fields fill with `"Unknown"`; numeric fields fill with the median **only** if under 30% is missing — otherwise it's flagged for manual review, not faked.
  - Outliers are reported, never silently removed (they're usually real — e.g. executive salaries).
- **Data Quality Score** — a single, honestly-computed percentage (completeness + duplicate check, correctly excluding fields where "empty" is a valid state).
- A dynamic, numbered audit log explaining exactly what was found and what was done about it — regenerated fresh for whatever dataset is currently loaded.

### 📊 Analytics Pages
| Page | What it shows |
|---|---|
| **Welcome** | The register's title page — a text-only cover with a table of contents, no stock imagery, leading into Home |
| **Home** | Pipeline overview KPIs (raw vs. cleaned records, active workforce, departments, average compensation) |
| **Finance & Compensation** | Payroll by department, salary distribution, salary vs. performance tier, salary vs. retention — every chart is click-to-filter and combines with the others |
| **Performance & Engagement** | Performance tier breakdown, engagement vs. satisfaction, performance by department, special projects vs. performance |
| **Attendance & Reliability** | Absences by department, absence distribution, a combined attendance-vs-attrition signal chart, and a high-risk watchlist |
| **Recruitment & Turnover** | Sourcing channel volume *and* quality (turnover rate by source), top termination drivers, hiring trend over time, tenure-at-exit analysis |
| **Recommended Actions** | Rule-based recommendations, generated fresh from whatever dataset is loaded, shown as memo cards — the highest-priority one gets a rotated "URGENT" stamp |
| **Predictive Attrition** | A Random Forest classifier trained on historical outcomes, with transparent feature importances and a ranked risk watchlist for the current active workforce |

### 🖱️ Click-to-Filter Cross-Filtering
Charts aren't just static — click a bar on most pages and every other chart/metric on that page filters to match, with selections combining (AND logic) across multiple charts. Built entirely on Streamlit's native `on_select`, no extra libraries.

### 🎨 Custom Design System — "Personnel Ledger"
A fully custom theme built around the subject matter itself instead of a generic SaaS card kit: the system is styled like a bound personnel register rather than a dashboard app.
- **Paper + cover, not cards and shadows** — a warm paper-cream content area, a dark ledger-green sidebar standing in for the register's cover, and hairline rules in place of floating white cards with drop shadows.
- **Typography with a job to do** — a serif (Source Serif 4) for headings, like a title page; a monospace (JetBrains Mono) for every number — salaries, percentages, dates — so figures line up like real ledger entries; Inter for body copy.
- **Folder-tab navigation** — the active sidebar page takes on the paper's own color and pulls left, reading as a tab you're currently on top of rather than a highlighted button among buttons.
- **A cover page, not a hero image** — Welcome is a text-only title page (eyebrow, serif title, a two-line description, a dotted table of contents) rather than a stock photo or icon banner.
- **Recommendations as memos** — each rule-based recommendation renders as an interoffice memo card; the single highest-priority one gets a rotated "URGENT" stamp instead of a generic colored alert box.
- **One accent, used sparingly** — ledger green for structure and primary actions, a brick-red accent reserved for genuinely urgent signals (high turnover, the memo stamp) — no purple, no gradients.

## How It Works — Data Flow

```
Raw file (CSV/XLSX, any column names)
        │
        ▼
schema_mapper.py  →  auto-detects columns, maps to canonical field names
        │
        ▼
data_cleaner.py   →  fills what's safely fillable, flags what isn't,
        │              reports outliers and duplicates
        ▼
data_loader.py    →  single source every page reads from — never
        │              reads a raw file directly
        ▼
Analytics pages   →  finance / performance / attendance / recruitment /
                      predictive attrition — all built on canonical
                      field names only
```

Because every page downstream only ever sees canonical field names, swapping the source file is a mapping step, not a rewrite.

## Tech Stack

- **Python** — core language
- **Streamlit** — UI framework and app server
- **Pandas** — data manipulation and the cleaning pipeline
- **Plotly** — all interactive charts, including click-to-filter selection
- **scikit-learn** — Random Forest classifier for attrition prediction
- **Custom CSS** — the Personnel Ledger theme, layered over Streamlit's default components

## Project Structure

```
hr_system/
├── app.py                      # Entry point — theme, sidebar, dynamic page list
├── style.py                    # Personnel Ledger theme + reusable UI components
├── filters.py                  # Shared slicers + chart styling + click-filter helper
├── data_loader.py              # Single source of truth for data access (default or uploaded)
├── data_cleaner.py             # Rule-based cleaning logic
├── schema_mapper.py            # Auto-mapping engine (exact + fuzzy matching)
├── canonical_schema.py         # The 18 standard fields everything else talks to
├── requirements.txt
├── .streamlit/
│   └── config.toml             # Theme colors, upload size limit
└── views/
    ├── welcome.py               # Register cover / title page + table of contents
    ├── home.py                  # KPI pipeline overview
    ├── upload_data.py           # Upload + column-mapping confirmation UI
    ├── data_cleaning.py         # Quality score + before/after + audit log
    ├── finance.py                # Cross-filtered compensation analytics
    ├── performance.py            # Engagement/performance analytics
    ├── attendance.py             # Absence/lateness analytics
    ├── recruitment.py            # Sourcing + turnover + tenure analytics
    ├── recommendations.py        # Rule-based recommendations, shown as memo cards
    └── predictive_attrition.py   # ML-based attrition risk scoring
```

## Getting Started

```bash
git clone https://github.com/Rokaia-Rezk/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501`. The bundled sample dataset (`HRDataset_v14.csv`) loads by default — or go to **Upload Data** in the sidebar to load your own HR export.

## Using Your Own Data

1. Go to the **Upload Data** page.
2. Upload a CSV or Excel file.
3. Review the auto-detected column mapping — every canonical field shows a dropdown pre-filled with the system's best guess. Confirm or correct each one.
4. Click **Apply Mapping & Load Data**. Every other page in the sidebar now reflects your data, and pages that don't apply to your dataset (e.g. no performance data) simply won't appear.

## Possible Next Steps

Ideas for later — none of this exists yet, this is the current project's Streamlit implementation only:

- [ ] **Natural-language data assistant** — a small function-calling agent (not free-form RAG, and not raw LLM-generated code) that lets someone ask a plain-language question about the currently loaded data ("what's the average salary in Sales?") and get an answer computed through a fixed, safe set of query tools built on the canonical schema, rather than an LLM writing and executing arbitrary Pandas code.
- [ ] A full-stack rebuild (separate backend + custom HTML/CSS frontend) for complete design control beyond what's achievable by styling Streamlit's components
- [ ] Persist uploaded datasets across sessions (currently session-only — closing the tab returns you to the sample dataset)
- [ ] Expand the predictive model with additional algorithms for comparison

## Author

**Rokaia Rezk** — Data Scientist & ML

- GitHub: [github.com/Rokaia-Rezk](https://github.com/Rokaia-Rezk)
- LinkedIn: [linkedin.com/in/rokaia-rezk-0761052bb](https://www.linkedin.com/in/rokaia-rezk-0761052bb)
- Portfolio: [portfolio-rokaia-rezk1.vercel.app](https://portfolio-rokaia-rezk1.vercel.app/)
