from fastapi import FastAPI
import uvicorn
from Db.db import create_tables
from Models.Models import User
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_tables(Drop=True)
    yield
    
app=FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    uvicorn.run("main:app",port=8000,host="0.0.0.0",reload=True)
