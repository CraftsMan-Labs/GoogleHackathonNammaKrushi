from __future__ import annotations

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    """Schema for creating a TODO task."""
    task_title: str = Field(..., min_length=3, max_length=200)
    task_description: Optional[str] = Field(None, max_length=1000)
    priority: str = Field(default="medium", pattern="^(high|medium|low)$")
    due_date: Optional[date] = None
    farm_id: Optional[int] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = Field(None, pattern="^(daily|weekly|monthly|seasonal)$")
    recurrence_interval: int = Field(default=1, ge=1, le=365)


class TodoUpdate(BaseModel):
    """Schema for updating a TODO task."""
    task_title: Optional[str] = Field(None, min_length=3, max_length=200)
    task_description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed|cancelled)$")
    due_date: Optional[date] = None
    completion_notes: Optional[str] = Field(None, max_length=500)


class TodoResponse(BaseModel):
    """Schema for TODO task response."""
    id: int
    user_id: int
    farm_id: Optional[int]
    task_title: str
    task_description: Optional[str]
    priority: str
    status: str
    due_date: Optional[date]
    is_system_generated: bool
    weather_triggered: bool
    ai_generated: bool
    is_recurring: bool
    recurrence_pattern: Optional[str]
    recurrence_interval: int
    parent_todo_id: Optional[int]
    next_due_date: Optional[date]
    is_template: bool
    completed_at: Optional[datetime]
    completion_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True