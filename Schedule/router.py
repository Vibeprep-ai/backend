from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List, Optional
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

from .schema import (
    SlotUpdate, SlotResponse, SlotCreateResponse, SlotUpdateResponse, 
    SlotDeleteResponse, UserCalendarResponse, MonthCalendarResponse,
    ErrorResponse, TaskUpdate, TaskAssignResponse, SimpleSlotUpdate,
    Task, SlotWithTask, TaskSearchResponse, CalendarDocument
)

load_dotenv()

router = APIRouter(prefix="/calendar", tags=["calendar"])

def get_mongodb_url():
    base_url = os.getenv("MONGODB_URL")
    return base_url

MONGODB_URL = get_mongodb_url()
DATABASE_NAME = os.getenv("DATABASE_NAME", "Vibeprep_Users")
COLLECTION_NAME = "calendar_data"

print(f"MongoDB URL: {MONGODB_URL}")
print(f"Database Name: {DATABASE_NAME}")

class MongoDB:
    client: MongoClient = None
    database = None

mongodb = MongoDB()

def connect_to_mongo():
    try:
        print(f"🔄 Connecting to MongoDB...")
        mongodb.client = MongoClient(
            MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        mongodb.database = mongodb.client[DATABASE_NAME]
        mongodb.client.admin.command('ping')
        print(f"Successfully connected to MongoDB database: {DATABASE_NAME}")
    except OperationFailure as e:
        print(f"Authentication/Operation failed: {e}")
        if "authentication failed" in str(e).lower():
            print("Please check your MongoDB username and password")
        raise e
    except ConnectionFailure as e:
        print(f"Connection failed: {e}")
        print("Could not connect to MongoDB server")
        raise e
    except Exception as e:
        print(f"Unexpected error connecting to MongoDB: {e}")
        print(f"Error type: {type(e).__name__}")
        raise e

def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
        print("📤 Disconnected from MongoDB")

def get_database():
    if mongodb.database is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection not established"
        )
    return mongodb.database

def convert_legacy_slots(slots: List[Any]) -> List[SlotWithTask]:
    converted_slots = []
    for slot in slots:
        if isinstance(slot, str):
            converted_slots.append(SlotWithTask(time_slot=slot, task=None))
        elif isinstance(slot, dict):
            if "time_slot" in slot:
                task_data = slot.get("task")
                task = Task(**task_data) if task_data else None
                converted_slots.append(SlotWithTask(time_slot=slot["time_slot"], task=task))
            else:
                converted_slots.append(SlotWithTask(time_slot=slot.get("time_slot", ""), task=None))
    return converted_slots

def get_calendar_document(
    user_id: str, 
    year: int, 
    month: int, 
    date: int
) -> Optional[Dict[str, Any]]:
    db = get_database()
    return db[COLLECTION_NAME].find_one({
        "user_id": user_id,
        "year": year,
        "month": month,
        "date": date
    })

def upsert_calendar_document(
    user_id: str,
    year: int,
    month: int,
    date: int,
    slots: List[Dict[str, Any]]
) -> None:
    db = get_database()
    db[COLLECTION_NAME].update_one(
        {
            "user_id": user_id,
            "year": year,
            "month": month,
            "date": date
        },
        {
            "$set": {
                "slots": slots,
                "updated_at": datetime.utcnow()
            },
            "$setOnInsert": {
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )

# Health check endpoint for MongoDB
@router.get("/health")
def health_check():
    """Health check endpoint for MongoDB connection"""
    try:
        if mongodb.database is None:
            return {"status": "error", "message": "Database not connected"}
        
        # Try to ping the database
        mongodb.client.admin.command('ping')
        return {
            "status": "healthy", 
            "message": "MongoDB connection is working",
            "database": DATABASE_NAME
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Database connection failed: {str(e)}"
        }

# GET endpoint - Get slots with tasks for a given day
@router.get(
    "/slots/{user_id}/{year}/{month}/{date}",
    response_model=SlotResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Slots not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def get_slots(
    user_id: str, 
    year: int, 
    month: int, 
    date: int
) -> SlotResponse:
    """Get slots with tasks for a specific user and date"""
    try:
        doc = get_calendar_document(user_id, year, month, date)
        
        if not doc:
            return SlotResponse(
                user_id=user_id,
                year=year,
                month=month,
                date=date,
                slots=[],
                total_slots=0
            )
        
        raw_slots = doc.get("slots", [])
        slots = convert_legacy_slots(raw_slots)
        
        # Filter out empty slots
        non_empty_slots = [slot for slot in slots if slot.time_slot.strip()]
        
        return SlotResponse(
            user_id=user_id,
            year=year,
            month=month,
            date=date,
            slots=non_empty_slots,
            total_slots=len(non_empty_slots)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving slots: {str(e)}"
        )

# POST endpoint - Create/Add slots with tasks for a date
@router.post(
    "/slots/{user_id}/{year}/{month}/{date}",
    response_model=SlotCreateResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid date or data"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def create_slots(
    user_id: str, 
    year: int, 
    month: int, 
    date: int, 
    slot_data: SlotUpdate
) -> SlotCreateResponse:
    """Create or add slots with tasks for a specific date"""
    try:
        # Validate date
        datetime(year, month, date)
        
        # Get existing document
        existing_doc = get_calendar_document(user_id, year, month, date)
        existing_slots = []
        
        if existing_doc:
            existing_raw_slots = existing_doc.get("slots", [])
            existing_slots = convert_legacy_slots(existing_raw_slots)
        
        # Convert new slots to dict format for storage
        new_slots_dict = []
        for slot in slot_data.slots:
            slot_dict = {
                "time_slot": slot.time_slot,
                "task": slot.task.dict() if slot.task else None
            }
            new_slots_dict.append(slot_dict)
        
        # Combine existing and new slots (avoid duplicates by time_slot)
        existing_time_slots = {slot.time_slot for slot in existing_slots}
        combined_slots = [slot.dict() for slot in existing_slots]
        
        for new_slot in new_slots_dict:
            if new_slot["time_slot"] not in existing_time_slots:
                combined_slots.append(new_slot)
        
        # Save to database
        upsert_calendar_document(user_id, year, month, date, combined_slots)
        
        # Convert back to response format
        response_slots = convert_legacy_slots(combined_slots)
        
        return SlotCreateResponse(
            message="Slots created successfully",
            user_id=user_id,
            year=year,
            month=month,
            date=date,
            slots=response_slots
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date: {str(ve)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating slots: {str(e)}"
        )

# POST endpoint - Assign task to a specific slot
@router.post(
    "/slots/{user_id}/{year}/{month}/{date}/{time_slot}/task",
    response_model=TaskAssignResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid data"},
        404: {"model": ErrorResponse, "description": "Slot not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def assign_task_to_slot(
    user_id: str, 
    year: int, 
    month: int, 
    date: int, 
    time_slot: str,
    task_data: TaskUpdate
) -> TaskAssignResponse:
    """Assign a task to a specific time slot"""
    try:
        doc = get_calendar_document(user_id, year, month, date)
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Date not found in calendar"
            )
        
        raw_slots = doc.get("slots", [])
        slots = convert_legacy_slots(raw_slots)
        
        # Find the slot and assign task
        slot_found = False
        updated_slots = []
        
        for slot in slots:
            if slot.time_slot == time_slot:
                slot.task = task_data.task
                slot_found = True
            updated_slots.append(slot.dict())
        
        if not slot_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Time slot '{time_slot}' not found"
            )
        
        # Update in database
        upsert_calendar_document(user_id, year, month, date, updated_slots)
        
        return TaskAssignResponse(
            message="Task assigned successfully",
            user_id=user_id,
            year=year,
            month=month,
            date=date,
            time_slot=time_slot,
            task=task_data.task
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assigning task: {str(e)}"
        )

# GET endpoint - Search tasks by status or priority
@router.get(
    "/tasks/{user_id}",
    response_model=TaskSearchResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def search_tasks(
    user_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None
) -> TaskSearchResponse:
    """Search tasks by various criteria"""
    try:
        db = get_database()
        
        # Build query
        query = {"user_id": user_id}
        if year:
            query["year"] = year
        if month:
            query["month"] = month
        
        # Get all matching documents
        documents = list(db[COLLECTION_NAME].find(query))
        
        tasks = []
        
        for doc in documents:
            raw_slots = doc.get("slots", [])
            slots = convert_legacy_slots(raw_slots)
            
            for slot in slots:
                if slot.task:
                    # Apply filters
                    if status and slot.task.status != status:
                        continue
                    if priority and slot.task.priority != priority:
                        continue
                        
                    tasks.append({
                        "date": f"{doc['year']}-{str(doc['month']).zfill(2)}-{str(doc['date']).zfill(2)}",
                        "time_slot": slot.time_slot,
                        "task": slot.task.dict()
                    })
        
        return TaskSearchResponse(
            user_id=user_id,
            tasks=tasks
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching tasks: {str(e)}"
        )

# PUT endpoint - Update/Replace slots for a date
@router.put(
    "/slots/{user_id}/{year}/{month}/{date}",
    response_model=SlotUpdateResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid date or data"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def update_slots(
    user_id: str, 
    year: int, 
    month: int, 
    date: int, 
    slot_data: SlotUpdate
) -> SlotUpdateResponse:
    """Update/Replace slots for a specific date"""
    try:
        # Validate date
        datetime(year, month, date)
        
        # Convert slots to dict format for storage
        slots_dict = []
        for slot in slot_data.slots:
            slot_dict = {
                "time_slot": slot.time_slot,
                "task": slot.task.dict() if slot.task else None
            }
            slots_dict.append(slot_dict)
        
        # Update in database
        upsert_calendar_document(user_id, year, month, date, slots_dict)
        
        return SlotUpdateResponse(
            message="Slots updated successfully",
            user_id=user_id,
            year=year,
            month=month,
            date=date,
            slots=slot_data.slots
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date: {str(ve)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating slots: {str(e)}"
        )

# DELETE endpoint - Delete slots for a date
@router.delete(
    "/slots/{user_id}/{year}/{month}/{date}",
    response_model=SlotDeleteResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Slots not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def delete_slots(
    user_id: str, 
    year: int, 
    month: int, 
    date: int
) -> SlotDeleteResponse:
    """Delete all slots for a specific date"""
    try:
        db = get_database()
        
        result = db[COLLECTION_NAME].delete_one({
            "user_id": user_id,
            "year": year,
            "month": month,
            "date": date
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No slots found for the specified date"
            )
        
        return SlotDeleteResponse(
            message="Slots deleted successfully",
            user_id=user_id,
            year=year,
            month=month,
            date=date
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting slots: {str(e)}"
        )

# GET endpoint - Get all data for a user
@router.get(
    "/user/{user_id}",
    response_model=UserCalendarResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def get_user_calendar(user_id: str) -> UserCalendarResponse:
    """Get all calendar data for a specific user"""
    try:
        db = get_database()
        
        documents = list(db[COLLECTION_NAME].find({"user_id": user_id}))
        
        # Convert ObjectId to string for JSON serialization
        calendar_data = []
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            calendar_data.append(doc)
        
        return UserCalendarResponse(
            user_id=user_id,
            calendar=calendar_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user calendar: {str(e)}"
        )

# GET endpoint - Get month view
@router.get(
    "/month/{user_id}/{year}/{month}",
    response_model=MonthCalendarResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
def get_month_calendar(
    user_id: str, 
    year: int, 
    month: int
) -> MonthCalendarResponse:
    """Get all slots for a specific month"""
    try:
        db = get_database()
        
        documents = list(db[COLLECTION_NAME].find({
            "user_id": user_id,
            "year": year,
            "month": month
        }))
        
        # Convert to response format
        month_data = []
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            raw_slots = doc.get("slots", [])
            slots = convert_legacy_slots(raw_slots)
            doc["slots"] = [slot.dict() for slot in slots]
            month_data.append(doc)
        
        return MonthCalendarResponse(
            user_id=user_id,
            year=year,
            month=month,
            dates=month_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving month data: {str(e)}"
        )