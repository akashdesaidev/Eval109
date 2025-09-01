from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from Models.Model import Transaction
from Schemas.schemas import (
    TransactionResponse, 
    TransactionCreate, 
    PaginationParams, 
    PaginatedTransactionResponse
)
from Services.trasnactionServices import TransactionServices
from db.db import get_db

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("/{user_id}", response_model=PaginatedTransactionResponse)
async def get_user_transactions(
    user_id: int, 
    page: int = 1, 
    limit: int = 10, 
    db: AsyncSession = Depends(get_db)
):
    """Get all user transactions with pagination"""
    offset = (page - 1) * limit
    
    # Get total count
    total_result = await db.execute(
        select(func.count(Transaction.id)).filter(Transaction.user_id == user_id)
    )
    total = total_result.scalar()
    
    # Get transactions
    result = await db.execute(
        select(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    transactions = result.scalars().all()
    
    total_pages = (total + limit - 1) // limit
    
    return PaginatedTransactionResponse(
        transactions=transactions,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )

@router.get("/detail/{transaction_id}", status_code=status.HTTP_200_OK, response_model=TransactionResponse) 
async def get_transaction_detail(transaction_id: int, db: AsyncSession = Depends(get_db)):
    """Get single transaction detail"""
    result = await db.execute(select(Transaction).filter(Transaction.id == transaction_id))
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    
    return transaction

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction_data: TransactionCreate, user_id: int, db: AsyncSession = Depends(get_db)):
    """Create a credit or debit transaction"""
    transaction_service = TransactionServices(db)
    
    if transaction_data.transaction_type == "CREDIT":
        transaction = await transaction_service.credit(
            user_id=user_id, 
            amount=transaction_data.amount, 
            description=transaction_data.description
        )
    elif transaction_data.transaction_type == "DEBIT":
        transaction = await transaction_service.withdraw(
            user_id=user_id, 
            amount=transaction_data.amount, 
            description=transaction_data.description
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Only CREDIT and DEBIT transactions are allowed. Use transfer endpoint for transfers."
        )
    
    return transaction
