from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession,async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


Db_url = "sqlite+aiosqlite:///./Db/Database.db"
engine = create_async_engine(url=Db_url,echo=True,future=True)

class Base(DeclarativeBase):
    pass

SessionLocal = async_sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)

async def get_Db():
    with SessionLocal() as Session:
        try:
            yield Session
        except Exception as e:
            print(e)
            await Session.rollout()
        finally:
            await Session.close()    


async def create_tables(Drop=False):
   async with engine.begin() as conn:
        Drop and await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

