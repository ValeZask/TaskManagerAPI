import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import pytz
from typing import Generator

from app.main import app
from app.database import Base, get_db
from app.models import TaskStatus
from app.config import AUTH_TOKEN

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

KG_TIMEZONE = pytz.timezone("Asia/Bishkek")

def override_get_db() -> Generator:
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers():
    return {"Authorization": f"Bearer {AUTH_TOKEN}"}

@pytest.fixture
def future_datetime():
    return KG_TIMEZONE.localize(datetime.now() + timedelta(days=1))

@pytest.fixture
def task_data(future_datetime):
    return {
        "title": "Test Task",
        "description": "Test Description",
        "due_date": future_datetime.isoformat(),
        "status": "new"
    }

@pytest.fixture
def created_task(auth_headers, task_data):
    response = client.post("/api/tasks/", headers=auth_headers, json=task_data)
    assert response.status_code == 200
    return response.json()

def test_create_task(auth_headers, task_data):
    response = client.post("/api/tasks/", headers=auth_headers, json=task_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["status"] == task_data["status"]
    assert "id" in data

def test_create_task_validation_error(auth_headers, task_data):
    invalid_data = task_data.copy()
    invalid_data["title"] = ""
    response = client.post("/api/tasks/", headers=auth_headers, json=invalid_data)
    assert response.status_code == 422

    invalid_data = task_data.copy()
    past_date = KG_TIMEZONE.localize(datetime.now() - timedelta(days=1))
    invalid_data["due_date"] = past_date.isoformat()
    response = client.post("/api/tasks/", headers=auth_headers, json=invalid_data)
    assert response.status_code == 422

def test_create_duplicate_task(auth_headers, task_data):
    response = client.post("/api/tasks/", headers=auth_headers, json=task_data)
    assert response.status_code == 200

    response = client.post("/api/tasks/", headers=auth_headers, json=task_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_get_task(auth_headers, created_task):
    task_id = created_task["id"]
    response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == created_task["title"]

def test_get_nonexistent_task(auth_headers):
    response = client.get("/api/tasks/999", headers=auth_headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_get_tasks(auth_headers, created_task):
    response = client.get("/api/tasks/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == created_task["title"]

def test_get_tasks_filtered_by_status(auth_headers, task_data, future_datetime):
    client.post("/api/tasks/", headers=auth_headers, json=task_data)

    in_progress_task = task_data.copy()
    in_progress_task["title"] = "Task In Progress"
    in_progress_task["status"] = "in_progress"
    client.post("/api/tasks/", headers=auth_headers, json=in_progress_task)

    response = client.get("/api/tasks/?status=new", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "new"

    response = client.get("/api/tasks/?status=in_progress", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "in_progress"

def test_get_tasks_filtered_by_due_date(auth_headers, task_data, future_datetime):
    client.post("/api/tasks/", headers=auth_headers, json=task_data)

    tomorrow_plus_one = KG_TIMEZONE.localize(datetime.now() + timedelta(days=2))
    next_day_task = task_data.copy()
    next_day_task["title"] = "Task for Next Day"
    next_day_task["due_date"] = tomorrow_plus_one.isoformat()
    client.post("/api/tasks/", headers=auth_headers, json=next_day_task)

    due_date = future_datetime.date().isoformat()
    response = client.get(f"/api/tasks/?due_date={due_date}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

def test_update_task(auth_headers, created_task):
    task_id = created_task["id"]
    update_data = {
        "title": "Updated Task",
        "status": "in_progress"
    }
    response = client.put(f"/api/tasks/{task_id}", headers=auth_headers, json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["status"] == update_data["status"]
    assert data["description"] == created_task["description"]

def test_update_task_validation_error(auth_headers, created_task):
    task_id = created_task["id"]
    invalid_data = {"title": ""}
    response = client.put(f"/api/tasks/{task_id}", headers=auth_headers, json=invalid_data)
    assert response.status_code == 422

    past_date = KG_TIMEZONE.localize(datetime.now() - timedelta(days=1))
    invalid_data = {"due_date": past_date.isoformat()}
    response = client.put(f"/api/tasks/{task_id}", headers=auth_headers, json=invalid_data)
    assert response.status_code == 422

def test_update_nonexistent_task(auth_headers):
    update_data = {"title": "Updated Task"}
    response = client.put("/api/tasks/999", headers=auth_headers, json=update_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_delete_task(auth_headers, created_task):
    task_id = created_task["id"]
    response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 404

def test_delete_nonexistent_task(auth_headers):
    response = client.delete("/api/tasks/999", headers=auth_headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_get_task_history(auth_headers, created_task):
    task_id = created_task["id"]
    update_data = {"title": "Updated Task", "status": "in_progress"}
    client.put(f"/api/tasks/{task_id}", headers=auth_headers, json=update_data)
    response = client.get(f"/api/tasks/{task_id}/history", headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 2
    assert history[0]["change_type"] == "created"
    assert "updated_title_status" in history[1]["change_type"]

def test_get_history_nonexistent_task(auth_headers):
    response = client.get("/api/tasks/999/history", headers=auth_headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_authentication_required(future_datetime):
    response = client.get("/api/tasks/9999")
    assert response.status_code == 401
    assert "Invalid or missing token" in response.json()["detail"]

    response = client.get("/api/tasks/9999", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
    assert "Invalid or missing token" in response.json()["detail"]

    minimal_task_data = {
        "title": "Auth Test",
        "due_date": future_datetime.isoformat()
    }
    response = client.post("/api/tasks/", json=minimal_task_data, headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
    assert "Invalid or missing token" in response.json()["detail"]
