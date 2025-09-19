from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Header, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.cors import CORSMiddleware
from datetime import timedelta
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import random
import string

# Local imports
from models import *
from auth import *
from database import get_database, create_indexes, close_db_connection
from email_service import email_service

# Background task for sending emails asynchronously
async def send_appointment_notification_background(
    admin_emails: list,
    user_name: str,
    user_email: str,
    service_name: str,
    appointment_date: str,
    appointment_time: str
):
    """Send appointment notification email in background - non-blocking"""
    try:
        for admin_email in admin_emails:
            await email_service.send_appointment_notification(
                admin_email=admin_email,
                user_name=user_name,
                user_email=user_email,
                service_name=service_name,
                appointment_date=appointment_date,
                appointment_time=appointment_time
            )
        logging.info(f"Background email notification sent for appointment: {user_name} - {service_name}")
    except Exception as e:
        logging.error(f"Background email notification failed: {str(e)}")
        # Don't re-raise - background task failures shouldn't affect API response

async def send_appointment_cancellation_background(
    client_email: str,
    client_name: str,
    service_name: str,
    appointment_date: str,
    appointment_time: str,
    service_price: float
):
    """Send appointment cancellation email in background - non-blocking"""
    try:
        await email_service.send_appointment_cancellation_to_client(
            client_email=client_email,
            client_name=client_name,
            service_name=service_name,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            service_price=service_price
        )
        logging.info(f"Background cancellation email sent to: {client_email} - {service_name}")
    except Exception as e:
        logging.error(f"Background cancellation email failed: {str(e)}")
        # Don't re-raise - background task failures shouldn't affect API response

async def send_review_notification_background(
    admin_emails: list,
    user_name: str,
    rating: int,
    comment: str
):
    """Send review notification email to admins in background - non-blocking"""
    try:
        for admin_email in admin_emails:
            await email_service.send_review_notification(
                admin_email=admin_email,
                user_name=user_name,
                rating=rating,
                comment=comment
            )
        logging.info(f"Background review notification sent for: {user_name} - {rating} stars")
    except Exception as e:
        logging.error(f"Background review notification failed: {str(e)}")
        # Don't re-raise - background task failures shouldn't affect API response

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
        service_name="HennaLash",  # Service par défaut
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
    background_tasks: BackgroundTasks,
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
    
    # Schedule email notification in background (non-blocking)
    try:
        # Get admin emails
        admin_users = await db.users.find({"role": "admin"}).to_list(10)
        admin_emails = [admin["email"] for admin in admin_users]
        
        if admin_emails:
            user_name = f"{current_user.first_name} {current_user.last_name}"
            slot_obj = TimeSlot(**slot)
            appointment_date = slot_obj.date.strftime("%d/%m/%Y")
            appointment_time = slot_obj.start_time
            
            # Add background task - this returns immediately without waiting for email
            background_tasks.add_task(
                send_appointment_notification_background,
                admin_emails=admin_emails,
                user_name=user_name,
                user_email=current_user.email,
                service_name=appointment_data.service_name,
                appointment_date=appointment_date,
                appointment_time=appointment_time
            )
            logging.info(f"Email notification scheduled for appointment: {appointment.id}")
    except Exception as e:
        logging.warning(f"Failed to schedule email notification: {str(e)}")
        # Continue - email failure shouldn't block appointment creation
    
    # Return appointment with populated fields (user_name, user_email, slot_info)
    pipeline = [
        {"$match": {"id": appointment.id}},
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
    
    created_appointment_list = await db.appointments.aggregate(pipeline).to_list(length=1)
    if not created_appointment_list:
        # Fallback to basic response if aggregation fails
        return AppointmentResponse(**appointment_dict)
    
    return AppointmentResponse(**created_appointment_list[0])

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
        # Regular user can only see their own appointments - with slot info
        pipeline = [
            {"$match": {"user_id": current_user.id}},
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit},
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
                    "slot_info": {"$arrayElemAt": ["$slot_info", 0]}
                }
            }
        ]
        
        appointments = await db.appointments.aggregate(pipeline).to_list(length=limit)
    
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
    
    # Update appointment - preserve original client notes if no admin notes provided
    update_fields = {
        "status": appointment_update.status, 
        "updated_at": datetime.utcnow()
    }
    
    # Only update notes if admin provides new notes, otherwise preserve existing ones
    if appointment_update.notes is not None and appointment_update.notes.strip():
        # If admin provides notes, append them to existing client notes
        existing_notes = appointment.get("notes", "")
        if existing_notes:
            update_fields["notes"] = f"{existing_notes}\n\n--- Notes Admin ---\n{appointment_update.notes}"
        else:
            update_fields["notes"] = appointment_update.notes
    # If no admin notes provided, keep existing client notes unchanged
    
    await db.appointments.update_one(
        {"id": appointment_id},
        {"$set": update_fields}
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
    
    # Return the updated appointment with populated fields (user_name, user_email, slot_info)
    pipeline = [
        {"$match": {"id": appointment_id}},
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
    
    updated_appointment_list = await db.appointments.aggregate(pipeline).to_list(length=1)
    if not updated_appointment_list:
        raise HTTPException(status_code=404, detail="Updated appointment not found")
    
    return AppointmentResponse(**updated_appointment_list[0])

@api_router.delete("/appointments/{appointment_id}")
async def delete_appointment(
    appointment_id: str,
    current_user: User = Depends(get_current_active_user_with_db),
    db = Depends(get_db)
):
    """Delete an appointment. Admins can delete any appointment, clients can only delete their own past completed/cancelled appointments."""
    
    # Check if appointment exists
    appointment = await db.appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # If user is not admin, check if they own the appointment and if it's eligible for deletion
    if current_user.role != "admin":
        # Check if user owns the appointment
        if appointment["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="You can only delete your own appointments")
        
        # Check if appointment is completed or cancelled (only past appointments can be deleted by clients)
        if appointment["status"] not in ["completed", "cancelled"]:
            raise HTTPException(status_code=403, detail="You can only delete completed or cancelled appointments")
        
        # Check if appointment is at least 1 hour old (additional safety)
        appointment_date = appointment.get("created_at", datetime.utcnow())
        if isinstance(appointment_date, str):
            appointment_date = datetime.fromisoformat(appointment_date.replace('Z', '+00:00'))
        hours_passed = (datetime.utcnow() - appointment_date).total_seconds() / 3600
        if hours_passed < 1:
            raise HTTPException(status_code=403, detail="You can only delete appointments that are at least 1 hour old")
    
    # For admin users or eligible client deletions, make the slot available again only if it's not already taken
    if appointment["status"] in ["confirmed", "pending"]:
        await db.time_slots.update_one(
            {"id": appointment["slot_id"]},
            {"$set": {"is_available": True}}
        )
    
    # Delete appointment
    await db.appointments.delete_one({"id": appointment_id})
    
    return {"message": "Appointment deleted successfully"}
@api_router.put("/appointments/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_admin_user_with_db),
    db = Depends(get_db)
):
    """Cancel an appointment and notify client by email (Admin only)."""
    
    # Get appointment with user details using aggregation
    pipeline = [
        {"$match": {"id": appointment_id}},
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
                "user_info": {"$arrayElemAt": ["$user_info", 0]},
                "slot_info": {"$arrayElemAt": ["$slot_info", 0]}
            }
        }
    ]
    
    appointment_data = await db.appointments.aggregate(pipeline).to_list(length=1)
    if not appointment_data:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment = appointment_data[0]
    
    # Update appointment status to cancelled
    await db.appointments.update_one(
        {"id": appointment_id},
        {"$set": {"status": "cancelled", "updated_at": datetime.utcnow()}}
    )
    
    # Make the slot available again
    await db.time_slots.update_one(
        {"id": appointment["slot_id"]},
        {"$set": {"is_available": True}}
    )
    
    # Send cancellation email to client
    if appointment.get("user_info") and appointment.get("slot_info"):
        user_info = appointment["user_info"]
        slot_info = appointment["slot_info"]
        
        client_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip()
        client_email = user_info.get("email")
        service_name = appointment.get("service_name", "Service")
        service_price = appointment.get("service_price", 0)
        
        # Format date and time
        appointment_date = "Date non spécifiée"
        appointment_time = "Heure non spécifiée"
        
        if slot_info.get("date"):
            try:
                date_obj = datetime.fromisoformat(slot_info["date"].replace('Z', '+00:00'))
                appointment_date = date_obj.strftime("%d/%m/%Y")
            except:
                pass
        
        if slot_info.get("start_time"):
            appointment_time = slot_info["start_time"]
        
        # Send email in background (non-blocking for better performance)
        if client_email:
            background_tasks.add_task(
                send_appointment_cancellation_background,
                client_email=client_email,
                client_name=client_name,
                service_name=service_name,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                service_price=service_price
            )
            logging.info(f"Cancellation email scheduled for: {client_email}")
        else:
            logging.warning("No client email found for cancellation notification")
    
    return {"message": "Appointment cancelled successfully and client notified by email"}

# ==========================================
# REVIEW ROUTES
# ==========================================

@api_router.post("/reviews", response_model=ReviewResponse)
async def create_review(
    review_data: ReviewCreate,
    background_tasks: BackgroundTasks,
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
    
    # Send notification to admin in background (non-blocking for better performance)
    try:
        admin_users = await db.users.find({"role": "admin"}).to_list(10)
        admin_emails = [admin["email"] for admin in admin_users]
        
        if admin_emails:
            user_name = f"{current_user.first_name} {current_user.last_name}"
            background_tasks.add_task(
                send_review_notification_background,
                admin_emails=admin_emails,
                user_name=user_name,
                rating=review_data.rating,
                comment=review_data.comment
            )
            logging.info(f"Review notification scheduled for: {user_name} - {review_data.rating} stars")
    except Exception as e:
        logger.warning(f"Failed to schedule review notification: {str(e)}")
    
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
# MAINTENANCE MODE ENDPOINTS
# ==========================================

# Fonctions pour gérer l'état de maintenance en base de données
async def get_maintenance_from_db():
    """Récupère l'état de maintenance depuis la base de données."""
    db = await get_database()
    maintenance_doc = await db.maintenance.find_one({"_id": "site_maintenance"})
    
    if maintenance_doc:
        return {
            "is_maintenance": maintenance_doc.get("is_maintenance", False),
            "message": maintenance_doc.get("message", "Site en maintenance. Veuillez réessayer plus tard."),
            "enabled_at": maintenance_doc.get("enabled_at"),
            "enabled_by": maintenance_doc.get("enabled_by")
        }
    else:
        # État par défaut si aucun document n'existe
        return {
            "is_maintenance": False,
            "message": "Site en maintenance. Veuillez réessayer plus tard.",
            "enabled_at": None,
            "enabled_by": None
        }

async def save_maintenance_to_db(maintenance_state):
    """Sauvegarde l'état de maintenance en base de données."""
    db = await get_database()
    await db.maintenance.update_one(
        {"_id": "site_maintenance"},
        {"$set": maintenance_state},
        upsert=True
    )

@api_router.get("/maintenance", response_model=MaintenanceStatus)
async def get_maintenance_status():
    """Get current maintenance status - public endpoint."""
    maintenance_state = await get_maintenance_from_db()
    return MaintenanceStatus(**maintenance_state)

@api_router.post("/maintenance", response_model=MaintenanceStatus)
async def toggle_maintenance(
    maintenance_data: MaintenanceToggle,
    current_user: User = Depends(get_current_admin_user_with_db)
):
    """Toggle maintenance mode (Admin only)."""
    maintenance_state = {
        "is_maintenance": maintenance_data.is_maintenance,
        "message": maintenance_data.message or "Site en maintenance. Veuillez réessayer plus tard.",
        "enabled_at": datetime.utcnow() if maintenance_data.is_maintenance else None,
        "enabled_by": current_user.id if maintenance_data.is_maintenance else None
    }
    
    await save_maintenance_to_db(maintenance_state)
    return MaintenanceStatus(**maintenance_state)

@api_router.post("/maintenance/emergency-disable")
async def emergency_disable_maintenance():
    """
    Route d'urgence pour désactiver la maintenance sans authentification.
    À utiliser uniquement en cas de problème critique.
    Cette route nécessite un paramètre secret dans l'URL.
    """
    maintenance_state = {
        "is_maintenance": False,
        "message": "Site opérationnel",
        "enabled_at": None,
        "enabled_by": None
    }
    
    await save_maintenance_to_db(maintenance_state)
    return {"status": "success", "message": "Maintenance désactivée via route d'urgence"}

# ==========================================
# PASSWORD RESET ROUTES
# ==========================================

def generate_reset_code():
    """Generate a 6-digit numeric code."""
    return ''.join(random.choices(string.digits, k=6))

@api_router.post("/auth/password-reset/request")
async def request_password_reset(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Request password reset - sends code via email."""
    
    # Check if user exists
    user = await db.users.find_one({"email": request.email})
    if not user:
        # Security: Don't reveal if email exists or not
        return {"message": "Si l'email existe, un code de réinitialisation a été envoyé."}
    
    # Generate 6-digit code
    reset_code = generate_reset_code()
    
    # Save reset code to database
    reset_data = PasswordResetCode(
        email=request.email,
        code=reset_code
    )
    
    # Remove any existing reset codes for this email
    await db.password_resets.delete_many({"email": request.email})
    
    # Insert new reset code
    await db.password_resets.insert_one(reset_data.model_dump())
    
    # Send email in background
    background_tasks.add_task(
        send_password_reset_email,
        request.email,
        reset_code,
        user.get("first_name", "")
    )
    
    return {"message": "Si l'email existe, un code de réinitialisation a été envoyé."}

@api_router.post("/auth/password-reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db = Depends(get_db)
):
    """Confirm password reset with code and set new password."""
    
    # Find valid reset code
    reset_record = await db.password_resets.find_one({
        "email": request.email,
        "code": request.code,
        "used": False,
        "expires_at": {"$gt": datetime.utcnow()}
    })
    
    if not reset_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code invalide ou expiré"
        )
    
    # Check if user still exists
    user = await db.users.find_one({"email": request.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Hash new password
    hashed_password = get_password_hash(request.new_password)
    
    # Update user password
    await db.users.update_one(
        {"email": request.email},
        {"$set": {"password_hash": hashed_password, "updated_at": datetime.utcnow()}}
    )
    
    # Mark reset code as used
    await db.password_resets.update_one(
        {"id": reset_record["id"]},
        {"$set": {"used": True}}
    )
    
    # Clean up old reset codes for this email
    await db.password_resets.delete_many({
        "email": request.email,
        "$or": [
            {"used": True},
            {"expires_at": {"$lt": datetime.utcnow()}}
        ]
    })
    
    return {"message": "Mot de passe réinitialisé avec succès"}

# Background task for sending password reset email
async def send_password_reset_email(email: str, code: str, first_name: str):
    """Send password reset email in background."""
    try:
        await email_service.send_password_reset_email(
            email=email,
            code=code,
            first_name=first_name
        )
        print(f"Password reset email sent to {email}")
    except Exception as e:
        print(f"Failed to send password reset email to {email}: {e}")

# ==========================================
# MAINTENANCE MIDDLEWARE
# ==========================================

from fastapi import Request
from fastapi.responses import JSONResponse

@app.middleware("http")
async def maintenance_middleware(request: Request, call_next):
    """Middleware to handle maintenance mode."""
    try:
        # Skip maintenance check for static health endpoints
        if request.url.path in ["/", "/health", "/api/ping"]:
            response = await call_next(request)
            return response
            
        # Récupérer l'état de maintenance depuis la BD
        maintenance_state = await get_maintenance_from_db()
        
        # Always allow these endpoints even during maintenance
        allowed_paths = ["/api/maintenance", "/api/maintenance/emergency-disable", "/api/login", "/api/register", "/api/ping", "/docs", "/openapi.json", "/"]
        
        if maintenance_state["is_maintenance"] and request.url.path not in allowed_paths:
            # Allow admin users to bypass maintenance
            auth_header = request.headers.get("authorization")
            if auth_header and "Bearer " in auth_header:
                # Let the request through - admin authentication will be validated later
                pass
            else:
                return JSONResponse(
                    status_code=503,
                    content={
                        "detail": maintenance_state["message"],
                        "maintenance": True,
                        "enabled_at": maintenance_state["enabled_at"].isoformat() if maintenance_state["enabled_at"] else None
                    }
                )
        
        response = await call_next(request)
        return response
    except Exception as e:
        # If maintenance check fails, let request through to avoid blocking service
        logger.warning(f"Maintenance middleware error: {e}")
        response = await call_next(request)
        return response

# ==========================================
# CORS Configuration
# ==========================================

# Configure CORS - More permissive for deployment
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
if cors_origins == ["*"]:
    cors_origins = ["*"]  # Allow all origins in development
else:
    # Add common deployment URLs
    cors_origins.extend([
        "http://localhost:3000", 
        "https://hennalash.fr", 
        "https://www.hennalash.fr", 
        "https://hennalash.onrender.com"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ==========================================
# ROOT ROUTE for Health Check (Render compatibility)
# ==========================================

@app.get("/")
async def root():
    """Root endpoint for health checks and deployment verification."""
    return {
        "status": "ok",
        "service": "HennaLash Salon API",
        "version": "1.0.0",
        "message": "API is running"
    }

# Additional health check for HEAD requests (Render requirement)
@app.head("/")
async def root_head():
    """Root HEAD endpoint for health checks."""
    return {"status": "ok"}

# Health endpoint for load balancers
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    try:
        # Test database connection
        db = await get_database()
        await db.command('ping')
        return {
            "status": "healthy",
            "service": "HennaLash API",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "HennaLash API", 
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

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