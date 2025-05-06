"""
Connector module to help the LangChain agent interact with the database API.
These functions can be used as tools in your LangChain agent.
"""

import requests
import json
from typing import List, Dict, Any, Optional
import uuid

# Base URL for the API
BASE_URL = "http://localhost:8092"  # Make sure this includes http://

# ------------------ USER MANAGEMENT ------------------

def create_user(first_name: str, last_name: str, email_id: str, mobile: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new user in the database.
    
    Args:
        first_name: User's first name
        last_name: User's last name
        email_id: User's email address
        mobile: Optional mobile number
        
    Returns:
        Created user details or error
    """
    user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email_id": email_id
    }
    
    if mobile:
        user_data["mobile"] = mobile
    
    # Make API request
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    
    if response.status_code == 201:
        return response.json()
    else:
        return {"error": f"Failed to create user: {response.text}"}

def find_user_by_name(first_name: str, last_name: str) -> List[Dict[str, Any]]:
    """
    Find users by first and last name.
    
    Args:
        first_name: User's first name
        last_name: User's last name
        
    Returns:
        List of matching users or error
    """
    # Make API request
    response = requests.get(f"{BASE_URL}/users/by-name/{first_name}/{last_name}")
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to find user: {response.text}"}

def get_user(user_id: str) -> Dict[str, Any]:
    """
    Get user details by ID.
    
    Args:
        user_id: UUID of the user
        
    Returns:
        User details or error
    """
    # Make API request
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to get user: {response.text}"}

def update_user(user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update user details.
    
    Args:
        user_id: UUID of the user
        update_data: Dictionary with fields to update
        
    Returns:
        Updated user details or error
    """
    # Make API request
    response = requests.put(f"{BASE_URL}/users/{user_id}", json=update_data)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to update user: {response.text}"}

# ------------------ CLINIC SEARCH ------------------

def search_clinics(
    location_city: Optional[str] = None,
    procedure_name: Optional[str] = None,
    max_price: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Search for clinics based on location, procedure, and price.
    
    Args:
        location_city: City to search in
        procedure_name: Name of dental procedure
        max_price: Maximum price for the procedure
        
    Returns:
        List of matching clinics with their services
    """
    # Build query parameters
    params = {}
    if location_city:
        params["location_city"] = location_city
    if procedure_name:
        params["procedure_name"] = procedure_name
    if max_price is not None:
        params["max_price"] = max_price
    
    # Make API request
    response = requests.get(f"{BASE_URL}/clinics/search", params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to search clinics: {response.text}"}

# ------------------ BOOKING MANAGEMENT ------------------

def create_booking(
    user_id: str,
    clinic_id: str,
    service_id: str,
    doctor_id: Optional[str] = None,
    appointment_startdate: str = None
) -> Dict[str, Any]:
    """
    Create a booking appointment.
    
    Args:
        user_id: UUID of the user
        clinic_id: UUID of the clinic
        service_id: UUID of the service
        doctor_id: Optional UUID of the doctor
        appointment_startdate: Start time for appointment in ISO format
        
    Returns:
        Created booking details or error
    """
    booking_data = {
        "user_id": user_id,
        "clinic_id": clinic_id,
        "service_id": service_id,
        "appointment_startdate": appointment_startdate
    }
    
    if doctor_id:
        booking_data["doctor_id"] = doctor_id
    
    # Make API request
    response = requests.post(f"{BASE_URL}/bookings/", json=booking_data)
    
    if response.status_code == 201:
        return response.json()
    else:
        return {"error": f"Failed to create booking: {response.text}"}

def get_user_bookings(user_id: str) -> List[Dict[str, Any]]:
    """
    Get all bookings for a user.
    
    Args:
        user_id: UUID of the user
        
    Returns:
        List of bookings for the user
    """
    # Make API request
    response = requests.get(f"{BASE_URL}/bookings/{user_id}")
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to get bookings: {response.text}"}

def cancel_booking(booking_id: str) -> Dict[str, Any]:
    """
    Cancel a booking.
    
    Args:
        booking_id: UUID of the booking to cancel
        
    Returns:
        Success message or error
    """
    # Make API request
    response = requests.delete(f"{BASE_URL}/bookings/{booking_id}")
    
    if response.status_code == 204:
        return {"success": True, "message": "Booking cancelled successfully"}
    else:
        return {"error": f"Failed to cancel booking: {response.text}"} 