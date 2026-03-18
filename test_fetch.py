"""
Standalone test script for Scope 1 — validates Jira connection and fetch logic.

Usage:
    python test_fetch.py <TICKET_ID>

Requires a valid .env file with Jira credentials.
"""

import sys
from core.config import load_config, ConfigError
from core.jira_client import JiraClient, AuthError, TicketNotFoundError, JiraAPIError
from core.fetcher import fetch_tree, fetch_comments


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_fetch.py <TICKET_ID>")
        print("Example: python test_fetch.py MTC-1234")
        sys.exit(1)

    ticket_id = sys.argv[1]

    # 1. Load config
    print("Loading config from .env...")
    try:
        config = load_config()
    except ConfigError as e:
        print(f"CONFIG ERROR: {e}")
        sys.exit(1)

    print(f"  Jira URL: {config.jira_url}")
    print(f"  User: {config.jira_user}")
    print(f"  Project type: {config.project_type}")
    print(f"  Start date field: {config.start_date_field_id}")
    print(f"  Due date field: {config.due_date_field_id}")
    print()

    # 2. Fetch ticket tree
    client = JiraClient(config)
    print(f"Fetching ticket tree for {ticket_id}...")
    try:
        tree = fetch_tree(ticket_id, config, client)
    except AuthError as e:
        print(f"AUTH ERROR: {e}")
        sys.exit(1)
    except TicketNotFoundError as e:
        print(f"NOT FOUND: {e}")
        sys.exit(1)
    except JiraAPIError as e:
        print(f"API ERROR: {e}")
        sys.exit(1)

    # 3. Print summary
    all_tickets = tree.all_tickets()
    epics = tree.epics()
    stories = tree.stories()

    print(f"\nFeature: {tree.root.id} — {tree.root.name}")
    print(f"  Status: {tree.root.status}")
    print(f"  Type: {tree.root.issue_type}")
    print(f"  Assignee: {tree.root.assignee or '(none)'}")
    print(f"  Start: {tree.root.start_date or '(none)'}")
    print(f"  Due: {tree.root.due_date or '(none)'}")
    print()
    print(f"Total tickets: {len(all_tickets)}")
    print(f"  Epics: {len(epics)}")
    print(f"  Stories/Tasks: {len(stories)}")
    print()

    for epic in epics:
        children = epic.children
        print(f"  Epic: {epic.id} — {epic.name} [{epic.status}]")
        print(f"    Assignee: {epic.assignee or '(none)'}")
        print(f"    Start: {epic.start_date or '(none)'}  Due: {epic.due_date or '(none)'}")
        print(f"    Children: {len(children)}")
        for child in children:
            print(f"      {child.id} — {child.name} [{child.status}] (Assignee: {child.assignee or '(none)'})")
        print()

    # 4. Fetch comments
    print("Fetching comments (last 7 days)...")
    fetch_comments(tree, config, client)
    print(f"  Total comments: {len(tree.comments)}")

    feature_comments = [c for c in tree.comments if c.ticket_id == tree.root.id]
    other_comments = [c for c in tree.comments if c.ticket_id != tree.root.id]
    print(f"  Feature comments (Weekly Updates): {len(feature_comments)}")
    print(f"  Epic/Story comments (Updates): {len(other_comments)}")

    for c in tree.comments[:10]:
        print(f"    [{c.ticket_id}] {c.author} @ {c.created}: {c.body[:80]}...")
    if len(tree.comments) > 10:
        print(f"    ... and {len(tree.comments) - 10} more")

    # 5. Date range
    min_d, max_d = tree.date_range()
    print(f"\nDate range: {min_d} → {max_d}")

    print("\nDone.")


if __name__ == "__main__":
    main()
