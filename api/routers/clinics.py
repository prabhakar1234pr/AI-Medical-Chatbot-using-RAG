from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import uuid

from ..db import get_db
from ..models import Clinic, Service
from ..schemas import ClinicSearchResult, ClinicDB, ServiceDB

router = APIRouter(
    prefix="/clinics",
    tags=["clinics"],
    responses={404: {"description": "Not found"}}
)

@router.get("/search", response_model=List[ClinicSearchResult])
async def search_clinics(
    location_city: Optional[str] = Query(None, description="Filter by city"),
    procedure_name: Optional[str] = Query(None, description="Filter by procedure/service name"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    db: Session = Depends(get_db)
):
    """
    Search for clinics based on location, procedure, and price range.
    Returns up to 5 matches joining clinics and services tables.
    """
    query = db.query(Clinic, Service).join(Service, Clinic.clinic_id == Service.clinic_id)
    
    # Apply filters if provided
    if location_city:
        query = query.filter(Clinic.location_city.ilike(f"%{location_city}%"))
    
    if procedure_name:
        query = query.filter(Service.service_name.ilike(f"%{procedure_name}%"))
    
    if max_price is not None:
        query = query.filter(Service.pricestart <= max_price)
    
    # Limit to 5 results
    results = query.limit(5).all()
    
    # Format results
    formatted_results = []
    for clinic, service in results:
        formatted_results.append(
            ClinicSearchResult(
                clinic=clinic,
                service=service
            )
        )
    
    return formatted_results 