from datetime import date, timedelta
from typing import List, Optional, Tuple
from core.models import Ticket


def calc_date_range(tickets: List[Ticket]) -> Tuple[Optional[date], Optional[date]]:
    start_dates = [t.start_date for t in tickets if t.start_date]
    due_dates = [t.due_date for t in tickets if t.due_date]
    all_dates = start_dates + due_dates

    if not all_dates:
        return (None, None)

    return (min(all_dates), max(all_dates))


def generate_week_columns(min_date: date, max_date: date) -> List[date]:
    monday = min_date - timedelta(days=min_date.weekday())
    end_sunday = max_date + timedelta(days=(6 - max_date.weekday()))

    weeks = []
    current = monday
    while current <= end_sunday:
        weeks.append(current)
        current += timedelta(days=7)

    return weeks


def ticket_in_week(ticket: Ticket, week_monday: date) -> bool:
    week_sunday = week_monday + timedelta(days=6)

    if ticket.start_date and ticket.due_date:
        return ticket.start_date <= week_sunday and ticket.due_date >= week_monday
    if ticket.start_date:
        return ticket.start_date <= week_sunday
    if ticket.due_date:
        return ticket.due_date >= week_monday

    return False
