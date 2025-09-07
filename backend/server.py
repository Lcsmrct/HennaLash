from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Header
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

# Dependency to get current user optionally (no auth required)
async def get_current_user_with_db_optional(
    authorization: Optional[str] = Header(None),
    db = Depends(get_db)
) -> Optional[User]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        credentials = HTTPAuthorizationCredentials(
            scheme="bearer",
            credentials=authorization.split(" ")[1]
        )
        return await get_current_user(credentials, db)
    except:
        return None

# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@api_router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db = Depends(get_db)):
    """Create a new user account."""
    # Check if user with this email already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    password_hash = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        password_hash=password_hash,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone
    )
    
    # Insert user into database
    user_dict = user.model_dump()
    await db.users.insert_one(user_dict)
    
    return UserResponse(**user_dict)

@api_router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db = Depends(get_db)):
    """Authenticate user and return access token."""
    # Find user by email
    user_data = await db.users.find_one({"email": user_credentials.email})
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user_data["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user_with_db)
):
    """Get current user information."""
    return current_user

# ==========================================
# TIME SLOT ROUTES (Admin Only)
# ==========================================

@api_router.post("/slots", response_model=TimeSlotResponse)
async def create_time_slot(
    slot_data: TimeSlotCreate,
    current_user: User = Depends(get_current_admin_user_with_db),
    db = Depends(get_db)
):
    """Create a new time slot (Admin only)."""
    
    # Calculer end_time basé sur start_time + 1 heure fixe
    try:
        from datetime import datetime, timedelta
        start_time_obj = datetime.strptime(slot_data.time, "%H:%M")
        end_time_obj = start_time_obj + timedelta(hours=1)  # Durée fixe 1 heure
        end_time_str = end_time_obj.strftime("%H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")
    
    slot = TimeSlot(
        date=slot_data.date,
        start_time=slot_data.time,
        end_time=end_time_str,
        service_name="Henné Artisanal",  # Service par défaut
        service_duration=60,  # 1 heure
        price=15.0,  # Prix par défaut
        created_by=current_user.id
    )
    
    slot_dict = slot.model_dump()
    await db.time_slots.insert_one(slot_dict)
    
    return TimeSlotResponse(**slot_dict)

@api_router.get("/slots", response_model=List[TimeSlotResponse])
async def get_time_slots(
    available_only: bool = False,
    limit: int = 50,  # Optimisation: limite par défaut
    skip: int = 0,    # Optimisation: pagination
    db = Depends(get_db)
):
    """Get time slots with pagination and filtering."""
    query = {}
    if available_only:
        query["is_available"] = True
    
    # Optimisation: utiliser projection et limit
    cursor = db.time_slots.find(query).sort("date", 1).skip(skip).limit(limit)
    slots = await cursor.to_list(length=limit)
    
    return [TimeSlotResponse(**slot) for slot in slots]

@api_router.delete("/slots/{slot_id}")
async def delete_time_slot(
    slot_id: str,
    current_user: User = Depends(get_current_admin_user_with_db),
    db = Depends(get_db)
):
    """Delete a time slot (Admin only)."""
    # Check if slot exists
    slot = await db.time_slots.find_one({"id": slot_id})
    if not slot:
        raise HTTPException(status_code=404, detail="Time slot not found")
    
    # Delete the slot
    await db.time_slots.delete_one({"id": slot_id})
    
    return {"message": "Time slot deleted successfully"}

# ==========================================
# APPOINTMENT ROUTES
# ==========================================

@api_router.post("/appointments", response_model=AppointmentResponse)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: User = Depends(get_current_active_user_with_db),
    db = Depends(get_db)
):
    """Create a new appointment."""
    
    # Check if slot exists and is still available
    slot = await db.time_slots.find_one({"id": appointment_data.slot_id, "is_available": True})
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time slot not available"
        )
    
    # Create appointment
    appointment = Appointment(
        user_id=current_user.id,
        slot_id=appointment_data.slot_id,
        service_name=appointment_data.service_name,
        service_price=appointment_data.service_price,
        notes=appointment_data.notes
    )
    
    appointment_dict = appointment.model_dump()
    await db.appointments.insert_one(appointment_dict)
    
    # Mark slot as unavailable
    await db.time_slots.update_one(
        {"id": appointment_data.slot_id},
        {"$set": {"is_available": False}}
    )
    
    # Send email notification to admin
    try:
        # Get admin users
        admin_users = await db.users.find({"role": "admin"}).to_list(10)
        for admin in admin_users:
            user_name = f"{current_user.first_name} {current_user.last_name}"
            slot_obj = TimeSlot(**slot)
            appointment_date = slot_obj.date.strftime("%d/%m/%Y")
            appointment_time = slot_obj.start_time
            
            await email_service.send_appointment_notification(
                admin_email=admin["email"],
                user_name=user_name,
                user_email=current_user.email,
                service_name=appointment_data.service_name,  # Service choisi par le client
                appointment_date=appointment_date,
                appointment_time=appointment_time
            )
    except Exception as e:
        logger.warning(f"Failed to send appointment notification: {str(e)}")
    
    # Return appointment with populated fields
    return AppointmentResponse(**appointment_dict)

@api_router.get("/appointments", response_model=List[AppointmentResponse])
async def get_appointments(
    current_user: User = Depends(get_current_active_user_with_db),
    limit: int = 50,  # Optimisation: pagination
    skip: int = 0,
    db = Depends(get_db)
):
    """Get appointments for current user or all appointments if admin."""
    
    if current_user.role == UserRole.ADMIN:
        # Admin can see all appointments with user info - Optimisation: agregation pipeline
        pipeline = [
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "id",
                    "as": "user_info"
                }
            },
            {
                "$lookup": {
                    "from": "time_slots",
                    "localField": "slot_id",
                    "foreignField": "id",
                    "as": "slot_info"
                }
            },
            {
                "$addFields": {
                    "user_name": {
                        "$concat": [
                            {"$arrayElemAt": ["$user_info.first_name", 0]},
                            " ",
                            {"$arrayElemAt": ["$user_info.last_name", 0]}
                        ]
                    },
                    "user_email": {"$arrayElemAt": ["$user_info.email", 0]},
                    "slot_info": {"$arrayElemAt": ["$slot_info", 0]}
                }
            },
            {
                "$project": {
                    "user_info": 0  # Remove user_info array
                }
            }
        ]
        
        appointments = await db.appointments.aggregate(pipeline).to_list(length=limit)
    else:
        # Regular user can only see their own appointments
        appointments = await db.appointments.find(
            {"user_id": current_user.id}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    
    return [AppointmentResponse(**appointment) for appointment in appointments]

@api_router.put("/appointments/{appointment_id}/status", response_model=AppointmentResponse)
async def update_appointment_status(
    appointment_id: str,
    appointment_update: AppointmentUpdate,
    current_user: User = Depends(get_current_admin_user_with_db),
    db = Depends(get_db)
):
    """Update appointment status (Admin only)."""
    
    # Check if appointment exists
    appointment = await db.appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Update appointment
    await db.appointments.update_one(
        {"id": appointment_id},
        {"$set": {"status": appointment_update.status, "notes": appointment_update.notes, "updated_at": datetime.utcnow()}}
    )
    
    # Send confirmation email to client if status is confirmed
    if appointment_update.status == AppointmentStatus.CONFIRMED:
        try:
            # Get user and slot info
            user = await db.users.find_one({"id": appointment["user_id"]})
            slot = await db.time_slots.find_one({"id": appointment["slot_id"]})
            
            if user and slot:
                user_name = f"{user['first_name']} {user['last_name']}"
                slot_obj = TimeSlot(**slot)
                appointment_date = slot_obj.date.strftime("%d/%m/%Y")
                appointment_time = slot_obj.start_time
                
                await email_service.send_appointment_confirmation_to_client(
                    client_email=user["email"],
                    client_name=user_name,
                    service_name=appointment.get("service_name", "Service"),
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    service_price=appointment.get("service_price", 0)
                )
        except Exception as e:
            logger.warning(f"Failed to send confirmation email to client: {str(e)}")
    
    updated_appointment = await db.appointments.find_one({"id": appointment_id})
    return AppointmentResponse(**updated_appointment)

@api_router.delete("/appointments/{appointment_id}")
async def delete_appointment(
    appointment_id: str,
    current_user: User = Depends(get_current_admin_user_with_db),
    db = Depends(get_db)
):
    """Delete an appointment (Admin only)."""
    
    # Check if appointment exists
    appointment = await db.appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Make the slot available again
    await db.time_slots.update_one(
        {"id": appointment["slot_id"]},
        {"$set": {"is_available": True}}
    )
    
    # Delete appointment
    await db.appointments.delete_one({"id": appointment_id})
    
    return {"message": "Appointment deleted successfully"}

# ==========================================
# REVIEW ROUTES
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
    
    review_dict = review.model_dump()
    await db.reviews.insert_one(review_dict)
    
    # Send notification to admin
    try:
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
    
    return ReviewResponse(**review_dict)

@api_router.get("/reviews", response_model=List[ReviewResponse])
async def get_reviews(
    approved_only: bool = False,
    limit: int = 50,  # Optimisation: pagination
    skip: int = 0,
    db = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_with_db_optional)
):
    """Get reviews. If approved_only=true, no authentication required."""
    
    if approved_only:
        # Public endpoint - optimized with compound index
        reviews = await db.reviews.find(
            {"status": "approved"}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    else:
        # Admin endpoint - need authentication
        if not current_user or current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Optimised aggregation pipeline for admin reviews
        pipeline = [
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit},
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
                        "$concat": [
                            {"$arrayElemAt": ["$user_info.first_name", 0]},
                            " ",
                            {"$arrayElemAt": ["$user_info.last_name", 0]}
                        ]
                    }
                }
            },
            {
                "$project": {
                    "user_info": 0
                }
            }
        ]
        
        reviews = await db.reviews.aggregate(pipeline).to_list(length=limit)
    
    return [ReviewResponse(**review) for review in reviews]

@api_router.put("/reviews/{review_id}", response_model=ReviewResponse)
async def update_review_status(
    review_id: str,
    review_update: ReviewUpdate,
    current_user: User = Depends(get_current_admin_user_with_db),
    db = Depends(get_db)
):
    """Update review status (Admin only)."""
    
    # Check if review exists
    review = await db.reviews.find_one({"id": review_id})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Update review
    await db.reviews.update_one(
        {"id": review_id},
        {"$set": {"status": review_update.status, "updated_at": datetime.utcnow()}}
    )
    
    updated_review = await db.reviews.find_one({"id": review_id})
    return ReviewResponse(**updated_review)

# ==========================================
# UTILITY ROUTES
# ==========================================

@api_router.get("/ping")
async def health_check():
    """Health check endpoint."""
    return {"status": "Ok"}

@api_router.head("/ping")
async def health_check_head():
    """Health check HEAD endpoint."""
    return {"status": "Ok"}

# ==========================================
# CORS Configuration
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://henna-lash.onrender.com", "https://henna-lash-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount the API router
app.include_router(api_router)

# Add logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Startup event to create indexes
@app.on_event("startup")
async def startup_event():
    """Create database indexes on startup."""
    await create_indexes()
    logger.info("Database indexes created successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    await close_db_connection()
    logger.info("Database connection closed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)