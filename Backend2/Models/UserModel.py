from sqlalchemy import Column,Integer,String
from db.db import Base

class User(Base):
    __tablename__="users"
    id=Column(Integer,index=True)
    name=Column(String(100),nullable=False)
    age=Column(Integer)
    
class Post(Base):
    __tablename__="Posts"

    title = Column(String(100),nullable=False)

    


