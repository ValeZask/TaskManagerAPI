from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from .models import Task, TaskHistory, TaskStatus
from .schemas import TaskCreate, TaskUpdate
from fastapi import HTTPException
from datetime import datetime, date
from pytz import timezone
from typing import Optional

KG_TIMEZONE = timezone("Asia/Bishkek")


def create_task(db: Session, task: TaskCreate):
    existing_task = db.query(Task).filter(Task.title == task.title, Task.due_date == task.due_date).first()
    if existing_task:
        raise HTTPException(status_code=400, detail="Task with this title and due date already exists")
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    db_history = TaskHistory(
        task_id=db_task.id,
        title=db_task.title,
        description=db_task.description,
        due_date=db_task.due_date,
        status=db_task.status,
        change_type="created"
    )
    db.add(db_history)
    db.commit()
    return db_task


def get_task(db: Session, task_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def get_tasks(db: Session, status: Optional[TaskStatus] = None, due_date: Optional[date] = None):
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)
    if due_date:
        start_of_day = datetime.combine(due_date, datetime.min.time(), tzinfo=KG_TIMEZONE)
        end_of_day = datetime.combine(due_date, datetime.max.time(), tzinfo=KG_TIMEZONE)
        query = query.filter(Task.due_date.between(start_of_day, end_of_day))
    return query.all()


def update_task(db: Session, task_id: int, task_update: TaskUpdate):
    db_task = get_task(db, task_id)
    update_data = task_update.model_dump(exclude_unset=True)
    if "title" in update_data or "due_date" in update_data:
        new_title = update_data.get("title", db_task.title)
        new_due_date = update_data.get("due_date", db_task.due_date)
        existing_task = db.query(Task).filter(Task.id != task_id, Task.title == new_title, Task.due_date == new_due_date).first()
        if existing_task:
            raise HTTPException(status_code=400, detail="Task with this title and due date already exists")
    change_type = "updated_" + "_".join(update_data.keys())
    for key, value in update_data.items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    db_history = TaskHistory(
        task_id=db_task.id,
        title=db_task.title,
        description=db_task.description,
        due_date=db_task.due_date,
        status=db_task.status,
        change_type=change_type
    )
    db.add(db_history)
    db.commit()
    return db_task


def delete_task(db: Session, task_id: int):
    db_task = get_task(db, task_id)
    db.delete(db_task)
    db.commit()
    return db_task


def get_task_history(db: Session, task_id: int):
    get_task(db, task_id)
    return db.query(TaskHistory).filter(TaskHistory.task_id == task_id).all()
