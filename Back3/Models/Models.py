from Db.db import Base
from sqlalchemy import  Column,Integer,String,DateTime,ForeignKey,func
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True)
    name=Column(String(100),nullable=False)
    email=Column(String(100),nullable=False,unique=True)
    created_at=Column(DateTime,default=func.now())
    updated_at=Column(DateTime,default=func.now(),onupdate=func.now())
    
    blogs=relationship("Blog",back_populates="author")


class Blog(Base):
    __tablename__="blogs"
    id=Column(Integer,primary_key=True)
    title=Column(String(100),nullable=False)
    description=Column(String(1000))
    created_at=Column(DateTime,default=func.now())
    updated_at=Column(DateTime,default=func.now(),onupdate=func.now())    
    author_id=Column(Integer,ForeignKey("users.id"))

    author=relationship("User",back_populates="blogs")