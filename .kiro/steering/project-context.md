---
inclusion: always
---

# Markdown Task Manager - Project Context

## Overview
This is a single-file Kanban task manager (`task-manager.html`) that reads/writes local Markdown files (`kanban.md`, `archive.md`) using the browser's File System Access API. It also supports a remote/VPS mode via `serve.py` (Python HTTP server on port 8444) with REST API endpoints.

## Architecture
- Single HTML file with embedded CSS and JavaScript (no build tools, no frameworks, no dependencies)
- Uses File System Access API for local mode, HTTP API for remote mode
- Data stored in Markdown files following a strict task format (see `AI_WORKFLOW.md`)
- Translation system supports English and French (`translations` object)
- IndexedDB for storing project directory handles across sessions

## Key Files
- `task-manager.html` — The entire app (HTML + CSS + JS, ~3500 lines)
- `serve.py` — Python HTTP server for VPS/remote access
- `AI_WORKFLOW.md` — Strict task format and workflow guidelines for AI assistants
- `kanban.md` — Active tasks in Markdown
- `archive.md` — Archived tasks in Markdown

## Task Format (Strict)
```markdown
### TASK-XXX | Task title
**Priority**: [Value] | **Category**: [Value] | **Assigned**: @user
**Created**: YYYY-MM-DD | **Started**: YYYY-MM-DD | **Due**: YYYY-MM-DD | **Finished**: YYYY-MM-DD
**Tags**: #tag1 #tag2
Description text (no ## or ### headings inside tasks)
**Subtasks**:
- [ ] Subtask item
- [x] Completed subtask
**Notes**:
Free-form notes with Markdown support
```

## Conventions
- No external dependencies — everything is self-contained in the HTML file
- All UI text goes through the `t()` translation function with keys in `translations` object
- Modals use `.modal` / `.modal.active` pattern for show/hide
- Task data is parsed from Markdown and stored in the `tasks` array
- Changes are saved back to Markdown files immediately (auto-save)
- CSS uses CSS custom properties (`:root` variables) for theming
- Priority colors map from emoji icons via `priorityIconClasses`

## Important Constraints
- No `##` or `###` headings inside task content (parser limitation)
- File System Access API only works in Chrome 86+, Edge 86+, Opera 72+
- The app must remain a single HTML file with zero dependencies
