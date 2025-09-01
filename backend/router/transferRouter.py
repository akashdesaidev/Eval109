from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from Services.trasnactionServices import TransactionServices
from Schemas.schemas import TransferRequest, MoneyOperationResponse
from db.db import get_db

router = APIRouter(prefix="/transfers", tags=["transfers"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MoneyOperationResponse)
async def transfer_funds(
    sender_user_id: int, 
    transfer_data: TransferRequest, 
    db: AsyncSession = Depends(get_db)
):
    """Transfer funds from one user to another"""
    transaction_service = TransactionServices(db)
    
    transfer_transaction = await transaction_service.transfer(
        from_user_id=sender_user_id,
        to_user_id=transfer_data.recipient_user_id,
        amount=transfer_data.amount,
        description=transfer_data.description
    )
    
    if not transfer_transaction:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transfer failed")
    
    # Get updated sender balance
    from sqlalchemy import select
    from Models.Model import User
    result = await db.execute(select(User).filter(User.id == sender_user_id))
    sender = result.scalar_one_or_none()
    
    return MoneyOperationResponse(
        transaction_id=transfer_transaction.id,
        user_id=transfer_transaction.user_id,
        amount=transfer_transaction.amount,
        new_balance=sender.balance,
        transaction_type=transfer_transaction.transaction_type,
        description=transfer_transaction.description,
        created_at=transfer_transaction.created_at
    )
