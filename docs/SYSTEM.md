# System: Jira Feature Report Tool

## What This System Does
A local Streamlit application that accepts a Jira Feature ticket ID, recursively fetches the full ticket hierarchy (Feature → Epic → Story/Task → Sub-task) via Jira Cloud REST API v3, generates a multi-worksheet Excel report with status-colored Gantt charts and comment summaries, and can create a model Epic hierarchy in Jira from a fixed template. Deployed locally only — no cloud, no Docker.

## Architecture Principles
- API-first: all Jira interaction via REST API v3 with Basic Auth (email + API token)
- Credentials in `.env` only — never in UI or code
- `app.py` is UI-only — all business logic lives in `core/`
- No persistent database — all state is in-memory during a single report generation run
- Depth capped at 4 levels (Feature → Epic → Story/Task → Sub-task) — no infinite recursion

## Cross-Project Constraints
- Python with Streamlit, requests, openpyxl, python-dotenv
- Output: `.xlsx` downloaded via Streamlit + saved to `./output/`
- Custom field IDs configured via `.env` (no auto-discovery UI)
- Supports both classic and next-gen Jira project types via `JIRA_PROJECT_TYPE` env var

## Projects
| ID      | Name                    | Status      | Summary                                              |
|---------|-------------------------|-------------|------------------------------------------------------|
| P-0001  | Jira Feature Report Tool | [DONE]     | Recursive Jira fetch + multi-sheet Excel report tool |
| P-0002  | Jira Tool Enhancements   | [DONE]     | Depth-4 fetch, status-color Gantt, Create Model Epic |
