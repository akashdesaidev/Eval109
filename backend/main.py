from fastapi import FastAPI
import uvicorn
from router import userRouter,transactionsRouter
from db.db import engine, Base
   
app = FastAPI()

app.on_event("startup")
async def startup_db_clien():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(userRouter.router)
app.include_router(transactionRouter.router)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
