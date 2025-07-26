from __future__ import annotations

from datetime import datetime, timedelta, date
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..models.crop import Crop
from ..models.todo import TodoTask
from ..models.user import User
from ..schemas.todo import TodoCreate, TodoResponse, TodoUpdate
from ..utils.auth import get_current_user

router = APIRouter(prefix="/todos", tags=["todos"])


def calculate_next_due_date(
    current_date: Optional[date], pattern: str, interval: int
) -> date:
    """Calculate when the next recurring task should be created."""
    if not current_date:
        current_date = date.today()

    if pattern == "daily":
        return current_date + timedelta(days=interval)
    elif pattern == "weekly":
        return current_date + timedelta(weeks=interval)
    elif pattern == "monthly":
        # Simple monthly calculation
        next_month = current_date.month + interval
        year = current_date.year + (next_month - 1) // 12
        month = ((next_month - 1) % 12) + 1
        return date(year, month, min(current_date.day, 28))  # Avoid month-end issues
    else:
        return current_date + timedelta(days=1)


def create_recurring_instance(template: TodoTask, db: Session) -> None:
    """Create a new instance of a recurring task."""
    instance = TodoTask(
        user_id=template.user_id,
        crop_id=template.crop_id,
        task_title=template.task_title,
        task_description=template.task_description,
        priority=template.priority,
        due_date=template.due_date,
        is_system_generated=True,
        parent_todo_id=template.id,
        is_recurring=False,  # Instances are not recurring themselves
        is_template=False,
    )
    db.add(instance)
    db.commit()


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    todo_data: TodoCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TodoTask:
    """Create a new TODO task."""
    # Verify crop ownership if crop_id is provided
    if todo_data.crop_id:
        crop = (
            db.query(Crop)
            .filter(Crop.id == todo_data.crop_id, Crop.user_id == current_user.id)
            .first()
        )
        if not crop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found"
            )

    # Create the main TODO
    db_todo = TodoTask(user_id=current_user.id, **todo_data.model_dump())

    if todo_data.is_recurring:
        db_todo.is_template = True
        db_todo.next_due_date = calculate_next_due_date(
            todo_data.due_date,
            todo_data.recurrence_pattern or "daily",
            todo_data.recurrence_interval,
        )

    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)

    # If recurring, create first instance
    if todo_data.is_recurring:
        create_recurring_instance(db_todo, db)

    return db_todo


@router.get("/", response_model=List[TodoResponse])
def get_user_todos(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    status_filter: Optional[str] = None,
    crop_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[TodoTask]:
    """Get all TODO tasks for the current user."""
    query = db.query(TodoTask).filter(TodoTask.user_id == current_user.id)

    if status_filter:
        query = query.filter(TodoTask.status == status_filter)

    if crop_id:
        query = query.filter(TodoTask.crop_id == crop_id)

    return query.order_by(TodoTask.due_date).offset(skip).limit(limit).all()


@router.get("/active", response_model=List[TodoResponse])
def get_active_todos(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> List[TodoTask]:
    """Get only active TODO instances (not templates)."""
    return (
        db.query(TodoTask)
        .filter(
            TodoTask.user_id == current_user.id,
            TodoTask.status == "pending",
            TodoTask.is_template == False,  # Only get instances, not templates
        )
        .order_by(TodoTask.due_date)
        .all()
    )


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(
    todo_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TodoTask:
    """Get a specific TODO task."""
    todo = (
        db.query(TodoTask)
        .filter(TodoTask.id == todo_id, TodoTask.user_id == current_user.id)
        .first()
    )

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="TODO task not found"
        )

    return todo


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TodoTask:
    """Update a TODO task."""
    todo = (
        db.query(TodoTask)
        .filter(TodoTask.id == todo_id, TodoTask.user_id == current_user.id)
        .first()
    )

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="TODO task not found"
        )

    # Update todo with provided data
    update_data = todo_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo, field, value)

    db.commit()
    db.refresh(todo)

    return todo


@router.put("/{todo_id}/complete", response_model=TodoResponse)
def complete_todo(
    todo_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TodoTask:
    """Mark a TODO task as completed."""
    todo = (
        db.query(TodoTask)
        .filter(TodoTask.id == todo_id, TodoTask.user_id == current_user.id)
        .first()
    )

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="TODO task not found"
        )

    todo.status = "completed"
    todo.completed_at = datetime.utcnow()

    # If this was from a recurring template, check if we need to create next instance
    if todo.parent_todo_id:
        template = db.query(TodoTask).filter(TodoTask.id == todo.parent_todo_id).first()
        if template and template.is_recurring:
            # Update template's next due date
            template.next_due_date = calculate_next_due_date(
                todo.due_date,
                template.recurrence_pattern or "daily",
                template.recurrence_interval,
            )

    db.commit()
    db.refresh(todo)

    return todo


@router.delete("/{todo_id}")
def delete_todo(
    todo_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    """Delete a TODO task."""
    todo = (
        db.query(TodoTask)
        .filter(TodoTask.id == todo_id, TodoTask.user_id == current_user.id)
        .first()
    )

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="TODO task not found"
        )

    db.delete(todo)
    db.commit()

    return {"message": "TODO task deleted successfully"}


@router.post("/generate-recurring")
def generate_recurring_todos(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    """Manually trigger creation of pending recurring TODOs."""
    today = date.today()

    # Find all recurring templates that need new instances
    recurring_templates = (
        db.query(TodoTask)
        .filter(
            TodoTask.user_id == current_user.id,
            TodoTask.is_template == True,
            TodoTask.is_recurring == True,
            TodoTask.next_due_date <= today,
        )
        .all()
    )

    for template in recurring_templates:
        # Create new instance
        create_recurring_instance(template, db)

        # Update next due date
        template.next_due_date = calculate_next_due_date(
            template.next_due_date,
            template.recurrence_pattern or "daily",
            template.recurrence_interval,
        )

    db.commit()

    return {"message": f"Generated {len(recurring_templates)} recurring TODOs"}
