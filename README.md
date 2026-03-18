# Jira Feature Report Tool

A local Streamlit application that takes a Jira Feature ticket ID, recursively fetches the full ticket hierarchy (Feature → Epic → Story/Task), and generates a multi-sheet Excel report with Gantt charts and comment summaries.

## Features

- **Recursive ticket fetch** — Feature → Epic → Story/Task (3 levels max)
- **5 Excel worksheets:**
  - **Tickets** — flat list of all tickets with hyperlinks
  - **Simplified Gantt** — open epics only, week-column calendar with coloured date ranges
  - **Full Gantt** — same as Simplified + indented child sub-rows per epic
  - **Updates** — comments on epics and children from the last 7 days
  - **Weekly Updates** — comments on the root Feature ticket from the last 7 days
- **Configurable open statuses** via sidebar multiselect
- **Download + local save** — `st.download_button` + auto-saved to `./output/`
- **Error handling** — auth failures, missing tickets, rate limits (exponential backoff)

## Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/felipe-stanham/JiraGantt-Tool.git
   cd JiraGantt-Tool
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure credentials:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your Jira instance details:
   ```
   JIRA_URL=https://your-org.atlassian.net
   JIRA_USER=your-email@example.com
   JIRA_TOKEN=your-api-token
   JIRA_START_DATE_FIELD=customfield_10039
   JIRA_DUE_DATE_FIELD=duedate
   JIRA_PROJECT_TYPE=nextgen
   ```
   To find your start date custom field ID, query: `GET /rest/api/3/field`

4. **Run the app:**
   ```bash
   python3 -m streamlit run app.py
   ```

## Project Structure

```
├── app.py                  # Streamlit UI (no business logic)
├── .env                    # Credentials (not committed)
├── .env.example            # Template with all required keys
├── requirements.txt        # streamlit, requests, openpyxl, python-dotenv
├── output/                 # Auto-created; generated reports saved here
├── core/
│   ├── config.py           # .env loading and validation
│   ├── models.py           # Dataclasses: Config, Ticket, TicketTree, Comment, etc.
│   ├── jira_client.py      # Jira REST API client with retry and pagination
│   ├── fetcher.py          # Recursive tree fetch and comment fetch
│   ├── excel_builder.py    # Multi-sheet Excel report generation
│   └── gantt.py            # Date range and week-column utilities
├── test_fetch.py           # Standalone Jira connection test
└── test_excel.py           # Standalone Excel generation test
```

## Usage

1. Open `http://localhost:8501` in your browser
2. Configure open statuses in the sidebar (defaults exclude Cancelled, Duplicate, Closed)
3. Enter a Jira Feature ticket ID (e.g. `MTC-1916`)
4. Click **Generate Report**
5. Download the `.xlsx` via the download button or find it in `./output/`
