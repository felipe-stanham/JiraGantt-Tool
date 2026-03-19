# Regression Test Registry

---

## P-0001 / Jira Feature Report Tool

*(Acceptance criteria from P-0001 scopes — see docs/Projects/P-0001.md for details)*

---

## P-0002 / Jira Tool Enhancements

### Scope 1: Fetcher & Report Enhancements

**Source:** P-0002 / Scope 1

- **cap-001:** Fetcher retrieves tickets at depth 0 (Feature), 1 (Epic), 2 (Story/Task), and 3 (Sub-task). Sub-tasks appear in the Tickets sheet. Comments are fetched for Sub-tasks alongside all other tickets. Depth is capped at 4 levels; no infinite recursion. Features/Epics/Stories with zero children at any level are handled without error.
- **cap-002:** Each distinct status value maps to a unique fill color per the defined palette. Gantt week cells that are filled use the status color of that ticket row, not a single fixed blue. The Status column cell in both Gantt sheets is filled with the same status color. Tickets with an unrecognised status fall back to a neutral gray (`EBEBEB`).
- **cap-003:** In the Full Gantt, a thick bottom border (medium weight) is applied to the last row of each Epic group. A thin bottom border is applied to each child row (Stories/Tasks and Sub-tasks). No blank rows are inserted; separators are purely border-based.
- **cap-004:** In the Full Gantt, the children of each Epic are listed in ascending ticket ID order. Sub-tasks within each Story/Task are listed in ascending ticket ID order. Ticket ID sort is numeric-aware (MTC-9 before MTC-10).

### Scope 2: Create Model Epic

**Source:** P-0002 / Scope 2

- **cap-005:** A "Create Model Epic" section is visible below the report form in the main area, always rendered regardless of report state. The user enters a Feature ID (text input) and an Epic name (text input). A "Create Model Epic" button is disabled when either field is empty. On success: a green success message shows the created Epic's Jira ticket ID and URL. On failure: an inline error message is shown; no stack trace.
- **cap-006:** The creator reads `docs/Projects/P-0002/EpicTemplate.md` at runtime. Each `EpicName` token is replaced with the user-provided name. The resulting hierarchy: Epic at depth 0, Stories at depth 1, Sub-tasks at depth 2. Tickets are created in order: Epic first, then each Story followed immediately by its Sub-tasks. The Epic is linked to the Feature ID as its parent. Each Story is linked to the Epic. Each Sub-task is linked to its Story. No assignee, due date, start date, or description is set on any created ticket. The Epic is named `[MODEL] {user_provided_name}`. Stories and Sub-tasks are named exactly as the substituted template line.
