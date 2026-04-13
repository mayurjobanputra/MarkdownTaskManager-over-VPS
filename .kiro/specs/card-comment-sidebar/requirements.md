# Requirements Document

## Introduction

This feature adds a comment sidebar to the card detail modal in the Markdown Task Manager, along with a user identity system that supports both human users and AI agents. The sidebar provides a chat-style conversation thread where users and AI agents can discuss and collaborate on card edits. A user identity prompt ensures every participant is identified before interacting, and a User Manager provides CRUD operations for managing users. User data is stored in the `**Users**:` config section of `kanban.md`, and comments are persisted as a `**Comments**:` section within each task block, keeping the system fully file-based and dependency-free.

## Glossary

- **Comment_Sidebar**: A panel displayed alongside the task detail content inside the task detail modal, containing a scrollable list of comments and a text input area for composing new comments.
- **Comment**: A single message entry in the Comment_Sidebar, consisting of an author identifier, a timestamp, and message text.
- **Task_Detail_Modal**: The existing modal (`#taskModal`) that displays task metadata, description, subtasks, and notes when a user clicks a card on the Kanban board.
- **Comment_Input**: The text input area at the bottom of the Comment_Sidebar where the user types a new comment.
- **Comment_List**: The scrollable area within the Comment_Sidebar that displays all comments for the current task in chronological order.
- **Markdown_Serializer**: The component (`generateMarkdown` function) responsible for converting in-memory task data back into markdown text for persistence.
- **Markdown_Parser**: The component (`parseTask` function) responsible for reading markdown text and populating in-memory task objects.
- **Config_Parser**: The component responsible for parsing the `## ⚙️ Configuration` section of `kanban.md`, including the `**Users**:` line.
- **Author_Tag**: A label on each comment indicating who wrote it, using the `@username` handle from the Users_Config.
- **Identity_Prompt**: A required, non-dismissable modal displayed to first-time users (or when no identity is stored in localStorage) that requires the user to select or create their identity before using the application.
- **User_Manager**: A CRUD interface accessible from the application header for creating, reading, updating, and deleting user entries in the Users_Config.
- **Users_Config**: The `**Users**:` line in the `## ⚙️ Configuration` section of `kanban.md`, storing all registered users with their username handle, display name, and role.
- **User_Entry**: A single user record containing a username (`@handle`), a display name, and a role (`human` or `agent`).
- **Active_Identity**: The currently selected User_Entry stored in localStorage, used as the author for new comments.
- **Agent_Example_File**: A template file (e.g., `CLAUDE.md.example`) in the project root that provides AI-specific configuration instructions referencing `AI_WORKFLOW.md`.
- **AI_WORKFLOW**: The `AI_WORKFLOW.md` file containing the authoritative strict task format, workflow rules, and guidelines for all AI assistants.
- **SKILL_File**: The `.claude/skills/markdown-task-manager/SKILL.md` file containing the Claude Code skill definition for markdown task management.

## Requirements

### Requirement 1: Display Comment Sidebar in Task Detail Modal

**User Story:** As a user, I want to see a comment sidebar when I open a card's detail modal, so that I can view the conversation history for that card without entering edit mode.

#### Acceptance Criteria

1. WHEN the Task_Detail_Modal is opened for a task, THE Comment_Sidebar SHALL be displayed as a right-side panel alongside the existing task detail content.
2. THE Comment_Sidebar SHALL display the Comment_List containing all comments for the current task in chronological order (oldest first).
3. WHILE the Task_Detail_Modal is open, THE Comment_Sidebar SHALL remain visible and accessible without requiring the user to switch to edit mode.
4. WHEN a task has zero comments, THE Comment_Sidebar SHALL display a localized empty-state message indicating no comments exist yet.
5. THE Comment_Sidebar SHALL use the existing translation system (`t()` function) for all user-facing text, with keys defined for both English and French.

### Requirement 2: Add New Comments

**User Story:** As a user, I want to type and submit comments from the sidebar, so that I can communicate with other users and AI agents about card edits directly from the detail view.

#### Acceptance Criteria

1. THE Comment_Sidebar SHALL display a Comment_Input area at the bottom of the panel.
2. WHEN the user types text into the Comment_Input and presses Enter or clicks a send button, THE Comment_Sidebar SHALL append a new Comment with the author set to the Active_Identity's username handle, the current date-time as the timestamp, and the entered text as the message body.
3. WHEN a new Comment is appended, THE Comment_List SHALL scroll to the bottom to display the newly added Comment.
4. WHEN the Comment_Input is empty and the user attempts to submit, THE Comment_Sidebar SHALL not create a new Comment.
5. WHEN a new Comment is appended, THE Markdown_Serializer SHALL persist the comment to the markdown file via the existing `autoSave()` mechanism.

### Requirement 3: Persist Comments in Markdown Format

**User Story:** As a user, I want my comments saved in the markdown file, so that the conversation history survives page reloads and is accessible to AI agents reading the file.

#### Acceptance Criteria

1. THE Markdown_Serializer SHALL write comments as a `**Comments**:` section within each task block, placed after the `**Notes**:` section.
2. THE Markdown_Serializer SHALL format each Comment as: `> **@author** (YYYY-MM-DD HH:mm): message text` using markdown blockquote syntax, with a blank line between each comment.
3. THE Markdown_Parser SHALL parse the `**Comments**:` section and populate a `comments` array on the task object, where each entry contains `author`, `timestamp`, and `text` fields.
4. FOR ALL valid task objects containing comments, parsing then serializing then parsing SHALL produce an equivalent comments array (round-trip property).
5. WHEN a task has no comments, THE Markdown_Serializer SHALL omit the `**Comments**:` section entirely.

### Requirement 4: Comment Display and Formatting

**User Story:** As a user, I want comments displayed in a readable chat-like format, so that the conversation flow between humans and AI agents is easy to follow.

#### Acceptance Criteria

1. THE Comment_Sidebar SHALL display each Comment as a distinct message bubble showing the Author_Tag, the timestamp, and the message text.
2. THE Comment_Sidebar SHALL use the role field from the Users_Config to visually distinguish comments from human users and agent users using different alignment, background colors, and an icon or badge indicating the role.
3. THE Comment_Sidebar SHALL render basic markdown formatting within comment text (bold, italic, inline code) using the existing `markdownToHtml` function.
4. THE Comment_Sidebar SHALL escape HTML entities in comment text to prevent script injection.
5. WHEN a comment's Author_Tag does not match any User_Entry in the Users_Config, THE Comment_Sidebar SHALL display the comment with a neutral default style.

### Requirement 5: Responsive Layout

**User Story:** As a user, I want the comment sidebar to adapt to different screen sizes, so that the modal remains usable on smaller displays.

#### Acceptance Criteria

1. THE Task_Detail_Modal SHALL use a two-column layout: task detail content on the left and Comment_Sidebar on the right, when the viewport width is 900 pixels or wider.
2. WHEN the viewport width is below 900 pixels, THE Task_Detail_Modal SHALL stack the Comment_Sidebar below the task detail content in a single-column layout.
3. THE Comment_Sidebar SHALL have a minimum height of 300 pixels and a maximum height constrained by the modal's viewport height.

### Requirement 6: AI Agent Comment Integration

**User Story:** As a user, I want AI agents to be able to add comments by editing the markdown file, so that I can have an asynchronous back-and-forth conversation through the comment thread.

#### Acceptance Criteria

1. WHEN the markdown file is reloaded or refreshed, THE Markdown_Parser SHALL parse any new comments added by external editors (including AI agents) into the task's comments array.
2. THE Comment format in markdown SHALL use the Author_Tag corresponding to the agent's `@username` from the Users_Config, allowing the Comment_Sidebar to identify and style agent comments using the role from the Users_Config.
3. IF a comment in the markdown file has a malformed format, THEN THE Markdown_Parser SHALL skip that comment and continue parsing the remaining comments without error.

### Requirement 7: User Identity Prompt

**User Story:** As a first-time user, I want to be prompted to select or create my identity before using the app, so that my comments are attributed to me.

#### Acceptance Criteria

1. WHEN the application loads and no Active_Identity is found in localStorage, THE Identity_Prompt SHALL be displayed as a non-dismissable modal overlay preventing interaction with the rest of the application.
2. THE Identity_Prompt SHALL display a list of existing human-role User_Entry records from the Users_Config for the user to select from.
3. THE Identity_Prompt SHALL provide an option to create a new User_Entry by entering a username handle and display name, with the role set to `human`.
4. WHEN the user selects an existing User_Entry or creates a new one, THE Identity_Prompt SHALL store the selected User_Entry as the Active_Identity in localStorage.
5. WHEN a new User_Entry is created via the Identity_Prompt, THE Config_Parser SHALL add the new User_Entry to the Users_Config in `kanban.md` and persist the change via `autoSave()`.
6. WHILE the Identity_Prompt is displayed, THE application SHALL not allow the user to interact with the Kanban board, modals, or any other UI element.
7. THE Identity_Prompt SHALL use the existing translation system (`t()` function) for all user-facing text.

### Requirement 8: User Manager

**User Story:** As a user, I want a management interface for users in the system, so that I can add, edit, and remove both human and AI agent identities.

#### Acceptance Criteria

1. THE application header SHALL include a button to open the User_Manager.
2. WHEN the User_Manager is opened, THE User_Manager SHALL display a list of all User_Entry records from the Users_Config, showing each entry's username handle, display name, and role.
3. THE User_Manager SHALL allow creating a new User_Entry by specifying a username handle, display name, and role (`human` or `agent`).
4. THE User_Manager SHALL allow editing an existing User_Entry's display name and role.
5. THE User_Manager SHALL allow deleting a User_Entry from the Users_Config.
6. WHEN a User_Entry is created, edited, or deleted via the User_Manager, THE Config_Parser SHALL update the Users_Config line in `kanban.md` and persist the change via `autoSave()`.
7. THE Users_Config line in `kanban.md` SHALL use the format: `**Users**: @handle1 (Display Name 1, role1), @handle2 (Display Name 2, role2)` where role is `human` or `agent`.
8. THE Config_Parser SHALL parse the Users_Config line and populate an in-memory array of User_Entry objects, each containing `username`, `displayName`, and `role` fields.
9. FOR ALL valid Users_Config content, parsing then serializing then parsing SHALL produce an equivalent array of User_Entry objects (round-trip property).
10. THE User_Manager SHALL use the existing translation system (`t()` function) for all user-facing text.
11. IF the user attempts to delete the User_Entry that matches the current Active_Identity, THEN THE User_Manager SHALL prevent the deletion and display a warning message.

### Requirement 9: Agent Identity

**User Story:** As a user, I want AI agents to self-identify using their registered username when writing comments, so that I can tell which agent authored each message.

#### Acceptance Criteria

1. THE Users_Config SHALL support User_Entry records with the role `agent` to represent AI agent identities.
2. WHEN an AI agent writes a comment by editing `kanban.md` directly, THE agent SHALL use its own `@username` from the Users_Config as the Author_Tag in the comment blockquote format.
3. THE application SHALL not provide a real-time notification system for new agent comments; the user views agent comments by reopening the Task_Detail_Modal or refreshing the board.

### Requirement 10: Role-Based Visual Distinction in Comments

**User Story:** As a user, I want to visually distinguish between human and AI agent comments at a glance, so that I can quickly identify who said what in the conversation.

#### Acceptance Criteria

1. WHEN rendering a Comment whose Author_Tag matches a User_Entry with role `human`, THE Comment_Sidebar SHALL display the comment aligned to the right with a human-specific background color and a person icon.
2. WHEN rendering a Comment whose Author_Tag matches a User_Entry with role `agent`, THE Comment_Sidebar SHALL display the comment aligned to the left with an agent-specific background color and a bot icon.
3. THE Comment_Sidebar SHALL display the author's display name (from the Users_Config) alongside the Author_Tag in each comment bubble.
4. WHEN a Comment's Author_Tag does not match any User_Entry in the Users_Config, THE Comment_Sidebar SHALL display the comment with neutral alignment, a default background color, and no role icon.

### Requirement 11: Fix File Extension Spelling

**User Story:** As a developer, I want the agent example template files to use the correct English spelling `.md.example` instead of the French spelling `.md.exemple`, so that the file extensions are consistent and discoverable.

#### Acceptance Criteria

1. THE project SHALL rename `CHATGPT.md.exemple` to `CHATGPT.md.example` in the project root.
2. THE project SHALL rename `CLAUDE.md.exemple` to `CLAUDE.md.example` in the project root.
3. THE project SHALL rename `CODEIUM.md.exemple` to `CODEIUM.md.example` in the project root.
4. THE project SHALL rename `COPILOT.md.exemple` to `COPILOT.md.example` in the project root.
5. THE project SHALL rename `GEMINI.md.exemple` to `GEMINI.md.example` in the project root.
6. THE project SHALL rename `OPENAI_CLI.md.exemple` to `OPENAI_CLI.md.example` in the project root.
7. THE project SHALL rename `QWEN.md.exemple` to `QWEN.md.example` in the project root.
8. WHEN the files are renamed, THE project SHALL update all references to `.md.exemple` in `README.md`, `readmeFR.md`, and `AI_WORKFLOW.md` to use `.md.example`.

### Requirement 12: Create KIRO.md.example

**User Story:** As a developer using Kiro, I want a `KIRO.md.example` agent configuration template, so that I can configure Kiro to use the Markdown task management system with comment and identity features.

#### Acceptance Criteria

1. THE project SHALL contain a `KIRO.md.example` file in the project root following the same minimal template pattern as the other agent example files.
2. THE `KIRO.md.example` file SHALL reference `AI_WORKFLOW.md` as the complete documentation source.
3. THE `KIRO.md.example` file SHALL include the critical rule about no `##` or `###` headings inside tasks.
4. THE `KIRO.md.example` file SHALL include instructions for Kiro on how to use the `**Comments**:` section to add comments to tasks using the blockquote format `> **@agent** (YYYY-MM-DD HH:mm): message text`.
5. THE `KIRO.md.example` file SHALL instruct Kiro to self-identify using its registered `@username` from the Users_Config when writing comments.

### Requirement 13: Update Agent Example Files with Comment and Identity Features

**User Story:** As a developer, I want all agent example files to document the comment system and user identity features, so that AI agents know how to participate in task conversations.

#### Acceptance Criteria

1. WHEN an agent example file is used as a configuration template, THE file SHALL document the `**Comments**:` section format for adding comments to tasks.
2. THE agent example files (CHATGPT, CLAUDE, CODEIUM, COPILOT, GEMINI, OPENAI_CLI, QWEN, and KIRO) SHALL each include instructions for the agent to self-identify using its `@username` from the Users_Config.
3. THE agent example files SHALL document the updated `**Users**:` format with roles: `@handle (Display Name, role)` where role is `human` or `agent`.
4. THE agent example files SHALL document the comment blockquote format: `> **@agent** (YYYY-MM-DD HH:mm): message text` for adding comments to the `**Comments**:` section of a task.

### Requirement 14: Update AI_WORKFLOW.md

**User Story:** As a developer, I want `AI_WORKFLOW.md` to document the comment system and updated user format, so that all AI agents have a single authoritative reference for the new features.

#### Acceptance Criteria

1. THE `AI_WORKFLOW.md` strict task format template SHALL include a `**Comments**:` section placed after the `**Notes**:` section.
2. THE `AI_WORKFLOW.md` SHALL document the comment blockquote format: `> **@author** (YYYY-MM-DD HH:mm): message text`.
3. THE `AI_WORKFLOW.md` SHALL document the updated `**Users**:` config format with roles: `@handle (Display Name, role)` where role is `human` or `agent`.
4. THE `AI_WORKFLOW.md` SHALL include instructions for agents on how to use the comment system: reading existing comments, adding new comments using their registered `@username`, and placing comments in the `**Comments**:` section.
5. THE `AI_WORKFLOW.md` examples section SHALL include at least one task example showing a `**Comments**:` section with sample comments from both a human and an agent user.
6. THE `AI_WORKFLOW.md` AI-Specific Configuration table SHALL include a row for Kiro referencing `KIRO.md` at the project root.

### Requirement 15: Update SKILL.md

**User Story:** As a developer using Claude Code, I want the `SKILL.md` file to document the comment system and updated user format, so that Claude Code can manage comments as part of its task management skill.

#### Acceptance Criteria

1. THE `.claude/skills/markdown-task-manager/SKILL.md` strict task format template SHALL include a `**Comments**:` section placed after the `**Notes**:` section.
2. THE `SKILL.md` SHALL document the comment blockquote format: `> **@author** (YYYY-MM-DD HH:mm): message text`.
3. THE `SKILL.md` SHALL document the updated `**Users**:` config format with roles: `@handle (Display Name, role)` where role is `human` or `agent`.
4. THE `SKILL.md` SHALL include instructions for Claude on how to read existing comments and add new comments using its registered `@username` from the Users_Config.
5. THE `SKILL.md` examples section SHALL include at least one task example showing a `**Comments**:` section with sample comments.
6. THE `SKILL.md` Skill Functions section SHALL include comment management functions: reading comments from a task, adding a comment to a task, and using the agent's registered identity.

### Requirement 16: Update README.md and readmeFR.md

**User Story:** As a user or contributor, I want the project documentation to describe the comment sidebar, user identity system, and updated file formats, so that the README accurately reflects the current feature set.

#### Acceptance Criteria

1. THE `README.md` SHALL document the comment sidebar feature in the Task_Detail_Modal, describing the chat-style conversation thread for human-agent collaboration.
2. THE `README.md` SHALL document the user identity system: the Identity_Prompt on first use, localStorage persistence, and the Active_Identity concept.
3. THE `README.md` SHALL document the User_Manager for creating, reading, updating, and deleting users with roles (`human` or `agent`).
4. THE `README.md` SHALL document the `**Comments**:` markdown format with the blockquote syntax for comments.
5. THE `README.md` SHALL document the updated `**Users**:` config format with roles: `@handle (Display Name, role)`.
6. THE `README.md` AI Assistants Integration table SHALL include a row for Kiro referencing `KIRO.md` at the project root, with `KIRO.md.example` listed as an available template.
7. THE `README.md` SHALL use the corrected file extension `.md.example` instead of `.md.exemple` in all references to agent template files.
8. THE `readmeFR.md` SHALL include equivalent documentation updates as `README.md` for the comment sidebar, user identity system, User_Manager, `**Comments**:` format, updated `**Users**:` format, Kiro entry, and corrected file extensions, written in French.
9. WHEN screenshots or diagrams are referenced for the new features, THE `README.md` and `readmeFR.md` SHALL include placeholder notes (e.g., `<!-- TODO: Add screenshot for comment sidebar -->`) where new visual documentation is needed.

### Requirement 17: Update Example Templates

**User Story:** As a developer setting up a new project, I want the example templates to demonstrate the comment system and updated user format, so that I can see the correct syntax from the start.

#### Acceptance Criteria

1. THE `examples/kanban.md` Configuration section SHALL use the updated `**Users**:` format with roles: `@handle (Display Name, role)`, for example `@alice (Alice, human), @bob (Bob, human), @claude (Claude, agent)`.
2. THE `examples/kanban.md` SHALL include at least one task with a `**Comments**:` section demonstrating the blockquote comment format.
3. THE `examples/kanban.md` SHALL include at least one task with a `**Comments**:` section showing a conversation between a human user and an AI agent.
4. THE `examples/archive.md` SHALL include at least one archived task with a `**Comments**:` section demonstrating the blockquote comment format.
5. FOR ALL example tasks containing comments, THE comment format SHALL use `> **@author** (YYYY-MM-DD HH:mm): message text` with a blank line between each comment.
