# System Workflows — Jira Feature Report Tool

## WF-01: Config Loading (cap-001)

```mermaid
flowchart TD
    A[App startup] --> B[load_dotenv]
    B --> C{All required vars present?\nJIRA_URL, JIRA_USER, JIRA_TOKEN\nJIRA_START_DATE_FIELD\nJIRA_DUE_DATE_FIELD}
    C -- No --> D[Raise ConfigError\nwith list of missing vars]
    C -- Yes --> E[Return Config object\nproject_type defaults to nextgen]
```

## WF-02: Recursive Ticket Tree Fetch (cap-002, cap-003)

```mermaid
flowchart TD
    A["fetch_tree(ticket_id)"] --> B["GET /rest/api/3/issue/TICKET_ID"]
    B --> C{HTTP OK?}
    C -- 401/403 --> ERR1[Raise AuthError]
    C -- 404 --> ERR2[Raise TicketNotFoundError]
    C -- 429 --> RETRY[Exponential backoff\nmax 3 retries]
    RETRY --> B
    C -- 200 --> D["Build Ticket, depth=0"]
    D --> E["_fetch_children(root, depth=0)"]

    subgraph fc ["_fetch_children(parent, depth)"]
        FC1{"depth >= 2?"} -- Yes --> FC2[Return — depth cap]
        FC1 -- No --> FC3{"project_type?"}
        FC3 -- nextgen --> FC4["JQL: parent = PARENT_ID"]
        FC3 -- classic --> FC5["JQL: 'Epic Link' = PARENT_ID"]
        FC4 & FC5 --> FC6["GET /rest/api/3/search/jql\nfields=*all\nToken-based pagination"]
        FC6 --> FC7["For each child:\nBuild Ticket, depth+1\nRecurse _fetch_children"]
    end

    E --> F[Return TicketTree]
```

## WF-03: Comment Fetch (cap-008, cap-009)

```mermaid
flowchart TD
    A["fetch_comments(tree)"] --> B[For each ticket in tree.all_tickets]
    B --> C["GET /rest/api/3/issue/ID/comment\nPaginate 50/page"]
    C --> D{"comment.created >= now - 7 days?"}
    D -- No --> E[Skip]
    D -- Yes --> F[Extract plain text from ADF body]
    F --> G[Build Comment object]
    G --> H[Append to tree.comments]
```

## WF-04: Gantt Date Utilities (cap-006, cap-007)

```mermaid
flowchart TD
    A["calc_date_range(tickets)"] --> B[Collect start_date + due_date\nignore None]
    B --> C["min_date, max_date"]
    C --> D["generate_week_columns(min, max)"]
    D --> E["Snap min to Monday\nSnap max to Sunday"]
    E --> F["Generate list of Mondays\nstep = 7 days"]
    F --> G["ticket_in_week(ticket, monday)\nTrue if date range overlaps week"]
```
