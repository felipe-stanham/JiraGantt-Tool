# wireframes.md — P-0002 UI & Excel Enhancements

---

## Screen: Main App — Create Model Epic Section [cap-005]

This section appears below the existing report form in the main area. It is always rendered.

```
+----------------------------------------------------------+
| JIRA FEATURE REPORT                          [sidebar →] |
+----------------------------------------------------------+
|                                                          |
|  Enter a Jira Feature ticket ID to generate the report.  |
|                                                          |
|  Ticket ID  [ MTC-1234                    ]             |
|                                                          |
|  [ Generate Report ]                                     |
|                                                          |
|  -- (report output area, unchanged from P-0001) --      |
|                                                          |
+----------------------------------------------------------+
|                                                          |
|  ── Create Model Epic ──────────────────────────────     |
|                                                          |
|  Feature ID  [ MTC-1234                   ]             |
|  (same field, shared with report above)                  |
|                                                          |
|  Epic Name   [                            ]             |
|                                                          |
|  [ Create Model Epic ]  ← disabled when either empty    |
|                                                          |
|  (success) ✓ Epic created: MTC-5678                     |
|             https://org.atlassian.net/browse/MTC-5678    |
|                                                          |
|  (error)   ✗ Jira API error: <message>                  |
|                                                          |
+----------------------------------------------------------+
```

**Notes:**
- The Feature ID input is the same `st.text_input` widget as the report — both sections read from the same session-state value.
- The Epic Name input is a separate `st.text_input`, only used for this section.
- The Create button is `disabled=True` when `ticket_id` or `epic_name` is empty.
- Success and error messages appear directly below the button, inline.
- The section is always visible; it does not depend on a report having been generated.

---

## Excel: Full Gantt Sheet — Visual Separators and Colors [cap-002, cap-003, cap-004]

The Full Gantt sheet layout does not change structurally. The visual changes are:

```
Row 1: HEADER (bold, blue fill)
       [ ID   | Name          | Assignee | STATUS      | Start | Due | W1 | W2 | W3 | ... ]

Row 2: EPIC row
       [ MTC-10 | Epic Alpha  | J.Smith  | IN PROGRESS | ...   | ... |████|████|    | ... ]
         ↑ status cell filled with status color          ↑ week cells filled with status color

Row 3: Child row (Story)
       [   MTC-11 | Story A   | J.Jones  | BACKLOG     |       |     |    |    |    | ... ]
         ↑ 2-space indent in ID              ↑ status cell filled ─────────── thin border ↓

Row 4: Sub-task row (depth 3)
       [     MTC-12 | Sub-task | J.Jones | TO DO       |       |     |    |    |    | ... ]
         ↑ 4-space indent in ID              ↑ status cell filled ─────────── thin border ↓

Row 5: Child row (Story)
       [   MTC-15 | Story B   | A.Lee    | IN REVIEW   |       |     |    |    |    | ... ]
                                                                             ─── thin border ↓

Row 6: ══════════════════════════════════════════════════════════  ← THICK border (epic sep)

Row 7: EPIC row
       [ MTC-20 | Epic Beta   | ...      | BLOCKED     | ...   | ... |    |████|████| ... ]
```

**Border rules:**
- **Thick (medium weight):** bottom border of the last row in each Epic group. Applied to all columns including week columns.
- **Thin (thin weight):** bottom border of each child row (depth 2 and depth 3). Applied to all columns.
- No blank rows are inserted anywhere.

**Color rules:**
- Gantt week cells: filled with the status color of that row's ticket (not a global constant).
- Status column cell: filled with the status color of that row's ticket.
- All other cells: no special fill (white/default).

**Ordering:**
- Children of each Epic sorted by ticket ID numeric suffix, ascending.
- Sub-tasks of each Story sorted by ticket ID numeric suffix, ascending.
- Epic ordering (by due date) is unchanged from P-0001.
```
