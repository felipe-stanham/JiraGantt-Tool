# System Architecture — Jira Feature Report Tool

## High-Level Component Architecture

```mermaid
flowchart TD
    subgraph app ["app.py — Streamlit Entry Point (Scope 3)"]
        UI[UI Layer — not yet implemented]
    end

    subgraph core ["core/ — Business Logic"]
        CFG[config.py\nConfig.from_env\nConfigError]
        CLIENT[jira_client.py\nJiraClient\nget_issue, get_children\nget_comments]
        FETCHER[fetcher.py\nfetch_tree, fetch_comments]
        BUILDER[excel_builder.py\nbuild_excel — Scope 2]
        GANTT[gantt.py\ncalc_date_range\ngenerate_week_columns\nticket_in_week]
        MODELS[models.py\nConfig, Ticket, TicketTree\nComment, ReportConfig\nExcelReport]
    end

    subgraph output ["output folder"]
        FILE[YYYYMMDD_ticketid.xlsx\n— Scope 2]
    end

    subgraph ext ["External"]
        JIRA[Jira Cloud\nREST API v3\n/rest/api/3/search/jql\n/rest/api/3/issue]
        ENV[.env file]
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

## Deployment Topology

```mermaid
flowchart LR
    subgraph machine ["User's Local Machine"]
        ENV2[".env file\ncredentials"]
        APP["streamlit run app.py\nlocalhost:8501"]
        OUT2["output/\nsaved reports"]
    end
    subgraph internet ["Internet"]
        JIRA2["Jira Cloud\nnclholdings.atlassian.net"]
    end
    APP -- "HTTPS REST API v3\nBasic Auth" --> JIRA2
    ENV2 -- "read on startup" --> APP
    APP -- "write xlsx" --> OUT2
    BROWSER["Browser\nlocalhost:8501"] -- "HTTP" --> APP
```

## Data Flow

```mermaid
flowchart LR
    A[".env file"] -->|Config| B["JiraClient"]
    B -->|Raw JSON| C["Fetcher"]
    C -->|TicketTree + Comments| D["ExcelBuilder — Scope 2"]
    D -->|openpyxl Workbook| E["BytesIO buffer"]
    E -->|bytes| F["st.download_button — Scope 3"]
    E -->|write| G["output/"]
```

## Jira API Notes

- **Search endpoint:** `/rest/api/3/search/jql` (the older `/rest/api/3/search` was deprecated and returns HTTP 410)
- **Pagination:** Token-based via `nextPageToken` / `isLast` (not `startAt` / `total`)
- **Fields:** Must request `fields=*all` to get full issue data from search results
- **Child fetch strategy (nextgen):** `parent = <TICKET_ID>` JQL
- **Child fetch strategy (classic):** `"Epic Link" = <TICKET_ID>` JQL
- **Comments:** `/rest/api/3/issue/<ID>/comment` with `startAt`/`maxResults` pagination (still uses offset-based)
- **Rate limiting:** Exponential backoff on HTTP 429 (delays: 1s, 2s, 4s, max 3 retries)
