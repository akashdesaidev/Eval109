from fastapi import APIRouter, Depends, HTTPException, status    
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Model import User
from Schemas.schemas import UserCreate, UserUpdate, UserResponse, AddMoneyRequest, WithdrawMoneyRequest, MoneyOperationResponse
from Services.trasnactionServices import TransactionServices
from db.db import get_db
import bcrypt

router = APIRouter(prefix="/users", tags=["users"])

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

@router.get("/", status_code=status.HTTP_200_OK, response_model=list[UserResponse])
async def get_users(db: AsyncSession = Depends(get_db)):
    """Get all users"""
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific user by ID"""
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user"""
    # Check if username or email already exists
    existing_user = await db.execute(
        select(User).filter((User.username == user_data.username) | (User.email == user_data.email))
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username or email already exists"
        )
    
    # Hash the password
    hashed_password = hash_password(user_data.password)
    
    # Create new user
    user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        phone_number=user_data.phone_number,
        balance=0.0
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):
    """Update user information"""
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Update only provided fields
    if user_update.username is not None:
        # Check if new username already exists
        existing = await db.execute(
            select(User).filter(User.username == user_update.username, User.id != user_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Username already exists"
            )
        user.username = user_update.username
    
    if user_update.phone_number is not None:
        user.phone_number = user_update.phone_number
    
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/{user_id}/add-money", status_code=status.HTTP_201_CREATED, response_model=MoneyOperationResponse)
async def add_money(user_id: int, request: AddMoneyRequest, db: AsyncSession = Depends(get_db)):
    """Add money to user's wallet"""
    transaction_service = TransactionServices(db)
    transaction = await transaction_service.credit(
        user_id=user_id,
        amount=request.amount,
        description=request.description
    )
    
    # Get updated user balance
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    
    return MoneyOperationResponse(
        transaction_id=transaction.id,
        user_id=transaction.user_id,
        amount=transaction.amount,
        new_balance=user.balance,
        transaction_type=transaction.transaction_type,
        description=transaction.description,
        created_at=transaction.created_at
    )

@router.post("/{user_id}/withdraw", status_code=status.HTTP_201_CREATED, response_model=MoneyOperationResponse)
async def withdraw_money(user_id: int, request: WithdrawMoneyRequest, db: AsyncSession = Depends(get_db)):
    """Withdraw money from user's wallet"""
    transaction_service = TransactionServices(db)
    transaction = await transaction_service.withdraw(
        user_id=user_id,
        amount=request.amount,
        description=request.description
    )
    
    # Get updated user balance
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    
    return MoneyOperationResponse(
        transaction_id=transaction.id,
        user_id=transaction.user_id,
        amount=transaction.amount,
        new_balance=user.balance,
        transaction_type=transaction.transaction_type,
        description=transaction.description,
        created_at=transaction.created_at
    )