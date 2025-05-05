from pydantic import BaseModel, UUID4, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enum Types
class BookingStatus(str, Enum):
    requested = "requested"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"
    rebooking = "rebooking"

# User Schemas
class UserBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email_id: EmailStr
    mobile: Optional[str] = None

class UserCreate(UserBase):
    email_id: EmailStr

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mobile: Optional[str] = None
    two_factor_auth: Optional[bool] = None

class UserDB(UserBase):
    user_id: UUID4
    two_factor_auth: bool = False
    
    class Config:
        orm_mode = True

# Clinic Schemas
class ClinicBase(BaseModel):
    clinic_name: str
    location_city: Optional[str] = None
    location_country: Optional[str] = None

class ClinicDB(ClinicBase):
    clinic_id: UUID4
    
    class Config:
        orm_mode = True

# Service Schemas
class ServiceBase(BaseModel):
    service_name: str
    pricestart: float
    priceend: float
    currency: str = "USD"
    description: Optional[str] = None

class ServiceDB(ServiceBase):
    service_id: UUID4
    clinic_id: UUID4
    
    class Config:
        orm_mode = True

# Doctor Schemas
class DoctorBase(BaseModel):
    doctor_name: str
    qualification: str
    years_of_experience: Optional[int] = 0
    specialization: Optional[str] = None

class DoctorDB(DoctorBase):
    doctor_id: UUID4
    clinic_id: UUID4
    service_id: UUID4
    
    class Config:
        orm_mode = True

# Booking Schemas
class BookingCreate(BaseModel):
    user_id: UUID4
    clinic_id: UUID4
    service_id: UUID4
    doctor_id: Optional[UUID4] = None
    appointment_startdate: datetime

class BookingDB(BaseModel):
    booking_id: UUID4
    user_id: UUID4
    clinic_id: UUID4
    service_id: UUID4
    doctor_id: Optional[UUID4] = None
    appointment_start: datetime
    appointment_end: datetime
    booking_status: BookingStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Combined Search Result Schema
class ClinicSearchResult(BaseModel):
    clinic: ClinicDB
    service: ServiceDB
    
    class Config:
        orm_mode = True 