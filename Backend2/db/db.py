from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase

db_url="sqlite+aiosqlite:///./db/database.db"

engine = create_async_engine(url=db_url,echo=True,future=True)
LocalSession = async_sessionmaker(bind=engine,expire_on_commit=False,class_=AsyncSession)
class Base(DeclarativeBase):
    pass

async def get_Db():
    async with LocalSession() as db:
        try:
            yield db
        except Exception as e:
           await db.rollback()
        finally:
           await  db.close()    

async def create_tables():
    async with engine.begin() as conn:
       await conn.run_sync(Base.metadata.drop_all)
       await conn.run_sync(Base.metadata.create_all)