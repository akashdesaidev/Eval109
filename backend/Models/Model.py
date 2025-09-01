from sqlalchemy import Column, ForeignKey ,Integer, String, Float, DateTime
from datetime import datetime
from db.db import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    phone_number = Column(String)
    balance = Column(Float, default=0.00)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user", foreign_keys="[Transaction.user_id]")
    sent_transactions = relationship("Transaction", back_populates="recipient_user", foreign_keys="[Transaction.recipient_user_id]")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String)
    reference_transaction_id = Column(Integer, ForeignKey("transactions.id"))
    recipient_user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="transactions", foreign_keys=[user_id])
    recipient_user = relationship("User", back_populates="sent_transactions", foreign_keys=[recipient_user_id])
    reference_transaction = relationship("Transaction", remote_side=[id])
   
 