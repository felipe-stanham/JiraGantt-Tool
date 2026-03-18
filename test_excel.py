"""
Standalone test script for Scope 2 — generates an Excel report from a live Jira ticket.

Usage:
    python test_excel.py <TICKET_ID>

Requires a valid .env file with Jira credentials.
"""

import sys
from datetime import date

from core.config import load_config, ConfigError
from core.jira_client import JiraClient, AuthError, TicketNotFoundError, JiraAPIError
from core.fetcher import fetch_tree, fetch_comments
from core.excel_builder import build_excel
from core.models import ReportConfig


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_excel.py <TICKET_ID>")
        print("Example: python test_excel.py MTC-1916")
        sys.exit(1)

    ticket_id = sys.argv[1]

    print("Loading config...")
    try:
        config = load_config()
    except ConfigError as e:
        print(f"CONFIG ERROR: {e}")
        sys.exit(1)

    client = JiraClient(config)

    print(f"Fetching ticket tree for {ticket_id}...")
    try:
        tree = fetch_tree(ticket_id, config, client)
    except (AuthError, TicketNotFoundError, JiraAPIError) as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print(f"  Feature: {tree.root.id} — {tree.root.name}")
    print(f"  Epics: {len(tree.epics())}  Stories: {len(tree.stories())}")

    print("Fetching comments...")
    fetch_comments(tree, config, client)
    print(f"  Comments: {len(tree.comments)}")

    report_config = ReportConfig(
        open_statuses=config.open_statuses,
        report_date=date.today(),
    )

    print("Building Excel report...")
    xlsx_bytes = build_excel(tree, report_config)
    filename = f"{report_config.report_date.strftime('%Y%m%d')}_{tree.root.id}.xlsx"
    print(f"  Size: {len(xlsx_bytes)} bytes")
    print(f"  Saved to: output/{filename}")
    print("Done.")


if __name__ == "__main__":
    main()
