from pathlib import Path
from fastmcp import FastMCP
import os
from loguru import logger
import aiosqlite
import tempfile
from configs.config_loader import settings
import datetime
from fastmcp.resources import FileResource

resource_path = Path("resources/database_todo_instructions.md").resolve()
prompt_path = Path("prompts/todo_database_prompt.txt").resolve()
TEMP_DIR = tempfile.gettempdir()
DB_PATH = os.path.join(TEMP_DIR, "todo.db")

class DBTools:
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self.init_db()
        logger.info("Registering DBTools methods...")
        self.register_tools()
        self.register_resources()
        self.register_prompts()
        
    def init_db(self):
        try:
            import sqlite3
            with sqlite3.connect(DB_PATH) as c:
                c.execute("PRAGMA journal_mode=WAL")
                c.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    created_date DATE NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'done', 'notneeded')),
                    priority TEXT NOT NULL DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high'))
                )
                """
                )
                logger.info(f"Database initialized at {DB_PATH}")
        except Exception as e:
            print(f"Database initialization error: {e}")
            raise

    async def add_task(self, title=None, description=None, created_date=None, status=None, priority=None):

        def is_missing(val):
            return val is None or str(val).strip() == ""

        # Collect missing fields
        missing_fields = []
        if is_missing(title):
            missing_fields.append("title")
        if is_missing(description):
            missing_fields.append("description")
        if is_missing(created_date):
            missing_fields.append("created_date")
        if is_missing(status):
            missing_fields.append("status")
        if is_missing(priority):
            missing_fields.append("priority")

        if missing_fields:
            return {
                "status": "error",
                "message": f"Please provide the following required fields: {', '.join(missing_fields)}"
            }

        allowed_status = {"pending", "done", "notneeded"}
        allowed_priority = {"low", "medium", "high"}
        if status not in allowed_status:
            return {"status": "error", "message": f"Invalid status. Allowed: {allowed_status}"}
        if priority not in allowed_priority:
            return {"status": "error", "message": f"Invalid priority. Allowed: {allowed_priority}"}

        try:
            date_obj = datetime.datetime.strptime(created_date, "%Y-%m-%d")
            created_date = date_obj.strftime("%Y-%m-%d") 
        except Exception:
            return {"status": "error", "message": "Invalid date format. Use YYYY-MM-DD."}

        # Insert into DB
        try:
            async with aiosqlite.connect(DB_PATH) as c:
                cur = await c.execute(
                    "INSERT INTO tasks(title, description, created_date, status, priority) VALUES (?,?,?,?,?)",
                    (title, description, created_date, status, priority)
                )
                task_id = cur.lastrowid
                await c.commit()
                return {"status": "success", "id": task_id, "message": "Task added successfully"}
        except Exception as e:
            if "readonly" in str(e).lower():
                return {"status": "error", "message": "Database is in read-only mode. Check file permissions."}
            return {"status": "error", "message": f"Database error: {str(e)}"}
    
    async def list_all_tasks(self):
        try:
            async with aiosqlite.connect(DB_PATH) as c:
                cur = await c.execute(
                    """
                    SELECT id, title, description, created_date, status, priority
                    FROM tasks
                    ORDER BY created_date DESC, id DESC
                    """
                )
                cols = [d[0] for d in cur.description]
                rows = await cur.fetchall()
                return [dict(zip(cols, r)) for r in rows]

        except Exception as e:
            return {"status": "error", "message": f"Error listing all tasks: {str(e)}"}
    
    async def list_tasks_by_priority(self, priority):
        allowed_priority = {"low", "medium", "high"}
        # Validate priority
        if priority not in allowed_priority:
            return {
                "status": "error",
                "message": f"Invalid priority. Allowed values: {allowed_priority}",
            }
        try:
            async with aiosqlite.connect(DB_PATH) as c:
                cur = await c.execute(
                    """
                    SELECT id, title, description, created_date, status, priority
                    FROM tasks
                    WHERE priority = ?
                    ORDER BY created_date DESC, id DESC
                    """,
                    (priority,),
                )
                cols = [d[0] for d in cur.description]
                rows = await cur.fetchall()
                return [dict(zip(cols, r)) for r in rows]
        except Exception as e:
            return {"status": "error", "message": f"Error listing tasks: {str(e)}"}
    
    async def delete_task(self, task_id, email=None):
        try:
            if email != settings.VERFIFIED_EMAIL:
                return {"status": "error", "message": "Unauthorized: Invalid email address please provide verfified email"}
            
            async with aiosqlite.connect(DB_PATH) as c:
                cur = await c.execute(
                    "DELETE FROM tasks WHERE id = ?",
                    (task_id,)
                )
                await c.commit()

                if cur.rowcount == 0:
                    return {"status": "not_found", "message": "No task found with that ID"}

                return {"status": "success", "message": f"Task {task_id} deleted successfully"}
        except Exception as e:
            return {"status": "error", "message": f"Error deleting task: {str(e)}"}
        
    async def update_task(self, task_id, title=None, description=None, priority=None, status=None, email=None):
        try:
            if email != settings.VERFIFIED_EMAIL:
                return {"status": "error", "message": "Unauthorized: Invalid email address please provide verfified email"}
            
            fields = []
            values = []
            
            if title is not None:
                fields.append("title = ?")
                values.append(title)
            if description is not None:
                fields.append("description = ?")
                values.append(description)
            if priority is not None:
                fields.append("priority = ?")
                values.append(priority)
            if status is not None:
                fields.append("status = ?")
                values.append(status)
            if not fields:
                return {"status": "error", "message": "No fields provided to update"}

            values.append(task_id)
            async with aiosqlite.connect(DB_PATH) as c:
                cur = await c.execute(
                    f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?",
                    values
                )
                await c.commit()
                if cur.rowcount == 0:
                    return {"status": "not_found", "message": "Task not found"}
                return {"status": "success", "message": f"Task {task_id} updated successfully"}
        except Exception as e:
            return {"status": "error", "message": f"Error updating task: {str(e)}"}
        
     # registering all the tools
    
    def register_tools(self):
        tools = [
            (self.add_task, "add_task", "Add a new task to the database"),
            (self.list_all_tasks, "list_all_tasks", "List all the tasks in the database"),
            (self.list_tasks_by_priority, "list_tasks_by_priority", "List tasks by priority"),
            (self.delete_task, "delete_task", "Delete a task by its ID"),
            (self.update_task, "update_task", "Update details of a task by its ID"),
        ]
        for method, name, desc in tools:
            self.mcp.tool(method, name=name, description=desc)
            logger.info("="*40)
            logger.info(f"Registered tool: {name}")
        logger.info("="*40)
        
    #registering the db resource
    def register_resources(self):
        if resource_path.exists():
            readme_resource = FileResource(
                    uri=f"file://{resource_path.as_posix()}",
                    path=resource_path , 
                    name="database_todo_instructions",
                    description="""this file contains instructions on how to use the todo database including CRUD operations
                    what fields are required and their formats and how to display the data properly.
                    """,
                    mime_type="text/markdown",
                    tags={"database instructions", "instructions for crud", "db usage"},
                )
            self.mcp.add_resource(readme_resource)
            
          
    #registering the db prompts
    def register_prompts(self):
        def todo_prompt_template():
            with open(prompt_path, 'r') as f:
                prompt_content = f.read()
            return prompt_content
        self.mcp.prompt(
           todo_prompt_template,
           name="todo_prompt",
        )

