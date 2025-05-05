from sqlalchemy import Column, String, UUID, ForeignKey, DECIMAL, Integer, DateTime, Enum, Text, TIMESTAMP, Boolean
from sqlalchemy.sql import func
import enum
import uuid
from db import Base

# Enum Types
class AccreditationStatus(enum.Enum):
    pending = "pending"
    approved = "approved"
    revoked = "revoked"

class BookingStatus(enum.Enum):
    requested = "requested"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"
    rebooking = "rebooking"

class PaymentStatus(enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"

class PaymentMethod(enum.Enum):
    card = "card"
    paypal = "paypal"
    bank_transfer = "bank_transfer"
    other = "other"

# Model classes
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email_id = Column(String(255), nullable=False, unique=True)
    mobile = Column(String(20))
    two_factor_auth = Column(Boolean, default=False)

class Clinic(Base):
    __tablename__ = "clinics"
    
    clinic_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    clinic_name = Column(String(100), nullable=False)
    location_city = Column(String(50))
    location_country = Column(String(50))
    email_id = Column(String(255), unique=True)
    mobile = Column(String(20))
    address = Column(String(250))
    two_factor_auth = Column(Boolean, default=False)
    accreditation_status = Column(Enum(AccreditationStatus))

class Service(Base):
    __tablename__ = "services"
    
    service_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    clinic_id = Column(UUID, ForeignKey("clinics.clinic_id", ondelete="CASCADE"), nullable=False)
    service_name = Column(String(100), nullable=False)
    pricestart = Column(DECIMAL(10, 2), nullable=False)
    priceend = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(5), nullable=False, default="USD")
    description = Column(String(255))
    about = Column(String(255))

class Doctor(Base):
    __tablename__ = "doctors"
    
    doctor_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    clinic_id = Column(UUID, ForeignKey("clinics.clinic_id", ondelete="CASCADE"), nullable=False)
    service_id = Column(UUID, ForeignKey("services.service_id", ondelete="CASCADE"), nullable=False)
    doctor_name = Column(String(100), nullable=False)
    qualification = Column(String(100), nullable=False)
    years_of_experience = Column(Integer, default=0)
    specialization = Column(String(100))

class Booking(Base):
    __tablename__ = "bookings"
    
    booking_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    clinic_id = Column(UUID, ForeignKey("clinics.clinic_id", ondelete="CASCADE"), nullable=False)
    service_id = Column(UUID, ForeignKey("services.service_id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(UUID, ForeignKey("doctors.doctor_id"))
    appointment_start = Column(DateTime, nullable=False)
    appointment_end = Column(DateTime, nullable=False)
    booking_status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.requested)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()) 