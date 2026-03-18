# workflows.md — Jira Feature Report Tool

---

## WF-01: Application Startup and Config Validation (cap-001, cap-002)

```mermaid
flowchart TD
    A[streamlit run app.py] --> B[Load .env via python-dotenv]
    B --> C{All required vars present?\nJIRA_URL, JIRA_USER, JIRA_TOKEN\nJIRA_START_DATE_FIELD\nJIRA_DUE_DATE_FIELD}
    C -- No --> D[st.error: list missing variables\nHalt — do not render main UI]
    C -- Yes --> E[Instantiate JiraClient\nwith base_url + BasicAuth]
    E --> F[Render Streamlit UI\nTicket ID input\nOpen statuses sidebar\nGenerate button]
```

---

## WF-02: Recursive Ticket Tree Fetch (cap-002, cap-003)

```mermaid
flowchart TD
    A[fetch_tree: ticket_id] --> B[GET /rest/api/3/issue/TICKET_ID\nFields: summary, status, issuetype\nparent, assignee, start_date_field, duedate]
    B --> C{HTTP OK?}
    C -- 401/403 --> ERR1[Raise AuthError]
    C -- 404 --> ERR2[Raise TicketNotFoundError]
    C -- 429 --> RETRY[Exponential back-off\nmax 3 retries]
    RETRY --> B
    C -- 200 --> D[Build Ticket object, depth=0]
    D --> E[fetch_children: ticket_id, depth=0]

    subgraph fetch_children [fetch_children: parent_id, parent_depth]
        FC1{parent_depth >= 2?} -- Yes --> FC2[Return empty list\ndepth cap reached]
        FC1 -- No --> FC3{project_type?}
        FC3 -- nextgen --> FC4[JQL: parent = parent_id]
        FC3 -- classic --> FC5["JQL: 'Epic Link' = parent_id\nor issueFunction in subtasksOf"]
        FC4 & FC5 --> FC6[Paginate results\nmax_results=100, startAt=0]
        FC6 --> FC7[For each child: build Ticket\ndepth=parent_depth+1\nrecurse fetch_children]
    end

    E --> F[Attach children to root Ticket]
    F --> G[Return TicketTree]
```

---

## WF-03: Comment Fetch and Routing (cap-008, cap-009)

```mermaid
flowchart TD
    A[fetch_comments: TicketTree] --> B[Collect ticket IDs\nEpics + Stories/Tasks\nexclude Feature root]
    B --> C[Also collect root Feature ID\nfor Weekly Updates]

    C --> D[For each ticket ID in scope]
    D --> E[GET /rest/api/3/issue/TICKET_ID/comment\norderBy=-created\npaginate if total > 50]
    E --> F[For each comment:\nparse created datetime]
    F --> G{created >= today - 7 days?}
    G -- No --> H[Skip]
    G -- Yes --> I[Build Comment object]
    I --> J{Is source ticket the Feature root?}
    J -- Yes --> K[Tag: weekly_updates only]
    J -- No --> L[Tag: updates only]
    K & L --> M[Add to TicketTree.comments]
```

---

## WF-04: Excel Report Construction (cap-005, cap-006, cap-007, cap-008, cap-009, cap-010)

```mermaid
flowchart TD
    A[build_excel: TicketTree + ReportConfig] --> B[Create openpyxl Workbook]

    B --> S1[Sheet: Tickets\nFlat DFS list of all tickets\nColumns: ID Link Name Status\nStart Due IssueType\nParentID ParentName Assignee\nTable formatting + auto-width]

    B --> S2[Sheet: Simplified Gantt\nFilter: open epics only\nSort: due_date asc, nulls last\nCalc date range then week columns\nFill cells in ticket range\nApply row formatting]

    B --> S3[Sheet: Full Gantt\nSame epic rows as Simplified Gantt\nAfter each epic row:\ninsert child sub-rows\nID Name Assignee Status\nNo date fill for sub-rows\nIndent sub-row ID column]

    B --> S4[Sheet: Updates\nFilter comments tagged updates\nSort: created desc\nColumns: TicketID TicketName\nAuthor Date CommentText]

    B --> S5[Sheet: Weekly Updates\nFilter comments tagged weekly_updates\nSort: created desc\nColumns: Author Date CommentText]

    S1 & S2 & S3 & S4 & S5 --> OUT[Save workbook to BytesIO]
    OUT --> WRITE[Write output/YYYYMMDD_ticketid.xlsx]
    OUT --> DL[Return bytes to Streamlit\nst.download_button]
```

---

## WF-05: Gantt Week-Column Generation (cap-006, cap-007)

```mermaid
flowchart TD
    A[Collect start_date and due_date\nfrom all filtered epic rows] --> B[Ignore None values]
    B --> C[min_date = min of all start dates\nmax_date = max of all due dates]
    C --> D{Any dates found?}
    D -- No --> E[Show warning: no dated tickets\nSkip Gantt sheets]
    D -- Yes --> F[Snap min_date to Monday of its week]
    F --> G[Snap max_date to Sunday of its week]
    G --> H[Generate list of Mondays:\nweek_starts = range from min_monday\nto max_sunday step 7 days]
    H --> I[For each Epic row and each week_start:\nIf start_date <= week_start+6\nAND due_date >= week_start\nthen fill cell with highlight colour\nElse leave blank]
```
