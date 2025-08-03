from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserSignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    password: str
    class_name: str
    target_exam: str


class OTPVerificationRequest(BaseModel):
    email: EmailStr
    otp: str


class OTPResendRequest(BaseModel):
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    class_name: str
    target_exam: str
    is_verified: bool
    created_at: datetime


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str
    first_name: str
    last_name: str


class MessageResponse(BaseModel):
    message: str
