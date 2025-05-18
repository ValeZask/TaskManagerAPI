from pydantic import BaseModel, field_validator, Field
from datetime import datetime
from typing import Optional
from .models import TaskStatus
from pytz import timezone

KG_TIMEZONE = timezone("Asia/Bishkek")

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    due_date: datetime
    status: TaskStatus = TaskStatus.new

    @field_validator("due_date")
    def validate_due_date(cls, value):
        now = datetime.now(KG_TIMEZONE)
        if value.tzinfo is None:
            value = KG_TIMEZONE.localize(value)
        if value < now:
            raise ValueError("Due date cannot be in the past")
        return value


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    due_date: Optional[datetime] = None
    status: Optional[TaskStatus] = None

    @field_validator("due_date")
    def validate_due_date(cls, value):
        if value is None:
            return value
        now = datetime.now(KG_TIMEZONE)
        if value.tzinfo is None:
            value = KG_TIMEZONE.localize(value)
        if value < now:
            raise ValueError("Due date cannot be in the past")
        return value


class TaskResponse(TaskBase):
    id: int
    due_date: datetime
    created_at: datetime

    @field_validator("due_date", "created_at", mode="before")
    def add_timezone(cls, value):
        if value and value.tzinfo is None:
            return KG_TIMEZONE.localize(value)
        return value

    model_config = {"from_attributes": True}


class TaskHistoryResponse(BaseModel):
    id: int
    task_id: int
    title: str
    description: Optional[str]
    due_date: datetime
    status: TaskStatus
    change_type: str
    changed_at: datetime

    @field_validator("due_date", "changed_at", mode="before")
    def add_timezone(cls, value):
        if value and value.tzinfo is None:
            return KG_TIMEZONE.localize(value)
        return value

    model_config = {"from_attributes": True}
