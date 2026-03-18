# Data Model — Jira Feature Report Tool

No persistent database. All state is in-memory during a single report generation run.

```mermaid
classDiagram

    class Config {
        +str jira_url
        +str jira_user
        +str jira_token
        +str start_date_field_id
        +str due_date_field_id
        +str project_type
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
        +int depth
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
        +List~Comment~ comments
        +all_tickets() List~Ticket~
        +epics() List~Ticket~
        +stories() List~Ticket~
        +filter_open_epics(statuses) List~Ticket~
        +date_range() Tuple~date, date~
    }

    class ReportConfig {
        +List~str~ open_statuses
        +date report_date
        +int lookback_days
    }

    class ExcelReport {
        +bytes xlsx_bytes
        +str filename
    }

    TicketTree "1" --> "1" Ticket : root
    Ticket "1" --> "0..*" Ticket : children
    TicketTree "1" --> "0..*" Comment : comments
    Comment "many" --> "1" Ticket : belongs to
    ExcelReport ..> TicketTree : consumes
    ExcelReport ..> ReportConfig : consumes
    Config ..> ReportConfig : seeds
```

## Field Mapping

| Model Field | Jira Source |
|---|---|
| `Ticket.id` | `issue.key` |
| `Ticket.url` | `{jira_url}/browse/{key}` (constructed) |
| `Ticket.name` | `fields.summary` |
| `Ticket.status` | `fields.status.name` |
| `Ticket.start_date` | `fields.customfield_10039` |
| `Ticket.due_date` | `fields.duedate` |
| `Ticket.issue_type` | `fields.issuetype.name` |
| `Ticket.assignee` | `fields.assignee.displayName` (null-safe) |
| `Ticket.parent_id` | Passed from parent during recursion |
| `Ticket.parent_name` | Passed from parent during recursion |
| `Comment.author` | `comment.author.displayName` |
| `Comment.created` | `comment.created` (ISO 8601, truncated to seconds) |
| `Comment.body` | `comment.body` (ADF → plain text extraction) |
