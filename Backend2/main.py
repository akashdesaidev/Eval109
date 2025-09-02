from fastapi import FastAPI
import uvicorn
from db.db import get_Db,create_tables
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("🔄 Recreating database tables with updated schema...")
    await create_tables()
    print("✅ Database tables recreated successfully!")
    yield

app = FastAPI(lifespan=lifespan)

app.get("/")
def healthCheck():
    return "api is heathy"

if __name__ == "__main__":
      uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)