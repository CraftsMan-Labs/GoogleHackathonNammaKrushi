from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..config.database import Base


class TodoTask(Base):
    """TODO tasks for farm management."""
    
    __tablename__ = "todo_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)  # NULL for general tasks
    
    # Task Details
    task_title = Column(String, nullable=False)
    task_description = Column(Text)
    priority = Column(String, default="medium")  # high, medium, low
    status = Column(String, default="pending")  # pending, in_progress, completed, cancelled
    due_date = Column(Date)
    
    # System Generated
    is_system_generated = Column(Boolean, default=False)
    weather_triggered = Column(Boolean, default=False)
    ai_generated = Column(Boolean, default=False)
    
    # Recurring Support
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String)  # daily, weekly, monthly, seasonal
    recurrence_interval = Column(Integer, default=1)  # every X days/weeks/months
    parent_todo_id = Column(Integer, ForeignKey("todo_tasks.id"), nullable=True)
    next_due_date = Column(Date)  # When to create next instance
    is_template = Column(Boolean, default=False)  # Original recurring template
    
    # Completion
    completed_at = Column(DateTime)
    completion_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="todos")
    farm = relationship("Farm", back_populates="todos")
    recurring_instances = relationship("TodoTask", cascade="all, delete-orphan")