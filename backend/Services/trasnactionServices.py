from fastapi import HTTPException, status

from backend.Models.Model import User
from Schemas.schemas import Transaction

class TransactionServices():
    def __init__(self, db):
        self.db = db

    def get_user_transactions(self, user_id: int, skip: int = 0, limit: int = 10):
    
        return self.db.query(Transaction).filter(Transaction.user_id == user_id).offset(skip).limit(limit).all()

    def credit(self, user_id: int, amount: float, description: str):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        transaction = self.createTransaction(user_id=user.id, amount=amount, transaction_type="CREDIT", description=description)
        if transaction:
            user.balance += amount
            self.db.commit()
        else:
            self.db.rollback()
        self.db.refresh(transaction)
        return transaction
     

    def withdraw(self, user_id: int, amount: float, description: str):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if user.balance < amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
        transaction = self.createTransaction(user_id=user.id, amount=amount, transaction_type="DEBIT", description=description)
        if transaction:
            user.balance -= amount
            self.db.commit()
        else:
            self.db.rollback()
        self.db.refresh(transaction)
        return transaction

    def transfer(self, from_user_id: int, to_user_id: int, amount: float, description: str):
        from_user = self.db.query(User).filter(User.id == from_user_id).first()
        to_user = self.db.query(User).filter(User.id == to_user_id).first()
        if not from_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="From user not found")
        if not to_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="To user not found")
        if from_user.balance < amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")

        from_user_transaction = self.createTransaction(user_id=from_user.id, recipient_user_id=to_user.id, amount=amount, transaction_type="TRANSFER_OUT", description=description)
        to_user_transaction = self.createTransaction(user_id=to_user.id, recipient_user_id=from_user.id, amount=amount, transaction_type="TRANSFER_IN", description=description)

        if from_user_transaction and to_user_transaction:
            from_user.balance -= amount
            to_user.balance += amount
            self.db.commit()
            self.db.refresh(from_user)
            self.db.refresh(to_user)
        else:
            self.db.rollback()
            self.db.refresh(from_user_transaction)
            return None
        return from_user_transaction


    def createTransaction(self, user_id: int, recipient_user_id: int, amount: float, transaction_type: str, description: str):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if transaction_type == "DEBIT" and user.balance < amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")

        transaction = Transaction(
            user_id=user.id,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
            reference_transaction_id=None,
            recipient_user_id=recipient_user_id if transaction_type in ["TRANSFER_IN", "TRANSFER_OUT"] else None

        )
        self.db.add(transaction)
        self.db.refresh(transaction)
        return transaction