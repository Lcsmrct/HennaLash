from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.cors import CORSMiddleware
from datetime import timedelta
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# Local imports
from models import *
from auth import *
from database import get_database, create_indexes, close_db_connection
from email_service import email_service

ROOT_DIR = Path(__file__).parent

# Create the main app without a prefix
app = FastAPI(title="Salon Booking API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Dependency to get database
async def get_db():
    return await get_database()

# Dependency to get current user with database
async def get_current_user_with_db(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
) -> User:
    return await get_current_user(credentials, db)

# Dependency to get current active user
async def get_current_active_user_with_db(
    current_user: User = Depends(get_current_user_with_db)
) -> User:
    return await get_current_active_user(current_user)

# Dependency to get current admin user
async def get_current_admin_user_with_db(
    current_user: User = Depends(get_current_active_user_with_db)
) -> User:
    return await get_current_admin_user(current_user)

# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@api_router.post("/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        role=UserRole.ADMIN if user_data.email == "admin@salon.com" else UserRole.CLIENT
    )
    
    await db.users.insert_one(user.dict())
    return UserResponse(**user.dict())

@api_router.post("/auth/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = await authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user_with_db)):
    """Get current user information."""
    return UserResponse(**current_user.dict())

# ==========================================
# TIME SLOTS ROUTES (Admin only)
# ==========================================

@api_router.post("/slots", response_model=TimeSlotResponse)
async def create_time_slot(
    slot_data: TimeSlotCreate,
    current_user: User = Depends(get_current_admin_user_with_db),
    db = Depends(get_db)
):
    """Create a new time slot (Admin only)."""
    time_slot = TimeSlot(
        **slot_data.dict(),
        created_by=current_user.id
    )
    await db.time_slots.insert_one(time_slot.dict())
    return TimeSlotResponse(**time_slot.dict())

@api_router.get("/slots", response_model=List[TimeSlotResponse])
async def get_time_slots(
    available_only: bool = False,
    db = Depends(get_db)
):
    """Get all time slots."""
    query = {}
    if available_only:
        query["is_available"] = True
    
    slots = await db.time_slots.find(query).sort("date", 1).to_list(1000)
    return [TimeSlotResponse(**slot) for slot in slots]

@api_router.put("/slots/{slot_id}", response_model=TimeSlotResponse)
async def update_time_slot_availability(
    slot_id: str,
    is_available: bool,
    current_user: User = Depends(get_current_admin_user_with_db),
    db = Depends(get_db)
):
    """Update time slot availability (Admin only)."""
    result = await db.time_slots.update_one(
        {"id": slot_id},
        {"$set": {"is_available": is_available}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Time slot not found")
    
    slot = await db.time_slots.find_one({"id": slot_id})
    return TimeSlotResponse(**slot)

@api_router.delete("/slots/{slot_id}")
async def delete_time_slot(
    slot_id: str,
    current_user: User = Depends(get_current_admin_user_with_db),
    db = Depends(get_db)
):
    """Delete a time slot (Admin only)."""
    result = await db.time_slots.delete_one({"id": slot_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Time slot not found")
    return {"message": "Time slot deleted successfully"}

# ==========================================
# APPOINTMENTS ROUTES
# ==========================================

@api_router.post("/appointments", response_model=AppointmentResponse)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: User = Depends(get_current_active_user_with_db),
    db = Depends(get_db)
):
    """Create a new appointment."""
    # Check if slot exists and is available
    slot = await db.time_slots.find_one({"id": appointment_data.slot_id, "is_available": True})
    if not slot:
        raise HTTPException(status_code=404, detail="Time slot not found or not available")
    
    # Check if user already has appointment for this slot
    existing = await db.appointments.find_one({
        "user_id": current_user.id,
        "slot_id": appointment_data.slot_id,
        "status": {"$in": ["pending", "confirmed"]}
    })
    if existing:
        raise HTTPException(status_code=400, detail="You already have an appointment for this slot")
    
    # Check if anyone else already booked this slot
    any_existing = await db.appointments.find_one({
        "slot_id": appointment_data.slot_id,
        "status": {"$in": ["pending", "confirmed"]}
    })
    if any_existing:
        raise HTTPException(status_code=400, detail="This slot has already been booked by another client")
    
    appointment = Appointment(
        user_id=current_user.id,
        slot_id=appointment_data.slot_id,
        notes=appointment_data.notes
    )
    
    # Insert appointment
    result = await db.appointments.insert_one(appointment.dict())
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create appointment")
    
    # Mark slot as unavailable
    update_result = await db.time_slots.update_one(
        {"id": appointment_data.slot_id},
        {"$set": {"is_available": False}}
    )
    
    if update_result.modified_count == 0:
        logger.warning(f"Failed to mark slot {appointment_data.slot_id} as unavailable")
        # Clean up the appointment if slot update failed
        await db.appointments.delete_one({"id": appointment.id})
        raise HTTPException(status_code=500, detail="Failed to reserve slot - please try again")
    
    # Send email notification to admin
    try:
        # Get admin users
        admin_users = await db.users.find({"role": "admin"}).to_list(10)
        for admin in admin_users:
            user_name = f"{current_user.first_name} {current_user.last_name}"
            slot_obj = TimeSlot(**slot)
            appointment_date = slot_obj.date.strftime("%d/%m/%Y")
            appointment_time = f"{slot_obj.start_time} - {slot_obj.end_time}"
            
            await email_service.send_appointment_notification(
                admin_email=admin["email"],
                user_name=user_name,
                user_email=current_user.email,
                service_name=slot_obj.service_name,
                appointment_date=appointment_date,
                appointment_time=appointment_time
            )
    except Exception as e:
        logger.warning(f"Failed to send appointment notification: {str(e)}")
    
    return AppointmentResponse(**appointment.dict())

@api_router.get("/appointments", response_model=List[AppointmentResponse])
async def get_appointments(
    current_user: User = Depends(get_current_active_user_with_db),
    db = Depends(get_db)
):
    """Get appointments (all for admin, own for clients)."""
    if current_user.role == UserRole.ADMIN:
        appointments = await db.appointments.find().sort("created_at", -1).to_list(1000)
    else:
        appointments = await db.appointments.find({"user_id": current_user.id}).sort("created_at", -1).to_list(1000)
    
    # Populate with user and slot info
    result = []
    for apt in appointments:
        apt_response = AppointmentResponse(**apt)
        
        # Get user info
        user = await db.users.find_one({"id": apt["user_id"]})
        if user:
            apt_response.user_name = f"{user['first_name']} {user['last_name']}"
            apt_response.user_email = user['email']
        
        # Get slot info
        slot = await db.time_slots.find_one({"id": apt["slot_id"]})
        if slot:
            apt_response.slot_info = TimeSlotResponse(**slot)
        
        result.append(apt_response)
    
    return result

@api_router.put("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment_status(
    appointment_id: str,
    update_data: AppointmentUpdate,
    current_user: User = Depends(get_current_admin_user_with_db),
    db = Depends(get_db)
):
    """Update appointment status (Admin only)."""
    appointment = await db.appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    update_dict = {"status": update_data.status, "updated_at": datetime.utcnow()}
    if update_data.notes is not None:
        update_dict["notes"] = update_data.notes
    
    await db.appointments.update_one({"id": appointment_id}, {"$set": update_dict})
    
    # If cancelled, make slot available again
    if update_data.status == AppointmentStatus.CANCELLED:
        await db.time_slots.update_one(
            {"id": appointment["slot_id"]},
            {"$set": {"is_available": True}}
        )
    
    updated_appointment = await db.appointments.find_one({"id": appointment_id})
    return AppointmentResponse(**updated_appointment)

@api_router.delete("/appointments/{appointment_id}")
async def delete_appointment(
    appointment_id: str,
    current_user: User = Depends(get_current_admin_user_with_db),
    db = Depends(get_db)
):
    """Delete an appointment (Admin only)."""
    appointment = await db.appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Make slot available again
    await db.time_slots.update_one(
        {"id": appointment["slot_id"]},
        {"$set": {"is_available": True}}
    )
    
    result = await db.appointments.delete_one({"id": appointment_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {"message": "Appointment deleted successfully"}

# ==========================================
# REVIEWS ROUTES
# ==========================================

@api_router.post("/reviews", response_model=ReviewResponse)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_active_user_with_db),
    db = Depends(get_db)
):
    """Create a new review."""
    review = Review(
        user_id=current_user.id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    
    await db.reviews.insert_one(review.dict())
    
    # Send email notification to admin
    try:
        # Get admin users
        admin_users = await db.users.find({"role": "admin"}).to_list(10)
        for admin in admin_users:
            user_name = f"{current_user.first_name} {current_user.last_name}"
            await email_service.send_review_notification(
                admin_email=admin["email"],
                user_name=user_name,
                rating=review_data.rating,
                comment=review_data.comment
            )
    except Exception as e:
        logger.warning(f"Failed to send review notification: {str(e)}")
    
    response = ReviewResponse(**review.dict())
    response.user_name = f"{current_user.first_name} {current_user.last_name}"
    
    return response

@api_router.get("/reviews", response_model=List[ReviewResponse])
async def get_reviews(
    approved_only: bool = True,
    db = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
):
    """Get reviews (approved only for public, all for admin)."""
    current_user = None
    if credentials:
        try:
            current_user = await get_current_user(credentials, db)
        except:
            pass
    
    query = {}
    if approved_only and (not current_user or current_user.role != UserRole.ADMIN):
        query["status"] = ReviewStatus.APPROVED
    
    # Optimized: Use aggregation pipeline to join reviews with users in one query
    pipeline = [
        {"$match": query},
        {"$sort": {"created_at": -1}},
        {"$limit": 50},  # Limit to improve performance
        {
            "$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "id",
                "as": "user_info"
            }
        },
        {
            "$addFields": {
                "user_name": {
                    "$cond": {
                        "if": {"$gt": [{"$size": "$user_info"}, 0]},
                        "then": {
                            "$concat": [
                                {"$arrayElemAt": ["$user_info.first_name", 0]},
                                " ",
                                {"$arrayElemAt": ["$user_info.last_name", 0]}
                            ]
                        },
                        "else": "Utilisateur Anonyme"
                    }
                }
            }
        },
        {
            "$project": {
                "user_info": 0  # Remove the joined user_info array from results
            }
        }
    ]
    
    reviews_with_users = await db.reviews.aggregate(pipeline).to_list(50)
    
    # Convert to response objects
    result = []
    for review in reviews_with_users:
        review_response = ReviewResponse(**review)
        result.append(review_response)
    
    return result

@api_router.put("/reviews/{review_id}", response_model=ReviewResponse)
async def update_review_status(
    review_id: str,
    update_data: ReviewUpdate,
    current_user: User = Depends(get_current_admin_user_with_db),
    db = Depends(get_db)
):
    """Update review status (Admin only)."""
    result = await db.reviews.update_one(
        {"id": review_id},
        {"$set": {"status": update_data.status, "updated_at": datetime.utcnow()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    
    review = await db.reviews.find_one({"id": review_id})
    response = ReviewResponse(**review)
    
    # Get user info
    user = await db.users.find_one({"id": review["user_id"]})
    if user:
        response.user_name = f"{user['first_name']} {user['last_name']}"
    
    return response

# ==========================================
# LEGACY ROUTES (keeping existing functionality)
# ==========================================

@api_router.get("/")
async def root():
    return {"message": "Salon Booking API"}

@api_router.get("/ping")
@api_router.head("/ping")
async def ping():
    """Health check endpoint that responds to both GET and HEAD requests."""
    return {"status": "Ok"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate, db = Depends(get_db)):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks(db = Depends(get_db)):
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Create database indexes on startup."""
    await create_indexes()
    logger.info("Database indexes created")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    await close_db_connection()
    logger.info("Database connection closed")
