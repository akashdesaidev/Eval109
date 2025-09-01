from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Model import User, Transaction
from Schemas.schemas import TransactionType
from typing import Optional

class TransactionServices:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_transactions(self, user_id: int, skip: int = 0, limit: int = 10):
        result = await self.db.execute(
            select(Transaction)
            .filter(Transaction.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Transaction.created_at.desc())
        )
        return result.scalars().all()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    async def credit(self, user_id: int, amount: float, description: str = "Credit transaction"):
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        transaction = await self.create_transaction(
            user_id=user.id,
            amount=amount,
            transaction_type=TransactionType.CREDIT,
            description=description
        )
        
        if transaction:
            user.balance += amount
            await self.db.commit()
            await self.db.refresh(transaction)
            await self.db.refresh(user)
        else:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Transaction failed")
        
        return transaction

    async def withdraw(self, user_id: int, amount: float, description: str = "Withdraw transaction"):
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        if user.balance < amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
        
        transaction = await self.create_transaction(
            user_id=user.id,
            amount=amount,
            transaction_type=TransactionType.DEBIT,
            description=description
        )
        
        if transaction:
            user.balance -= amount
            await self.db.commit()
            await self.db.refresh(transaction)
            await self.db.refresh(user)
        else:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Transaction failed")
        
        return transaction

    async def transfer(self, from_user_id: int, to_user_id: int, amount: float, description: str = "Transfer"):
        if from_user_id == to_user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot transfer to yourself")
        
        from_user = await self.get_user_by_id(from_user_id)
        to_user = await self.get_user_by_id(to_user_id)
        
        if not from_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sender user not found")
        if not to_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient user not found")
        
        if from_user.balance < amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")

        try:
            # Create outgoing transaction for sender
            from_user_transaction = await self.create_transaction(
                user_id=from_user.id,
                recipient_user_id=to_user.id,
                amount=amount,
                transaction_type=TransactionType.TRANSFER_OUT,
                description=f"Transfer to {to_user.username}: {description}"
            )
            
            # Create incoming transaction for recipient
            to_user_transaction = await self.create_transaction(
                user_id=to_user.id,
                recipient_user_id=from_user.id,
                amount=amount,
                transaction_type=TransactionType.TRANSFER_IN,
                description=f"Transfer from {from_user.username}: {description}",
                reference_transaction_id=from_user_transaction.id
            )

            # Update reference in from_user_transaction
            from_user_transaction.reference_transaction_id = to_user_transaction.id

            # Update balances
            from_user.balance -= amount
            to_user.balance += amount
            
            await self.db.commit()
            await self.db.refresh(from_user_transaction)
            await self.db.refresh(to_user_transaction)
            await self.db.refresh(from_user)
            await self.db.refresh(to_user)
            
            return from_user_transaction
            
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Transfer failed: {str(e)}")

    async def create_transaction(
        self,
        user_id: int,
        amount: float,
        transaction_type: TransactionType,
        description: str,
        recipient_user_id: Optional[int] = None,
        reference_transaction_id: Optional[int] = None
    ) -> Transaction:
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            transaction_type=transaction_type.value,
            description=description,
            recipient_user_id=recipient_user_id,
            reference_transaction_id=reference_transaction_id
        )
        
        self.db.add(transaction)
        await self.db.flush()  # Get the ID without committing
        return transaction