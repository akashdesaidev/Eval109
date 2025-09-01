from fastapi import APIRouter, Depends,HTTPException,status    
from Models.Model import User
from Schemas.schemas import UserUpdate
from db.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter(prefix="/users",tags=["users"])

@router.get("/")
async def get_users(db: AsyncSession = Depends(get_db)):
    
        users = await db.execute(select(User))
        users = users.scalars().all()
        return users

@router.get("/{user_id}")
async def get_user(user_id: int,db: AsyncSession = Depends(get_db)):
        user = await db.execute(select(User).filter(User.id == user_id))
        user = user.scalar_one_or_none()
        return user

@router.post("/")
async def create_user(user: User,db: AsyncSession = Depends(get_db),status_code: int = status.HTTP_201_CREATED):
        db.add(user)
        await db.commit()
        return user 

@router.put("/{user_id}")
async def update_user(user_id: int, UserUpdate: UserUpdate,db: AsyncSession = Depends(get_db)):
        user = await db.execute(select(User).filter(User.id == user_id))
        user = user.scalar_one_or_none()
        user.username = UserUpdate.username if UserUpdate.username else user.username
        user.phone_number = UserUpdate.phone_number if UserUpdate.phone_number else user.phone_number
        await db.commit()
        return user     