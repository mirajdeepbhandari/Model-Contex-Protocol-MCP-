# ToDo Database Instructions (CRUD Operations)

This guide explains how to interact with the ToDo SQLite database, including required fields, formats, and proper display of task data.

## 1. Database Overview

### Fields and Requirements:

- **id**: Auto-incremented primary key. No input needed.
- **title**: Required. The name of the task.
- **description**: Optional. Default is empty string.
- **created_date**: Required. Must be in YYYY-MM-DD format.
- **status**: Required. Allowed values are "pending", "done", "notneeded". Default is "pending".
- **priority**: Required. Allowed values are "low", "medium", "high". Default is "medium".

## 2. Adding a Task

- All required fields must be provided.
- `title` and `created_date` cannot be empty.
- `status` and `priority` must match the allowed values.
- If any required field is missing or invalid, an error will be returned.
- Successful addition returns confirmation and task ID.

## 3. Listing Tasks

Tasks can be listed in two ways:

- **All Tasks**: Displays every task in the database, ordered by creation date (most recent first).
- **By Priority**: Filters tasks based on priority (low, medium, high), ordered by creation date (most recent first).

### Display Format

Always show tasks in a tabular structure with the following columns:

| ID | Title | Description | Created Date | Status | Priority |
|----|-------|-------------|--------------|--------|----------|
| 1  | Finish report | Complete financial report | 2025-11-30 | pending | high |
| 2  | Grocery shopping | Buy weekly groceries | 2025-11-29 | done | medium |

## 4. Updating a Task

- Requires task ID and a verified email.
- Only the fields provided will be updated; others remain unchanged.
- Invalid or missing task ID or unverified email will return an error.
- Successful update returns confirmation message.

## 5. Deleting a Task

- Requires task ID and a verified email.
- If the task ID does not exist, a "not found" message is returned.
- Only a verified email can delete tasks; unauthorized attempts return an error.
- Successful deletion returns confirmation message.

## 6. Notes and Best Practices

- Always provide the correct date format (YYYY-MM-DD) to avoid errors.
- Use only allowed values for status and priority.
- When listing tasks, always display in a clear tabular format for easy reading.
- Keep your verified email ready for update or delete operations.
- Handle errors carefully and provide missing or invalid fields when prompted.