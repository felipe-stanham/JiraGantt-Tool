from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional, Tuple


@dataclass
class Config:
    jira_url: str
    jira_user: str
    jira_token: str
    start_date_field_id: str
    due_date_field_id: str
    project_type: str  # "classic" | "nextgen"
    open_statuses: List[str] = field(default_factory=lambda: [
        "Backlog", "Blocked", "On Hold", "Pending Manager Approval",
        "In Progress", "In Review", "Waiting for Response",
    ])

    @staticmethod
    def from_env() -> Config:
        from core.config import load_config
        return load_config()


@dataclass
class Ticket:
    id: str
    url: str
    name: str
    status: str
    start_date: Optional[date]
    due_date: Optional[date]
    issue_type: str
    parent_id: Optional[str]
    parent_name: Optional[str]
    assignee: Optional[str]
    depth: int  # 0=Feature, 1=Epic, 2=Story/Task
    children: List[Ticket] = field(default_factory=list)


@dataclass
class Comment:
    ticket_id: str
    ticket_name: str
    author: str
    created: datetime
    body: str


@dataclass
class TicketTree:
    root: Ticket
    comments: List[Comment] = field(default_factory=list)

    def all_tickets(self) -> List[Ticket]:
        result = []
        self._dfs(self.root, result)
        return result

    def _dfs(self, ticket: Ticket, result: List[Ticket]) -> None:
        result.append(ticket)
        for child in ticket.children:
            self._dfs(child, result)

    def epics(self) -> List[Ticket]:
        return [t for t in self.all_tickets() if t.depth == 1]

    def stories(self) -> List[Ticket]:
        return [t for t in self.all_tickets() if t.depth == 2]

    def filter_open_epics(self, open_statuses: List[str]) -> List[Ticket]:
        return [t for t in self.epics() if t.status in open_statuses]

    def date_range(self) -> Tuple[Optional[date], Optional[date]]:
        dates = []
        for t in self.all_tickets():
            if t.start_date:
                dates.append(t.start_date)
            if t.due_date:
                dates.append(t.due_date)
        if not dates:
            return (None, None)
        return (min(dates), max(dates))


@dataclass
class ReportConfig:
    open_statuses: List[str]
    report_date: date
    lookback_days: int = 7


@dataclass
class ExcelReport:
    xlsx_bytes: bytes
    filename: str
