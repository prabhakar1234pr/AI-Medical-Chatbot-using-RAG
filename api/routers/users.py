from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ..db import get_db
from ..models import User
from ..schemas import UserCreate, UserDB, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=UserDB, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user in the database.
    """
    # Check if user with this email already exists
    existing_user = db.query(User).filter(User.email_id == user.email_id).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new user
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email_id=user.email_id,
        mobile=user.mobile,
        two_factor_auth=False  # Default value
    )
    
    # Add to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/{user_id}", response_model=UserDB)
async def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Get user details by ID.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=UserDB)
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user details.
    """
    # Find the user
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields if provided
    user_data = user_update.dict(exclude_unset=True)
    for key, value in user_data.items():
        if value is not None:
            setattr(db_user, key, value)
    
    # Commit changes
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/by-name/{first_name}/{last_name}", response_model=List[UserDB])
async def find_user_by_name(
    first_name: str,
    last_name: str,
    db: Session = Depends(get_db)
):
    """
    Find users by first and last name.
    """
    users = db.query(User).filter(
        User.first_name.ilike(f"%{first_name}%"),
        User.last_name.ilike(f"%{last_name}%")
    ).all()
    
    return users 