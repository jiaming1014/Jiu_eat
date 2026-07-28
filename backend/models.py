from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=False)
    city = Column(String(100), default="")
    interests = Column(String(255), default="")
    bio = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    activities = relationship("Activity", back_populates="organizer")
    applications = relationship("Application", back_populates="member")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    organizer_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    category = Column(String(50), nullable=False)
    city = Column(String(100), nullable=False)
    location_name = Column(String(200), nullable=False)
    activity_date = Column(DateTime, nullable=False)
    deadline = Column(DateTime, nullable=False)
    max_participants = Column(Integer, nullable=False)
    image_url = Column(String(500), default="")
    status = Column(String(20), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)

    organizer = relationship("Member", back_populates="activities")
    applications = relationship("Application", back_populates="activity", cascade="all, delete-orphan")


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("activity_id", "member_id", name="uq_activity_member"),)

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    message = Column(Text, default="")
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    activity = relationship("Activity", back_populates="applications")
    member = relationship("Member", back_populates="applications")
