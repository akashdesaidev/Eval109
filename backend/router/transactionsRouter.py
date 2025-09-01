from fastapi import APIRouter,status,HTTPException,Depends
from Models.Model import Transaction
from Schemas.schemas import TransactionResponse,TransactionCreateRequest
from Services.trasnactionServices import TransactionServices
from db.db import get_db
router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/{user_id}")
def get_user_transactions(user_id: int, page: int = 1, limit: int = 10, db=Depends(get_db)):

    # get all user transactions

    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    total = query.count()
    transactions = query.offset((page - 1) * limit).limit(limit).all()
    return {
        "transactions": [
            {
                "transaction_id": tx.id,
                "transaction_type": tx.transaction_type,
                "amount": tx.amount,
                "description": tx.description,
                "created_at": tx.created_at
            }
            for tx in transactions
        ],
        "total": total,
        "page": page,
        "limit": limit
    }       


@router.get("/detail/{transaction_id}", status_code=status.HTTP_200_OK) 
def get_transaction_detail(transaction_id: int, db=Depends(get_db)):

    # get single transaction detail

    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return {
        "transaction_id": transaction.id,
        "user_id": transaction.user_id,
        "transaction_type": transaction.transaction_type,
        "amount": transaction.amount,
        "description": transaction.description,
        "recipient_user_id": transaction.recipient_user_id,
        "reference_transaction_id": transaction.reference_transaction_id,
        "created_at": transaction.created_at
    }   


@router.post("/", response_class=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction: TransactionCreateRequest, db=Depends(get_db)):

    # credit or debit transaction transfer router to send money to someone else

   transaction_service = TransactionServices(db)
   if transaction.transaction_type == "CREDIT":
       transaction = transaction_service.credit(user_id=transaction.user_id, amount=transaction.amount, description=transaction.description)
   elif transaction.transaction_type == "DEBIT":
       transaction = transaction_service.withdraw(user_id=transaction.user_id, amount=transaction.amount, description=transaction.description)
   return transaction
