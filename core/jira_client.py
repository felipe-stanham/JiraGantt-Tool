import time
import requests
from core.models import Config


class AuthError(Exception):
    pass


class TicketNotFoundError(Exception):
    pass


class JiraAPIError(Exception):
    pass


class JiraClient:
    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 2, 4]

    def __init__(self, config: Config):
        self.base_url = config.jira_url
        self.auth = (config.jira_user, config.jira_token)

    def _request(self, method: str, url: str, **kwargs) -> dict:
        for attempt in range(self.MAX_RETRIES + 1):
            response = requests.request(
                method, url, auth=self.auth, **kwargs
            )

            if response.status_code == 429:
                if attempt < self.MAX_RETRIES:
                    time.sleep(self.RETRY_DELAYS[attempt])
                    continue
                raise JiraAPIError(
                    f"Rate limited (HTTP 429) after {self.MAX_RETRIES} retries"
                )

            if response.status_code in (401, 403):
                raise AuthError(
                    "Authentication failed. Check your JIRA_USER and JIRA_TOKEN."
                )

            if response.status_code == 404:
                raise TicketNotFoundError(
                    f"Ticket not found (HTTP 404): {url}"
                )

            if not response.ok:
                raise JiraAPIError(
                    f"Jira API error (HTTP {response.status_code}): {response.text[:500]}"
                )

            return response.json()

        raise JiraAPIError("Unexpected retry loop exit")

    def get_issue(self, ticket_id: str) -> dict:
        url = f"{self.base_url}/rest/api/3/issue/{ticket_id}"
        return self._request("GET", url)

    def get_children(self, parent_id: str, project_type: str) -> list:
        if project_type == "nextgen":
            jql = f"parent = {parent_id}"
        else:
            jql = f'"Epic Link" = {parent_id}'

        results = []
        start_at = 0
        max_results = 100

        while True:
            url = f"{self.base_url}/rest/api/3/search"
            params = {
                "jql": jql,
                "startAt": start_at,
                "maxResults": max_results,
            }
            data = self._request("GET", url, params=params)
            issues = data.get("issues", [])
            results.extend(issues)

            if start_at + len(issues) >= data.get("total", 0):
                break
            start_at += len(issues)

        return results

    def get_comments(self, ticket_id: str) -> list:
        results = []
        start_at = 0
        max_results = 50

        while True:
            url = f"{self.base_url}/rest/api/3/issue/{ticket_id}/comment"
            params = {
                "startAt": start_at,
                "maxResults": max_results,
                "orderBy": "-created",
            }
            data = self._request("GET", url, params=params)
            comments = data.get("comments", [])
            results.extend(comments)

            if start_at + len(comments) >= data.get("total", 0):
                break
            start_at += len(comments)

        return results
