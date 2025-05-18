from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from .database import Base
import enum

class TaskStatus(enum.Enum):
    new = "new"
    in_progress = "in_progress"
    done = "done"

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.new, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class TaskHistory(Base):
    __tablename__ = "task_history"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=False)
    status = Column(Enum(TaskStatus), nullable=False)
    change_type = Column(String, nullable=False)
    changed_at = Column(DateTime, server_default=func.now(), nullable=False)
