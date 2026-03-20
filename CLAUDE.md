# Claude Code — Project Instructions

## Session Startup

At the start of every session:
1. Read `MEMORY.md` if it exists — it contains persistent learnings from past sessions.
2. Read `SYSTEM.md` if it exists — it contains a lightweight description of the current system state and active projects.
3. Read `SKILLS.md` and note available skills before starting work.

## System Context

- `SYSTEM.md` is the always-loaded system index. It describes the existing system at a high level without requiring all project files to be read.
- `SYSTEM.md` contains:
  - A brief description of what the system does and its main components
  - Key architectural decisions that must be respected across all projects
  - A list of completed and active projects with one-line summaries and links to their `P-xxxx.md`
  - Cross-project constraints that apply to every session
- Never load individual project files unless the user specifies which project to work on.
- When a project's final scope is marked `[DONE]`, update the project's entry in `SYSTEM.md` to reflect its completed status.
- If `SYSTEM.md` does not exist at session start, ask the user whether to create it before proceeding.

The expected `SYSTEM.md` format is:

```
# System: [System Name]

## What This System Does
[2–4 sentences describing the system's purpose and main components]

## Architecture Principles
- [Key decision that must be respected, e.g., "API-first: all features exposed via REST before UI"]
- [Another constraint, e.g., "Single Postgres database — no secondary datastores"]

## Cross-Project Constraints
- [Constraint that applies to every project, e.g., "All auth uses JWT via auth-service"]

## Projects
| ID      | Name            | Status      | Summary                              |
|---------|-----------------|-------------|--------------------------------------|
| P-0001  | [Project Name]  | [DONE]      | One-line description                 |
| P-0002  | [Project Name]  | [ACTIVE]    | One-line description                 |
```

---

## General

- Plans are produced externally and arrive as `docs/Projects/P-xxxx.md`. Do not modify the plan — if something in it is wrong or unclear, stop and ask.
- I will indicate in which project we will be working on by specifying the corresponding file.
- Do NOT read all the files in `docs/Projects/` folder unless instructed to.
- Commit after each completed task (not mid-implementation). Use clear, descriptive commit messages.
- When blocked or at a decision point with no clear answer, stop and ask rather than guessing.
- Prefer the simplest solution that works. Do not create abstractions unless there are at least two concrete use cases today.

## Memory

- `MEMORY.md` is the only place for persistent learnings. Update it when you discover gotchas, failed patterns, or non-obvious constraints.
- Never solve the same problem twice — if you're re-discovering something, it belongs in `MEMORY.md`.

## Skills

- Skills are reusable operation playbooks stored in `skills/` and indexed in `SKILLS.md`.
- Before performing any complex operation, check `SKILLS.md` for a matching skill and follow it exactly.
- If you discover a better way to perform a skill's operation, propose updating it.
- If no skill exists for a repeated operation, propose creating one after completing the task.

## Branching Strategy

- Branch naming: `scope/P-XXXX-NUMBER-<short-description>`
- Always branch off `main`. Never branch off another scope branch.
- One agent per branch when working in parallel.
- Never commit directly to `main` except for trivial fixes.
- Check with me before merging to main.
- If multiple branches are open, before merging to main, merge to a test branch and run all tests for all the included scopes.
- Delete the branches after merging to main.

## Planning

For any non-trivial task, plan before coding:
1. Explore relevant files, patterns, and existing implementations.
2. Read architecture docs and constraints.
3. If a spec package exists for the project (e.g., `spec.md`, `workflows.md`, `data_model.md`, `architecture.md` in the same folder as `P-xxxx.md`), read them before proposing an approach.
4. Propose an approach and identify all files to be modified.
5. Wait for approval before writing any code.

## Testing

- Tests are goal-oriented: acceptance criteria are defined in each `docs/Projects/P-xxxx.md` file, not implementation details.
- Run all tests for the **active project's** scopes before marking any scope complete.
- Use subagents defined in `.claude/agents/` to run tests. Each subagent covers one domain.
- Subagents read the acceptance criteria for their scope from `P-xxxx.md` and determine how to verify them.
- Run tests before marking any scope complete.
- Spawn as many sub-agents as needed.

### Regression Tests (`TESTS.md`)

- `TESTS.md` (at the repo root) is the cumulative regression test registry across all projects.
- When a scope is marked `[DONE]`, append its acceptance criteria to `TESTS.md`, grouped by project and scope, with a source reference (e.g., `P-0001 / Scope 2`).
- When a project modifies behavior defined in a previous project, update the affected entries in `TESTS.md` at the same time — do not leave stale criteria.
- For regression runs, read only `TESTS.md`. Do not re-load all `P-xxxx.md` files.

## Progress Tracking

- `P-xxxx.md` is the single source of truth for progress. Keep it current:
- Mark tasks `[x]` as they are completed.
- Update Scope status (`[ ]` → `[IN PROGRESS]` → `[DONE]`) after each commit.
- Never mark a Scope `[DONE]` unless its tests have passed.

## Documentation

- Document all APIs as part of the task that implements them. REST APIs must use OpenAPI.
- At the end of each scope, update `docs/System/` to reflect the current state of the system. The following files must be kept up to date:
  - `workflows.md`
    - A set of Mermaid diagrams covering the main workflows and interactions:
    - `flowchart` for process flows and decision logic
    - `sequenceDiagram` for system/component interactions and API calls
  - `architecture.md` Mermaid diagrams covering:
    - High-level component architecture
    - Deployment topology
    - External system interactions
    - Data flow between components
  - `dataModel.md`: Mermaid `erDiagram` and/or `classDiagram` representing the data model.
    - Use `classDiagram` for objects/classes model.
    - Use `erDiagram` for databases.
    - Include field types and key relationships
- For every schema change, create a migration and rollback script in `docs/System/migrations/`, named `YYYYMMDD_short_description.sql`.
- Use sub-agents for documentation.
