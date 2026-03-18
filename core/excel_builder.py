import io
import os
from datetime import date, datetime, timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from core.models import TicketTree, ReportConfig, Comment
from core.gantt import calc_date_range, generate_week_columns, ticket_in_week

GANTT_FILL = PatternFill(start_color="00B0F0", end_color="00B0F0", fill_type="solid")
HEADER_FONT = Font(bold=True)
HEADER_FILL = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")


def _auto_width(ws):
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val = str(cell.value) if cell.value is not None else ""
            max_len = max(max_len, len(val))
        ws.column_dimensions[col_letter].width = min(max_len + 2, 50)


def _write_header(ws, headers, row=1):
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col_idx, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL


def _sheet_tickets(wb, tree: TicketTree):
    ws = wb.create_sheet("Tickets")
    headers = ["ID", "Link", "Name", "Status", "Start Date", "Due Date",
               "Issue Type", "Parent ID", "Parent Name", "Assignee"]
    _write_header(ws, headers)
    ws.freeze_panes = "A2"

    for row_idx, ticket in enumerate(tree.all_tickets(), 2):
        ws.cell(row=row_idx, column=1, value=ticket.id)
        link_cell = ws.cell(row=row_idx, column=2, value=ticket.url)
        link_cell.hyperlink = ticket.url
        link_cell.font = Font(color="0563C1", underline="single")
        ws.cell(row=row_idx, column=3, value=ticket.name)
        ws.cell(row=row_idx, column=4, value=ticket.status)
        ws.cell(row=row_idx, column=5, value=ticket.start_date)
        ws.cell(row=row_idx, column=6, value=ticket.due_date)
        ws.cell(row=row_idx, column=7, value=ticket.issue_type)
        ws.cell(row=row_idx, column=8, value=ticket.parent_id or "")
        ws.cell(row=row_idx, column=9, value=ticket.parent_name or "")
        ws.cell(row=row_idx, column=10, value=ticket.assignee or "")

    _auto_width(ws)


def _sort_epics_by_due(epics):
    with_date = [e for e in epics if e.due_date is not None]
    without_date = [e for e in epics if e.due_date is None]
    with_date.sort(key=lambda e: e.due_date)
    return with_date + without_date


def _write_gantt_headers(ws, headers, week_columns):
    _write_header(ws, headers)
    col_offset = len(headers)
    for i, monday in enumerate(week_columns):
        col = col_offset + i + 1
        cell = ws.cell(row=1, column=col, value=monday.strftime("%d/%m"))
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center")
    ws.freeze_panes = "A2"


def _sheet_simplified_gantt(wb, tree: TicketTree, config: ReportConfig):
    ws = wb.create_sheet("Simplified Gantt")
    headers = ["ID", "Name", "Assignee", "Status", "Start Date", "Due Date"]

    open_epics = tree.filter_open_epics(config.open_statuses)
    sorted_epics = _sort_epics_by_due(open_epics)

    min_d, max_d = calc_date_range(sorted_epics)

    if not sorted_epics or min_d is None:
        _write_header(ws, headers)
        ws.freeze_panes = "A2"
        ws.cell(row=2, column=1, value="No open epics with dates found")
        _auto_width(ws)
        return

    week_columns = generate_week_columns(min_d, max_d)
    _write_gantt_headers(ws, headers, week_columns)
    col_offset = len(headers)

    for row_idx, epic in enumerate(sorted_epics, 2):
        ws.cell(row=row_idx, column=1, value=epic.id)
        ws.cell(row=row_idx, column=2, value=epic.name)
        ws.cell(row=row_idx, column=3, value=epic.assignee or "")
        ws.cell(row=row_idx, column=4, value=epic.status)
        ws.cell(row=row_idx, column=5, value=epic.start_date)
        ws.cell(row=row_idx, column=6, value=epic.due_date)

        for i, monday in enumerate(week_columns):
            if ticket_in_week(epic, monday):
                ws.cell(row=row_idx, column=col_offset + i + 1).fill = GANTT_FILL

    _auto_width(ws)


def _sheet_full_gantt(wb, tree: TicketTree, config: ReportConfig):
    ws = wb.create_sheet("Full Gantt")
    headers = ["ID", "Name", "Assignee", "Status", "Start Date", "Due Date"]

    open_epics = tree.filter_open_epics(config.open_statuses)
    sorted_epics = _sort_epics_by_due(open_epics)

    min_d, max_d = calc_date_range(sorted_epics)

    if not sorted_epics or min_d is None:
        _write_header(ws, headers)
        ws.freeze_panes = "A2"
        ws.cell(row=2, column=1, value="No open epics with dates found")
        _auto_width(ws)
        return

    week_columns = generate_week_columns(min_d, max_d)
    _write_gantt_headers(ws, headers, week_columns)
    col_offset = len(headers)

    row_idx = 2
    for epic in sorted_epics:
        ws.cell(row=row_idx, column=1, value=epic.id)
        ws.cell(row=row_idx, column=2, value=epic.name)
        ws.cell(row=row_idx, column=3, value=epic.assignee or "")
        ws.cell(row=row_idx, column=4, value=epic.status)
        ws.cell(row=row_idx, column=5, value=epic.start_date)
        ws.cell(row=row_idx, column=6, value=epic.due_date)

        for i, monday in enumerate(week_columns):
            if ticket_in_week(epic, monday):
                ws.cell(row=row_idx, column=col_offset + i + 1).fill = GANTT_FILL

        row_idx += 1

        for child in epic.children:
            ws.cell(row=row_idx, column=1, value=f"  {child.id}")
            ws.cell(row=row_idx, column=2, value=child.name)
            ws.cell(row=row_idx, column=3, value=child.assignee or "")
            ws.cell(row=row_idx, column=4, value=child.status)
            row_idx += 1

    _auto_width(ws)


def _filter_comments(comments, root_id, include_root: bool, lookback_days: int):
    cutoff = datetime.now() - timedelta(days=lookback_days)
    filtered = []
    for c in comments:
        if c.created < cutoff:
            continue
        is_root = c.ticket_id == root_id
        if include_root and is_root:
            filtered.append(c)
        elif not include_root and not is_root:
            filtered.append(c)
    filtered.sort(key=lambda c: c.created, reverse=True)
    return filtered


def _sheet_updates(wb, tree: TicketTree, config: ReportConfig):
    ws = wb.create_sheet("Updates")
    headers = ["Ticket ID", "Ticket Name", "Author", "Date", "Comment"]
    _write_header(ws, headers)
    ws.freeze_panes = "A2"

    comments = _filter_comments(tree.comments, tree.root.id, include_root=False, lookback_days=config.lookback_days)

    if not comments:
        ws.cell(row=2, column=1, value="No comments in the last 7 days")
        _auto_width(ws)
        return

    for row_idx, c in enumerate(comments, 2):
        ws.cell(row=row_idx, column=1, value=c.ticket_id)
        ws.cell(row=row_idx, column=2, value=c.ticket_name)
        ws.cell(row=row_idx, column=3, value=c.author)
        ws.cell(row=row_idx, column=4, value=c.created)
        ws.cell(row=row_idx, column=5, value=c.body)

    _auto_width(ws)


def _sheet_weekly_updates(wb, tree: TicketTree, config: ReportConfig):
    ws = wb.create_sheet("Weekly Updates")
    headers = ["Author", "Date", "Comment"]
    _write_header(ws, headers)
    ws.freeze_panes = "A2"

    comments = _filter_comments(tree.comments, tree.root.id, include_root=True, lookback_days=config.lookback_days)

    if not comments:
        ws.cell(row=2, column=1, value="No comments in the last 7 days")
        _auto_width(ws)
        return

    for row_idx, c in enumerate(comments, 2):
        ws.cell(row=row_idx, column=1, value=c.author)
        ws.cell(row=row_idx, column=2, value=c.created)
        ws.cell(row=row_idx, column=3, value=c.body)

    _auto_width(ws)


def build_excel(tree: TicketTree, config: ReportConfig) -> bytes:
    wb = Workbook()
    # Remove the default sheet
    wb.remove(wb.active)

    _sheet_tickets(wb, tree)
    _sheet_simplified_gantt(wb, tree, config)
    _sheet_full_gantt(wb, tree, config)
    _sheet_updates(wb, tree, config)
    _sheet_weekly_updates(wb, tree, config)

    buf = io.BytesIO()
    wb.save(buf)
    xlsx_bytes = buf.getvalue()

    # Save to output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    filename = f"{config.report_date.strftime('%Y%m%d')}_{tree.root.id}.xlsx"
    filepath = output_dir / filename
    with open(filepath, "wb") as f:
        f.write(xlsx_bytes)

    return xlsx_bytes
