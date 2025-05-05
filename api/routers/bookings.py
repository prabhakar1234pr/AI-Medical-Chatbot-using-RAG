from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import timedelta

from ..db import get_db
from ..models import Booking, BookingStatus
from ..schemas import BookingCreate, BookingDB

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=BookingDB, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new booking with status 'requested'.
    Sets appointment_end to 1 hour after appointment_start.
    """
    # Create appointment end time (1 hour after start)
    appointment_start = booking.appointment_startdate
    appointment_end = appointment_start + timedelta(hours=1)
    
    # Create new booking object
    db_booking = Booking(
        user_id=booking.user_id,
        clinic_id=booking.clinic_id,
        service_id=booking.service_id,
        doctor_id=booking.doctor_id,
        appointment_start=appointment_start,
        appointment_end=appointment_end,
        booking_status=BookingStatus.requested
    )
    
    # Add to database
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    return db_booking

@router.get("/{user_id}", response_model=List[BookingDB])
async def get_user_bookings(
    user_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Get all bookings for a specific user.
    """
    bookings = db.query(Booking).filter(Booking.user_id == user_id).all()
    return bookings

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking(
    booking_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Cancel a booking by setting status to 'cancelled'.
    """
    # Find the booking
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Update status to cancelled
    booking.booking_status = BookingStatus.cancelled
    
    # Commit changes
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT) 