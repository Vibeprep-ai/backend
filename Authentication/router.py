import os
from pymongo import MongoClient
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import random
import string
from .schema import (
    UserSignupRequest,
    OTPVerificationRequest,
    OTPResendRequest,
    LoginRequest,
    UserResponse,
    LoginResponse,
    MessageResponse,
)
from .email_config import send_otp_email

# Load environment variables
load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Database connection
client = MongoClient(MONGODB_URL)
db = client[DATABASE_NAME]
users_collection = db["users"]
otp_collection = db["otp_verification"]

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Initialize router
router = APIRouter(prefix="/auth", tags=["Authentication"])


# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/signup", response_model=MessageResponse)
async def signup(user_data: UserSignupRequest):
    """
    Register a new user and send OTP for email verification.
    Steps: Check if user exists -> Hash password -> Generate OTP -> Store temporarily -> Send OTP email
    """
    # Check if user already exists
    existing_user = users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Prepare user data for temporary storage
    hashed_password = hash_password(user_data.password)
    temp_user_data = {
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "email": user_data.email,
        "phone_number": user_data.phone_number,
        "password": hashed_password,
        "class_name": user_data.class_name,
        "target_exam": user_data.target_exam,
        "is_verified": False,
        "created_at": datetime.utcnow(),
    }

    # Generate OTP and store with user data temporarily
    otp = generate_otp()
    otp_record = {
        "email": user_data.email,
        "otp": otp,
        "user_data": temp_user_data,
        "expires_at": datetime.utcnow() + timedelta(minutes=10),
        "created_at": datetime.utcnow(),
    }

    # Remove any existing OTP records for this email
    otp_collection.delete_many({"email": user_data.email})

    # Store new OTP record
    otp_collection.insert_one(otp_record)

    # Send OTP email with error handling
    try:
        await send_otp_email(user_data.email, otp, user_data.first_name)
    except Exception as e:
        # Clean up OTP record if email fails
        otp_collection.delete_one({"email": user_data.email})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification email: {str(e)}",
        )

    return MessageResponse(
        message="OTP sent to your email. Please verify to complete registration."
    )


@router.post("/verify-otp", response_model=UserResponse)
async def verify_otp(verification_data: OTPVerificationRequest):
    """
    Verify OTP and complete user registration.
    Steps: Find valid OTP -> Get stored user data -> Create user in database -> Return user info
    """
    # Find valid OTP record
    otp_record = otp_collection.find_one(
        {
            "email": verification_data.email,
            "otp": verification_data.otp,
            "expires_at": {"$gt": datetime.utcnow()},
        }
    )

    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP or OTP has expired",
        )

    # Get user data from OTP record and mark as verified
    user_data = otp_record["user_data"]
    user_data["is_verified"] = True

    # Create user in database
    result = users_collection.insert_one(user_data)

    # Remove OTP record after successful verification
    otp_collection.delete_one({"_id": otp_record["_id"]})

    # Get created user and prepare response
    created_user = users_collection.find_one({"_id": result.inserted_id})
    user_response = UserResponse(
        id=str(created_user["_id"]),
        first_name=created_user["first_name"],
        last_name=created_user["last_name"],
        email=created_user["email"],
        phone_number=created_user["phone_number"],
        class_name=created_user["class_name"],
        target_exam=created_user["target_exam"],
        is_verified=created_user["is_verified"],
        created_at=created_user["created_at"],
    )

    return user_response


@router.post("/resend-otp", response_model=MessageResponse)
async def resend_otp(resend_data: OTPResendRequest):
    """
    Resend OTP for email verification.
    Steps: Check if pending verification exists -> Generate new OTP -> Update record -> Send email
    """
    # Check if there's a pending verification for this email
    existing_record = otp_collection.find_one({"email": resend_data.email})

    if not existing_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending verification found for this email",
        )

    # Generate new OTP and update expiration
    new_otp = generate_otp()
    otp_collection.update_one(
        {"email": resend_data.email},
        {
            "$set": {
                "otp": new_otp,
                "expires_at": datetime.utcnow() + timedelta(minutes=10),
            }
        },
    )

    # Send new OTP email with error handling
    user_data = existing_record["user_data"]
    try:
        await send_otp_email(resend_data.email, new_otp, user_data["first_name"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification email: {str(e)}",
        )

    return MessageResponse(message="New OTP sent to your email")


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """
    Authenticate user and return access token.
    Steps: Find user -> Verify password -> Check verification status -> Generate token -> Return response
    """
    # Find user by email
    user = users_collection.find_one({"email": login_data.email})

    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Check if user is verified
    if not user.get("is_verified", False):
        # Check if there's a pending OTP verification
        pending_verification = otp_collection.find_one({"email": login_data.email})

        if pending_verification:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not verified. Please check your email for OTP verification.",
            )
        else:
            # Generate new OTP for unverified user
            otp = generate_otp()
            user_data_copy = {k: v for k, v in user.items() if k != "_id"}

            otp_record = {
                "email": login_data.email,
                "otp": otp,
                "user_data": user_data_copy,
                "expires_at": datetime.utcnow() + timedelta(minutes=10),
                "created_at": datetime.utcnow(),
            }

            otp_collection.insert_one(otp_record)
            try:
                await send_otp_email(login_data.email, otp, user["first_name"])
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to send verification email: {str(e)}",
                )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account not verified. New OTP sent to your email.",
            )

    # Generate access token
    access_token = create_access_token(data={"sub": user["email"]})

    # Prepare login response
    login_response = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=str(user["_id"]),
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
    )

    return login_response


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = users_collection.find_one({"email": email})
    if user is None:
        raise credentials_exception

    return user
