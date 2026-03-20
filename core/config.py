import os
from dotenv import load_dotenv
from core.models import Config


class ConfigError(Exception):
    pass


REQUIRED_VARS = [
    "JIRA_URL",
    "JIRA_USER",
    "JIRA_TOKEN",
    "JIRA_START_DATE_FIELD",
    "JIRA_DUE_DATE_FIELD",
]


def load_config() -> Config:
    load_dotenv()

    missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
    if missing:
        raise ConfigError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    return Config(
        jira_url=os.getenv("JIRA_URL").rstrip("/"),
        jira_user=os.getenv("JIRA_USER"),
        jira_token=os.getenv("JIRA_TOKEN"),
        start_date_field_id=os.getenv("JIRA_START_DATE_FIELD"),
        due_date_field_id=os.getenv("JIRA_DUE_DATE_FIELD"),
        project_type=os.getenv("JIRA_PROJECT_TYPE", "nextgen"),
        project_key=os.getenv("JIRA_PROJECT_KEY") or None,
        issue_type_epic=os.getenv("JIRA_ISSUE_TYPE_EPIC", "Epic"),
        issue_type_story=os.getenv("JIRA_ISSUE_TYPE_STORY", "Story"),
        issue_type_subtask=os.getenv("JIRA_ISSUE_TYPE_SUBTASK", "Sub-Task"),
    )
