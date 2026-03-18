# data_model.md — Jira Feature Report Tool

The data model represents in-memory Python objects built from the Jira API response.
No persistent database is used; all state lives in memory during a single report generation run.

```mermaid
classDiagram

    class Config {
        +str jira_url
        +str jira_user
        +str jira_token
        +str start_date_field_id
        +str due_date_field_id
        +str project_type  % "classic" | "nextgen"
        +List~str~ open_statuses
        +from_env() Config
    }

    class Ticket {
        +str id
        +str url
        +str name
        +str status
        +date|None start_date
        +date|None due_date
        +str issue_type
        +str|None parent_id
        +str|None parent_name
        +str|None assignee
        +int depth  % 0=Feature, 1=Epic, 2=Story/Task
        +List~Ticket~ children
    }

    class Comment {
        +str ticket_id
        +str ticket_name
        +str author
        +datetime created
        +str body
    }

    class TicketTree {
        +Ticket root
        +List~Ticket~ all_tickets()
        +List~Ticket~ epics()
        +List~Ticket~ stories()
        +List~Comment~ comments
        +filter_open_epics(open_statuses) List~Ticket~
        +date_range() Tuple~date, date~
    }

    class ReportConfig {
        +List~str~ open_statuses
        +date report_date
        +int lookback_days  % default 7
    }

    class ExcelReport {
        +bytes xlsx_bytes
        +str filename
        +build(tree, config) ExcelReport
    }

    TicketTree "1" --> "1" Ticket : root
    Ticket "1" --> "0..*" Ticket : children
    TicketTree "1" --> "0..*" Comment : comments
    Comment "many" --> "1" Ticket : belongs to
    ExcelReport ..> TicketTree : consumes
    ExcelReport ..> ReportConfig : consumes
    Config ..> ReportConfig : seeds
```

## Notes

- `Ticket.depth` drives sheet logic: depth=0 is the Feature, depth=1 are Epics, depth=2 are Stories/Tasks.
- `TicketTree.all_tickets()` returns a flat list in DFS order (Feature first, then each Epic and its children before the next Epic).
- `TicketTree.filter_open_epics()` is used by both Gantt sheets.
- `Comment.body` is stored as plain text (Jira ADF/markdown stripped); no rich text rendering in Excel.
- `start_date` and `due_date` are Python `datetime.date` objects (time component discarded).
- `Ticket.url` is constructed as `{jira_url}/browse/{id}` — not fetched from API.
