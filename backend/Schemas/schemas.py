from pydantic import BaseModel, Field, EmailStr, validator, ConfigDict
from datetime import datetime
from typing import Optional, Literal
from enum import Enum

# Enums for better type safety
class TransactionType(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"

# Base User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username must be between 3-50 characters")
    email: EmailStr = Field(..., description="Valid email address")
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$', description="Valid phone number")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    balance: float = Field(..., ge=0, description="User balance, must be non-negative")
    created_at: datetime
    updated_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Wallet Schemas
class WalletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    user_id: int
    balance: float = Field(..., ge=0)
    last_updated: datetime

# Transaction Schemas
class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be positive")
    description: Optional[str] = Field(None, max_length=255)

class TransactionCreate(TransactionBase):
    transaction_type: TransactionType
    recipient_user_id: Optional[int] = Field(None, description="Required for transfer transactions")
    
    @validator('recipient_user_id')
    def validate_recipient_for_transfer(cls, v, values):
        transaction_type = values.get('transaction_type')
        if transaction_type in [TransactionType.TRANSFER_IN, TransactionType.TRANSFER_OUT]:
            if v is None:
                raise ValueError('recipient_user_id is required for transfer transactions')
        return v

class TransactionResponse(TransactionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    transaction_type: TransactionType
    recipient_user_id: Optional[int] = None
    reference_transaction_id: Optional[int] = None
    created_at: datetime

# Money Operations
class AddMoneyRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be positive")
    description: Optional[str] = Field("Add money to wallet", max_length=255)

class WithdrawMoneyRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be positive")
    description: Optional[str] = Field("Withdraw money from wallet", max_length=255)

class TransferRequest(BaseModel):
    recipient_user_id: int = Field(..., description="ID of the recipient user")
    amount: float = Field(..., gt=0, description="Amount must be positive")
    description: Optional[str] = Field("Transfer money", max_length=255)
    
    @validator('recipient_user_id')
    def validate_recipient_id(cls, v):
        if v <= 0:
            raise ValueError('recipient_user_id must be a positive integer')
        return v

class MoneyOperationResponse(BaseModel):
    transaction_id: int
    user_id: int
    amount: float
    new_balance: float
    transaction_type: TransactionType
    description: Optional[str] = None
    created_at: datetime

# Pagination
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number, starts from 1")
    limit: int = Field(default=10, ge=1, le=100, description="Items per page, max 100")

class PaginatedTransactionResponse(BaseModel):
    transactions: list[TransactionResponse]
    total: int
    page: int
    limit: int
    total_pages: int

# API Response wrappers
class SuccessResponse(BaseModel):
    message: str
    data: Optional[dict] = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None