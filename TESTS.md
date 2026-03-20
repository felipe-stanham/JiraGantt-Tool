# Regression Test Registry

> Critical-path tests only. Declarative — Claude Code reads these and generates verification scripts at runtime.
> Run all before merging to `main` or deploying to prod. Always execute against `dev` environment (`ENV=dev`).

---

## P-0001 / Jira Feature Report Tool

### Config & Auth

**Source:** P-0001 / Scope 1 (cap-001, cap-002)

- **test_config_loads:** Load config with all required `.env` variables set → `Config` object is populated, no error raised.
- **test_config_missing_vars:** Remove a required variable from `.env` → `ConfigError` raised listing the missing variable name.
- **test_jira_auth_success:** Make an authenticated GET request to Jira dev instance (e.g., fetch a known ticket) → HTTP 200, valid JSON returned.
- **test_jira_auth_failure:** Use invalid credentials → `AuthError` raised with a user-readable message, not a raw HTTP error.

### Fetcher — Tree Retrieval

**Source:** P-0001 / Scope 1 (cap-003), P-0002 / Scope 1 (cap-001)

- **test_fetch_tree_full_depth:** Call `fetch_tree` with a known dev Feature ID → Tree contains Feature (depth 0), Epics (depth 1), Stories/Tasks (depth 2), Sub-tasks (depth 3). Max depth is 3.
- **test_fetch_tree_empty_children:** Call `fetch_tree` with a Feature whose Epic has zero children → No error, Epic appears with empty children list.

### Excel Output

**Source:** P-0001 / Scope 2 (cap-005, cap-006, cap-007, cap-010)

- **test_excel_sheets_exist:** Generate a report from a known tree → Workbook contains exactly 5 sheets: Tickets, Simplified Gantt, Full Gantt, Updates, Weekly Updates.
- **test_excel_tickets_sheet:** Open the Tickets sheet → One row per ticket in the tree, all expected columns present, Link column contains hyperlinks.
- **test_excel_file_saved:** After `build_excel` → File exists at `./output/YYYYMMDD_<ticket-id>.xlsx`.

### Gantt — Status Colors & Sorting

**Source:** P-0002 / Scope 1 (cap-002, cap-004)

- **test_gantt_status_colors:** Generate a report with tickets in known statuses → In Simplified Gantt, Status column cells and in-range week cells use the correct palette fill color (not old fixed blue). Unknown statuses use gray `EBEBEB`.
- **test_gantt_sort_order:** Open Full Gantt sheet → Children of each Epic sorted by numeric ticket ID ascending (e.g., MTC-9 before MTC-10).

### UI — Core Flow

**Source:** P-0001 / Scope 3 (cap-004)

- **test_ui_generate_report:** Launch Streamlit app, enter a valid dev Feature ID, click Generate → Download button appears, no error shown.
- **test_ui_error_display:** Enter an invalid ticket ID, click Generate → Inline error message displayed, no stack trace.

---

## P-0002 / Jira Tool Enhancements

### Create Model Epic

**Source:** P-0002 / Scope 2 (cap-005, cap-006)

- **test_create_epic_ui_visible:** Launch Streamlit app → "Create Model Epic" section visible below the report form.
- **test_create_epic_success:** Call `create_model_epic` with a valid dev Feature ID and name "TestEpic" → Epic created as `[MODEL] TestEpic`, Stories and Sub-tasks exist as children in correct hierarchy, returned dict contains `id` and `url`.
- **test_create_epic_button_disabled:** In UI, leave Epic name empty → "Create Model Epic" button is disabled.
