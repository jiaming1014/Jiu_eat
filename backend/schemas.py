from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class MemberRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str = Field(min_length=1, max_length=100)
    city: str = ""
    interests: str = ""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class MemberUpdate(BaseModel):
    display_name: str = Field(min_length=1, max_length=100)
    city: str = ""
    interests: str = ""
    bio: str = ""


class Member(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    display_name: str
    city: str
    interests: str
    bio: str
    created_at: datetime


class LoginResponse(BaseModel):
    member_id: int
    display_name: str


class ActivityCreate(BaseModel):
    organizer_id: int
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    category: str
    city: str
    location_name: str
    activity_date: datetime
    deadline: datetime
    max_participants: int = Field(gt=0)
    image_url: str = ""


class ActivityUpdate(ActivityCreate):
    pass


class Activity(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    organizer_id: int
    organizer_name: str = ""
    title: str
    description: str
    category: str
    city: str
    location_name: str
    activity_date: datetime
    deadline: datetime
    max_participants: int
    approved_count: int = 0
    image_url: str
    status: str
    created_at: datetime


class ApplicationCreate(BaseModel):
    member_id: int
    message: str = ""


class Application(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activity_id: int
    member_id: int
    member_name: str = ""
    activity_title: str = ""
    message: str
    status: str
    created_at: datetime


class Recommendation(Activity):
    score: int
    reasons: list[str]
