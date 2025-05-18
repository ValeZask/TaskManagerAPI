from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from . import crud, schemas, auth
from .database import get_db
from .models import TaskStatus
from datetime import date

router = APIRouter()

@router.post("/tasks/", response_model=schemas.TaskResponse)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), token = Depends(auth.verify_token)):
    return crud.create_task(db, task)

@router.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db), token = Depends(auth.verify_token)):
    return crud.get_task(db, task_id)

@router.get("/tasks/", response_model=List[schemas.TaskResponse])
def get_tasks(status: Optional[TaskStatus] = None, due_date: Optional[date] = None, db: Session = Depends(get_db), token = Depends(auth.verify_token)):
    return crud.get_tasks(db, status, due_date)

@router.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db), token = Depends(auth.verify_token)):
    return crud.update_task(db, task_id, task)

@router.delete("/tasks/{task_id}", response_model=schemas.TaskResponse)
def delete_task(task_id: int, db: Session = Depends(get_db), token = Depends(auth.verify_token)):
    return crud.delete_task(db, task_id)

@router.get("/tasks/{task_id}/history", response_model=List[schemas.TaskHistoryResponse])
def get_task_history(task_id: int, db: Session = Depends(get_db), token = Depends(auth.verify_token)):
    return crud.get_task_history(db, task_id)
