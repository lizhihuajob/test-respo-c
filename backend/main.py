from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保数据目录存在
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# 连接数据库
DATABASE_PATH = os.getenv('DATABASE_PATH', os.path.join(DATA_DIR, 'kanban.db'))
conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
c = conn.cursor()

# 创建任务表
c.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL CHECK(status IN ('todo', 'doing', 'done')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# 路由
@app.get("/api/tasks")
def get_tasks():
    c.execute("SELECT * FROM tasks ORDER BY created_at")
    tasks = c.fetchall()
    return [{"id": task[0], "title": task[1], "description": task[2], "status": task[3], "created_at": task[4]} for task in tasks]

@app.post("/api/tasks")
def create_task(task: dict = Body(...)):
    try:
        logger.info(f"Received task creation request: {task}")
        
        # 验证必要字段
        if not task.get("title"):
            logger.error("Task title is required")
            raise HTTPException(status_code=400, detail="Task title is required")
        
        title = task["title"]
        description = task.get("description", "")
        status = task.get("status", "todo")
        
        logger.info(f"Inserting task: title={title}, description={description}, status={status}")
        
        c.execute("INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)", 
                 (title, description, status))
        conn.commit()
        
        new_task = {"id": c.lastrowid, "title": title, "description": description, "status": status}
        logger.info(f"Task created successfully: {new_task}")
        
        return new_task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, task: dict = Body(...)):
    try:
        logger.info(f"Received task update request for id={task_id}: {task}")
        
        # 检查任务是否存在
        c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        existing_task = c.fetchone()
        if not existing_task:
            logger.error(f"Task not found: id={task_id}")
            raise HTTPException(status_code=404, detail="Task not found")
        
        # 验证必要字段
        if not task.get("title"):
            logger.error("Task title is required")
            raise HTTPException(status_code=400, detail="Task title is required")
        if not task.get("status"):
            logger.error("Task status is required")
            raise HTTPException(status_code=400, detail="Task status is required")
        
        title = task["title"]
        description = task.get("description", "")
        status = task["status"]
        
        logger.info(f"Updating task: id={task_id}, title={title}, description={description}, status={status}")
        
        # 更新任务
        c.execute("UPDATE tasks SET title = ?, description = ?, status = ? WHERE id = ?", 
                 (title, description, status, task_id))
        conn.commit()
        
        updated_task = {"id": task_id, "title": title, "description": description, "status": status}
        logger.info(f"Task updated successfully: {updated_task}")
        
        return updated_task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    try:
        c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        conn.commit()
        return {"message": "Task deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)