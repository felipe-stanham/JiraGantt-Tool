from datetime import datetime, timedelta
from core.models import Config, Ticket, TicketTree, Comment
from core.jira_client import JiraClient


def _parse_date(value) -> None:
    if not value:
        return None
    if isinstance(value, str):
        return datetime.strptime(value[:10], "%Y-%m-%d").date()
    return None


def _extract_text_from_adf(node) -> str:
    if isinstance(node, str):
        return node
    if not isinstance(node, dict):
        return ""
    text = node.get("text", "")
    for child in node.get("content", []):
        text += _extract_text_from_adf(child)
    return text


def _build_ticket(raw: dict, config: Config, depth: int, parent_id: str = None, parent_name: str = None) -> Ticket:
    fields = raw.get("fields", {})
    key = raw.get("key", "")

    assignee = fields.get("assignee")
    assignee_name = assignee.get("displayName") if assignee else None

    return Ticket(
        id=key,
        url=f"{config.jira_url}/browse/{key}",
        name=fields.get("summary", ""),
        status=fields.get("status", {}).get("name", ""),
        start_date=_parse_date(fields.get(config.start_date_field_id)),
        due_date=_parse_date(fields.get(config.due_date_field_id)),
        issue_type=fields.get("issuetype", {}).get("name", ""),
        parent_id=parent_id,
        parent_name=parent_name,
        assignee=assignee_name,
        depth=depth,
    )


def _fetch_children(parent: Ticket, config: Config, client: JiraClient, depth: int) -> None:
    if depth >= 3:
        return

    raw_children = client.get_children(parent.id, config.project_type)
    for raw in raw_children:
        child = _build_ticket(raw, config, depth + 1, parent.id, parent.name)
        parent.children.append(child)
        _fetch_children(child, config, client, depth + 1)


def fetch_tree(ticket_id: str, config: Config, client: JiraClient) -> TicketTree:
    raw = client.get_issue(ticket_id)
    root = _build_ticket(raw, config, depth=0)
    _fetch_children(root, config, client, depth=0)
    return TicketTree(root=root)


def fetch_comments(tree: TicketTree, config: Config, client: JiraClient) -> None:
    cutoff = datetime.now() - timedelta(days=7)
    all_tickets = tree.all_tickets()

    for ticket in all_tickets:
        raw_comments = client.get_comments(ticket.id)
        for raw in raw_comments:
            created_str = raw.get("created", "")
            if not created_str:
                continue
            created = datetime.strptime(created_str[:19], "%Y-%m-%dT%H:%M:%S")

            if created < cutoff:
                continue

            body_adf = raw.get("body", {})
            body_text = _extract_text_from_adf(body_adf).strip()

            comment = Comment(
                ticket_id=ticket.id,
                ticket_name=ticket.name,
                author=raw.get("author", {}).get("displayName", "Unknown"),
                created=created,
                body=body_text,
            )
            tree.comments.append(comment)
