# architecture.md — Jira Feature Report Tool

---

## Component Architecture

```mermaid
flowchart TD
    subgraph app ["app.py — Streamlit Entry Point"]
        UI[UI Layer\nst.text_input, st.multiselect\nst.button, st.download_button\nst.progress, st.error]
    end

    subgraph core ["core/ — Business Logic"]
        CFG[config.py\nConfig.from_env]
        CLIENT[jira_client.py\nJiraClient\nget_issue, get_children\nget_comments]
        FETCHER[fetcher.py\nfetch_tree, fetch_comments]
        BUILDER[excel_builder.py\nbuild_excel\none function per sheet]
        GANTT[gantt.py\ngenerate_week_columns\ncalc_date_range\napply_gantt_fill]
        MODELS[models.py\nConfig, Ticket\nTicketTree, Comment\nReportConfig, ExcelReport]
    end

    subgraph output ["output folder"]
        FILE[YYYYMMDD_ticketid.xlsx]
    end

    subgraph ext ["External"]
        JIRA[Jira Cloud\nREST API v3]
        ENV[dot-env file]
    end

    ENV --> CFG
    UI --> FETCHER
    UI --> BUILDER
    CFG --> CLIENT
    CFG --> FETCHER
    FETCHER --> CLIENT
    CLIENT --> JIRA
    FETCHER --> MODELS
    BUILDER --> MODELS
    BUILDER --> GANTT
    BUILDER --> FILE
    BUILDER --> UI
```

---

## Module Responsibilities

| Module | Responsibility |
|---|---|
| `app.py` | Streamlit UI only. No business logic. Calls `fetch_tree`, `fetch_comments`, `build_excel`. |
| `core/config.py` | Loads and validates `.env`. Raises `ConfigError` if required vars missing. |
| `core/jira_client.py` | All HTTP calls to Jira. Auth, pagination, retry on 429. No domain logic. |
| `core/fetcher.py` | Orchestrates recursive tree fetch and comment fetch. Returns `TicketTree`. |
| `core/excel_builder.py` | Builds the openpyxl `Workbook`. One private function per sheet. |
| `core/gantt.py` | Pure date/calendar utilities. No Jira or openpyxl dependency. |
| `core/models.py` | Dataclasses only. No logic except simple helper methods on `TicketTree`. |

---

## Deployment Topology

```mermaid
flowchart LR
    subgraph machine ["User's Local Machine"]
        ENV2["dot-env file\ncredentials"]
        APP["streamlit run app.py\nlocalhost:8501"]
        OUT2["output folder\nsaved reports"]
    end
    subgraph internet ["Internet"]
        JIRA2["Jira Cloud\nyour-org.atlassian.net"]
    end
    APP -- "HTTPS REST API v3\nBasic Auth" --> JIRA2
    ENV2 -- "read on startup" --> APP
    APP -- "write xlsx" --> OUT2
    BROWSER["Browser\nlocalhost:8501"] -- "HTTP" --> APP
```

---

## Data Flow

```mermaid
flowchart LR
    A["dot-env file"] -->|Config| B["JiraClient"]
    B -->|Raw JSON| C["Fetcher"]
    C -->|TicketTree + Comments| D["ExcelBuilder"]
    D -->|openpyxl Workbook| E["BytesIO buffer"]
    E -->|bytes| F["st.download_button"]
    E -->|write| G["output folder"]
```

---

## File and Directory Structure

```
jira-report/
├── app.py                  # Streamlit entry point
├── .env                    # Credentials (not committed)
├── .env.example            # Template with all required keys
├── requirements.txt        # streamlit, requests, openpyxl, python-dotenv
├── output/                 # Auto-created; generated reports land here
└── core/
    ├── __init__.py
    ├── config.py
    ├── models.py
    ├── jira_client.py
    ├── fetcher.py
    ├── excel_builder.py
    └── gantt.py
```

---

## External Dependencies

| Library | Purpose |
|---|---|
| `streamlit` | UI framework |
| `requests` | Jira REST API HTTP calls |
| `openpyxl` | Excel file generation |
| `python-dotenv` | `.env` loading |

No other external dependencies. Standard library `datetime`, `dataclasses`, `io`, `os`, `pathlib` used freely.
