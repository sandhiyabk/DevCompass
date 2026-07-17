# database/models.py

import uuid
from datetime import date, datetime
from sqlalchemy import (
    Column, String, Integer, Boolean,
    Date, DateTime, ForeignKey, Text,
    Float, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    company_name = Column(String(100))
    company_type = Column(String(50))  # service/product/startup
    role = Column(String(100))
    tech_stack_at_work = Column(ARRAY(String))
    personal_goal = Column(String(200))
    joined_company_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    skills = relationship("UserSkill", back_populates="user")
    tasks = relationship("DailyTask", back_populates="user")
    stuck_sessions = relationship(
        "StuckSession", back_populates="user"
    )
    reflections = relationship(
        "Reflection", back_populates="user"
    )
    knowledge_items = relationship(
        "KnowledgeBase", back_populates="user"
    )
    weekly_reports = relationship(
        "WeeklyReport", back_populates="user"
    )

    @property
    def days_at_company(self):
        if self.joined_company_date:
            return (date.today() - self.joined_company_date).days
        return 0


class UserSkill(Base):
    __tablename__ = "user_skills"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    skill_name = Column(String(100), nullable=False)
    proficiency = Column(Integer, default=1)  # 1-5
    source = Column(String(50), default="self-rated")
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="skills")


class DailyTask(Base):
    __tablename__ = "daily_tasks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    task_input = Column(Text, nullable=False)
    task_date = Column(Date, default=date.today)

    # AI generated fields
    what_is_this = Column(Text)
    skills_needed = Column(ARRAY(String))
    skill_gaps = Column(ARRAY(String))
    skills_they_have = Column(ARRAY(String))
    reading_order = Column(ARRAY(String))
    before_touching_code = Column(ARRAY(String))
    estimated_hours = Column(Integer)
    what_youll_learn = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tasks")
    stuck_sessions = relationship(
        "StuckSession", back_populates="task"
    )


class StuckSession(Base):
    __tablename__ = "stuck_sessions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("daily_tasks.id"),
        nullable=True
    )
    time_stuck_minutes = Column(Integer)
    approaches_tried = Column(Text)
    next_idea = Column(Text)
    ai_decision = Column(String(50))  # ask_senior/keep_trying
    ai_reasoning = Column(Text)
    how_to_ask = Column(Text)
    next_step = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="stuck_sessions")
    task = relationship(
        "DailyTask", back_populates="stuck_sessions"
    )


class Reflection(Base):
    __tablename__ = "reflections"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    reflection_date = Column(Date, default=date.today)
    task_worked_on = Column(Text)
    what_confused = Column(Text)
    new_concept = Column(Text)
    confidence_score = Column(Integer)  # 1-5
    ai_summary = Column(Text)
    concepts_learned = Column(ARRAY(String))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reflections")


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    concept = Column(String(200), nullable=False)
    learned_from = Column(String(100))
    confidence = Column(Integer, default=3)  # 1-5
    times_reviewed = Column(Integer, default=0)
    last_revised = Column(Date, default=date.today)
    next_revision = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship(
        "User", back_populates="knowledge_items"
    )


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    week_start = Column(Date)
    week_end = Column(Date)
    tasks_completed = Column(Integer, default=0)
    reflections_count = Column(Integer, default=0)
    stuck_sessions_count = Column(Integer, default=0)
    skills_grown = Column(ARRAY(String))
    ai_report = Column(Text)
    growth_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="weekly_reports")