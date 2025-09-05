from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime, time
from enum import Enum
import uuid

class UserRole(str, Enum):
    CLIENT = "client"
    ADMIN = "admin"

class AppointmentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

# User Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password_hash: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.CLIENT
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime

# Slot Models (Time slots that admin creates)
class TimeSlot(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: datetime
    start_time: str  # Changed from time to str
    end_time: str    # Changed from time to str
    service_name: str
    service_duration: int  # minutes
    price: float
    is_available: bool = True
    created_by: str  # admin user id
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TimeSlotCreate(BaseModel):
    date: datetime
    start_time: str  # Changed from time to str
    end_time: str    # Changed from time to str
    service_name: str
    service_duration: int
    price: float

class TimeSlotResponse(BaseModel):
    id: str
    date: datetime
    start_time: str  # Changed from time to str
    end_time: str    # Changed from time to str
    service_name: str
    service_duration: int
    price: float
    is_available: bool
    created_at: datetime

# Appointment Models
class Appointment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    slot_id: str
    status: AppointmentStatus = AppointmentStatus.PENDING
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AppointmentCreate(BaseModel):
    slot_id: str
    notes: Optional[str] = None

class AppointmentUpdate(BaseModel):
    status: AppointmentStatus
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: str
    user_id: str
    slot_id: str
    status: AppointmentStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    # Populated fields
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    slot_info: Optional[TimeSlotResponse] = None

# Review Models
class Review(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str
    status: ReviewStatus = ReviewStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str

class ReviewUpdate(BaseModel):
    status: ReviewStatus

class ReviewResponse(BaseModel):
    id: str
    user_id: str
    rating: int
    comment: str
    status: ReviewStatus
    created_at: datetime
    # Populated fields
    user_name: Optional[str] = None

# JWT Token Models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

# Status Check (keeping existing)
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str