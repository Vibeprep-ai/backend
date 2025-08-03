from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional, List, Annotated
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class Task(BaseModel):
    task_id: str = Field(..., description="Unique task identifier", example="task_001")
    title: str = Field(..., description="Task title", example="Team Meeting")
    description: Optional[str] = Field(None, description="Task description", example="Weekly team sync meeting")
    priority: Optional[str] = Field("medium", description="Task priority", example="high")
    status: Optional[str] = Field("pending", description="Task status", example="pending")
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        allowed_priorities = ["low", "medium", "high", "urgent"]
        if v and v not in allowed_priorities:
            raise ValueError(f"Priority must be one of: {allowed_priorities}")
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed_statuses = ["pending", "in_progress", "completed", "cancelled"]
        if v and v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {allowed_statuses}")
        return v

class SlotWithTask(BaseModel):
    time_slot: str = Field(..., description="Time slot", example="09:00-10:00")
    task: Optional[Task] = Field(None, description="Assigned task for this slot")

class SlotUpdate(BaseModel):
    slots: List[SlotWithTask] = Field(
        ..., 
        description="List of time slots with optional tasks",
        example=[
            {
                "time_slot": "09:00-10:00",
                "task": {
                    "task_id": "task_001",
                    "title": "Team Meeting",
                    "description": "Weekly team sync",
                    "priority": "high",
                    "status": "pending"
                }
            },
            {
                "time_slot": "14:00-15:00",
                "task": None
            }
        ]
    )
    
    @field_validator('slots')
    @classmethod
    def validate_slots(cls, v):
        if not v:
            raise ValueError("Slots list cannot be empty")
        for slot_data in v:
            if not slot_data.time_slot.strip():
                raise ValueError("Time slot cannot be empty")
        return v

class SimpleSlotUpdate(BaseModel):
    slots: List[str] = Field(
        ..., 
        description="List of time slots",
        example=["09:00-10:00", "14:00-15:00"]
    )

class TaskUpdate(BaseModel):
    task: Task = Field(..., description="Task to assign to the slot")

# MongoDB Document Schemas
class CalendarDocument(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str = Field(..., description="User ID")
    year: int = Field(..., description="Year")
    month: int = Field(..., description="Month")
    date: int = Field(..., description="Date")
    slots: List[Dict[str, Any]] = Field(default=[], description="List of slots with tasks")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class CalendarData(BaseModel):
    user_id: str = Field(..., description="User ID", example="user_123")
    year: int = Field(..., description="Year", example=2025, ge=1900, le=3000)
    month: int = Field(..., description="Month", example=8, ge=1, le=12)
    date: int = Field(..., description="Date", example=15, ge=1, le=31)
    slots: List[SlotWithTask] = Field(
        default=[], 
        description="List of time slots with tasks",
        example=[
            {
                "time_slot": "09:00-10:00",
                "task": {
                    "task_id": "task_001",
                    "title": "Team Meeting",
                    "description": "Weekly sync",
                    "priority": "high",
                    "status": "pending"
                }
            }
        ]
    )

class SlotResponse(BaseModel):
    user_id: str = Field(..., description="User ID", example="user_123")
    year: int = Field(..., description="Year", example=2025)
    month: int = Field(..., description="Month", example=8)
    date: int = Field(..., description="Date", example=15)
    slots: List[SlotWithTask] = Field(
        default=[], 
        description="List of time slots with tasks",
        example=[
            {
                "time_slot": "09:00-10:00",
                "task": {
                    "task_id": "task_001",
                    "title": "Team Meeting",
                    "description": "Weekly sync",
                    "priority": "high",
                    "status": "pending"
                }
            }
        ]
    )
    total_slots: int = Field(..., description="Total number of slots", example=2)

class UserCalendarResponse(BaseModel):
    user_id: str = Field(..., description="User ID", example="user_123")
    calendar: List[Dict[str, Any]] = Field(
        default=[], 
        description="User's complete calendar data"
    )

class MonthCalendarResponse(BaseModel):
    user_id: str = Field(..., description="User ID", example="user_123")
    year: int = Field(..., description="Year", example=2025)
    month: int = Field(..., description="Month", example=8)
    dates: List[Dict[str, Any]] = Field(
        default=[], 
        description="Month's calendar data"
    )

class SlotCreateResponse(BaseModel):
    message: str = Field(..., description="Success message", example="Slots created successfully")
    user_id: str = Field(..., description="User ID", example="user_123")
    year: int = Field(..., description="Year", example=2025)
    month: int = Field(..., description="Month", example=8)
    date: int = Field(..., description="Date", example=15)
    slots: List[SlotWithTask] = Field(..., description="Updated list of slots with tasks")

class SlotUpdateResponse(BaseModel):
    """Schema for slot update response"""
    message: str = Field(..., description="Success message", example="Slots updated successfully")
    user_id: str = Field(..., description="User ID", example="user_123")
    year: int = Field(..., description="Year", example=2025)
    month: int = Field(..., description="Month", example=8)
    date: int = Field(..., description="Date", example=15)
    slots: List[SlotWithTask] = Field(..., description="Updated list of slots with tasks")

class TaskAssignResponse(BaseModel):
    """Schema for task assignment response"""
    message: str = Field(..., description="Success message", example="Task assigned successfully")
    user_id: str = Field(..., description="User ID", example="user_123")
    year: int = Field(..., description="Year", example=2025)
    month: int = Field(..., description="Month", example=8)
    date: int = Field(..., description="Date", example=15)
    time_slot: str = Field(..., description="Time slot", example="09:00-10:00")
    task: Task = Field(..., description="Assigned task")

class SlotDeleteResponse(BaseModel):
    """Schema for slot deletion response"""
    message: str = Field(..., description="Success message", example="Slots deleted successfully")
    user_id: str = Field(..., description="User ID", example="user_123")
    year: int = Field(..., description="Year", example=2025)
    month: int = Field(..., description="Month", example=8)
    date: int = Field(..., description="Date", example=15)

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str = Field(..., description="Error message", example="Invalid date provided")

class TaskSearchResponse(BaseModel):
    """Schema for task search response"""
    user_id: str = Field(..., description="User ID", example="user_123")
    tasks: List[Dict[str, Any]] = Field(
        default=[],
        description="List of tasks with their slot information",
        example=[
            {
                "date": "2025-08-15",
                "time_slot": "09:00-10:00",
                "task": {
                    "task_id": "task_001",
                    "title": "Team Meeting",
                    "description": "Weekly sync",
                    "priority": "high",
                    "status": "pending"
                }
            }
        ]
    )