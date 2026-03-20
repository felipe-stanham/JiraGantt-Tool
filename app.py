import streamlit as st
from datetime import date

from core.config import load_config, ConfigError
from core.jira_client import JiraClient, AuthError, TicketNotFoundError, JiraAPIError
from core.fetcher import fetch_tree, fetch_comments
from core.excel_builder import build_excel
from core.models import ReportConfig
from core.creator import create_model_epic, CreatorError

st.set_page_config(page_title="Jira Feature Report", page_icon="\U0001f5c2")
st.title("\U0001f5c2 Jira Feature Report")

# --- Config validation on startup ---
try:
    config = load_config()
except ConfigError as e:
    st.error(f"**Configuration Error**\n\n{e}")
    st.stop()

client = JiraClient(config)

# --- Sidebar ---
with st.sidebar:
    st.header("Open Statuses")
    ALL_STATUSES = [
        "Backlog", "Blocked", "On Hold", "Pending Manager Approval",
        "In Progress", "In Review", "Waiting for Response",
        "Cancelled", "Duplicate", "Closed",
    ]
    DONE_STATUSES = {"Cancelled", "Duplicate", "Closed"}
    default_open = [s for s in ALL_STATUSES if s not in DONE_STATUSES]

    open_statuses = st.multiselect(
        "Select statuses considered 'open' for Gantt filtering:",
        options=ALL_STATUSES,
        default=default_open,
    )

# --- Main area ---
st.markdown("Enter a Jira Feature ticket ID to generate the Excel report.")

ticket_id = st.text_input("Ticket ID", placeholder="MTC-1234")

if st.button("Generate Report", disabled=not ticket_id):
    report_config = ReportConfig(
        open_statuses=open_statuses,
        report_date=date.today(),
    )

    try:
        with st.spinner("Fetching ticket tree..."):
            tree = fetch_tree(ticket_id.strip(), config, client)

        with st.spinner("Fetching comments..."):
            fetch_comments(tree, config, client)

        with st.spinner("Building Excel report..."):
            xlsx_bytes = build_excel(tree, report_config)

        filename = f"{report_config.report_date.strftime('%Y%m%d')}_{tree.root.id}.xlsx"

        st.success("Report generated successfully")

        st.markdown("### Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Epics", len(tree.epics()))
        col2.metric("Stories/Tasks", len(tree.stories()))
        col3.metric("Comments (7d)", len(tree.comments))

        st.markdown(f"**Feature:** {tree.root.id} \u2014 {tree.root.name}")
        st.markdown(f"**File saved:** `output/{filename}`")

        st.download_button(
            label="\u2b07 Download Report",
            data=xlsx_bytes,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except AuthError:
        st.error("**Authentication failed.** Check your `JIRA_USER` and `JIRA_TOKEN` in `.env`.")
    except TicketNotFoundError:
        st.error(f"**Ticket `{ticket_id}` not found.** Check the ticket ID and try again.")
    except JiraAPIError as e:
        st.error(f"**Jira API error:** {e}")
    except Exception as e:
        st.error(f"**Unexpected error:** {e}")

if not ticket_id:
    st.info("Configure open statuses in the sidebar before generating.")

# --- Create Model Epic ---
st.markdown("---")
st.subheader("Create Model Epic")

epic_name = st.text_input("Epic Name", key="epic_name_input")

if "creator_pending_confirm" not in st.session_state:
    st.session_state.creator_pending_confirm = False

def _run_creation(feature_id: str, name: str):
    try:
        with st.spinner("Creating model epic in Jira..."):
            result = create_model_epic(feature_id, name, config, client)
        epic_id = result["id"]
        epic_url = result["url"]
        st.success(f"Epic created: [{epic_id}]({epic_url})")
    except CreatorError as e:
        st.error(f"Jira API error: {e}")
    except AuthError:
        st.error("**Authentication failed.** Check your `JIRA_USER` and `JIRA_TOKEN` in `.env`.")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

if st.button("Create Model Epic", disabled=not epic_name):
    if not ticket_id:
        st.session_state.creator_pending_confirm = True
    else:
        _run_creation(ticket_id.strip(), epic_name.strip())

if st.session_state.creator_pending_confirm:
    st.warning(
        "**No Feature ID provided.** The Epic will be created at the root of the "
        "project/space, not linked to any Feature ticket. Do you want to continue?"
    )
    col1, col2, _ = st.columns([1, 1, 6])
    if col1.button("Continue", key="creator_confirm_yes"):
        st.session_state.creator_pending_confirm = False
        _run_creation("", epic_name.strip())
    if col2.button("Cancel", key="creator_confirm_no"):
        st.session_state.creator_pending_confirm = False
