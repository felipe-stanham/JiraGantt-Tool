from pathlib import Path

from core.models import Config
from core.jira_client import JiraClient, JiraAPIError


class CreatorError(Exception):
    pass


_TEMPLATE_PATH = Path(__file__).parent.parent / "docs/Projects/P-0002/EpicTemplate.md"


def _create_issue(summary: str, issue_type: str, parent_key: str, config: Config, client: JiraClient) -> str:
    if parent_key:
        project_key = parent_key.split("-")[0]
    elif config.project_key:
        project_key = config.project_key
    else:
        raise CreatorError(
            "No Feature ID provided and JIRA_PROJECT_KEY is not set in .env. "
            "Cannot determine the target project."
        )

    if issue_type == "Epic":
        fields: dict = {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": config.issue_type_epic},
        }
        if parent_key:
            if config.project_type == "nextgen":
                fields["parent"] = {"key": parent_key}
            else:
                fields["customfield_10014"] = parent_key
        payload = {"fields": fields}
    else:
        issue_type_name = (
            config.issue_type_story if issue_type == "Story"
            else config.issue_type_subtask
        )
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "issuetype": {"name": issue_type_name},
                "parent": {"key": parent_key},
            }
        }

    try:
        result = client.create_issue(payload)
    except JiraAPIError as e:
        raise CreatorError(str(e)) from e

    return result["key"]


def create_model_epic(feature_id: str, epic_name: str, config: Config, client: JiraClient) -> dict:
    try:
        template_lines = _TEMPLATE_PATH.read_text().splitlines()
    except OSError as e:
        raise CreatorError(f"Cannot read EpicTemplate.md: {e}") from e

    # Parse template lines into (depth, name) tuples, skipping depth-0 (the epic line itself)
    parsed = []
    for line in template_lines:
        if not line.strip():
            continue
        stripped = line.lstrip(" ")
        leading_spaces = len(line) - len(stripped)
        depth = leading_spaces // 4
        name = stripped.replace("EpicName", epic_name)
        parsed.append((depth, name))

    # Create Epic (depth 0 line defines the template name, but Epic is named [MODEL] {epic_name})
    epic_summary = f"[MODEL] {epic_name}"
    try:
        epic_key = _create_issue(epic_summary, "Epic", feature_id, config, client)
    except CreatorError:
        raise

    current_story_key = None

    for depth, name in parsed:
        if depth == 0:
            # Skip — this is the template epic placeholder line
            continue
        elif depth == 1:
            # Story
            story_key = _create_issue(name, "Story", epic_key, config, client)
            current_story_key = story_key
        elif depth == 2:
            # Sub-task
            if current_story_key is None:
                raise CreatorError("Sub-task found before any Story in template")
            _create_issue(name, "Sub-Task", current_story_key, config, client)

    return {
        "id": epic_key,
        "url": f"{config.jira_url}/browse/{epic_key}",
    }
