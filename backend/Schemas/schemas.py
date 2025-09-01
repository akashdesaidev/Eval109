from pydantic import BaseModel,Field
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: int
    username: str
    email: str
    password: str
    phone_number: str
    balance: float
    created_at: datetime
    updated_at: datetime

class UserCreate(User):
   pass
    
class UserUpdate(User):
    username: Optional[str] = None
    phone_number: Optional[str] = None
    
class UserResponse(User):
   from_attributes = True

class Wallet(BaseModel):
    user_id: int
    balance: float
    last_updated: datetime

class WalletResponse(Wallet):
   from_attributes = True


class AddMoneyRequest(BaseModel):
    amount: float
    description: str
class AddMoneyResponse(BaseModel):
    transaction_id: int
    user_id: int
    amount: float
    new_balance: float
    transaction_type: str

    from_attributes = True


class TransactionCreateRequest(BaseModel):
    user_id: int
    transaction_type: str = Field(..., regex="^(CREDIT|DEBIT|TRANSFER_IN|TRANSFER_OUT)$")
    amount: float
    description: Optional[str] = None,
    recipient_user_id: int = Field(..., description="Recipient user ID for transfer transactions")

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    transaction_type: str = Field(..., regex="^(CREDIT|DEBIT|TRANSFER_IN|TRANSFER_OUT)$")
    amount: float
    description: Optional[str] = None
    recipient_user_id: Optional[int] = None
    created_at: datetime

    from_attributes = True