from fastapi import APIRouter,HTTPException,status,Depends
from Services.trasnactionServices import TransactionServices
from db.db import get_db
router=APIRouter(prefix="/transfers", tags=["transfers"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def transfer_funds(sender_user_id: int, recipient_user_id: int, amount: float, description: str, db=Depends(get_db)):
   transaction_service = TransactionServices(db)
   transfer = transaction_service.transfer(
       from_user_id=sender_user_id,
       to_user_id=recipient_user_id,
       amount=amount,
       description=description
   )
   if not transfer:
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transfer failed")
   return transfer
