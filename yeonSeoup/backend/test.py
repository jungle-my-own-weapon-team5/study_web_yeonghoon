from fastapi import FastAPI, Query, Depends
from pydantic import BaseModel
from typing import Annotated
from functools import lru_cache

from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column,DeclarativeBase
from sqlalchemy import create_engine, Column, Integer, String, MetaData,select, ForeignKey


app = FastAPI()

# 1. Engine 생성
engine = create_engine("postgresql+psycopg2://app:1q2w3e4r!@localhost:5432/ai_app")


# 2. Base 객체 생성
# v1
# Base = declarative_base()

# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key = True)
#     name = Column(String)
#     age = Column(Integer)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id : Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    name:Mapped[str]
    age: Mapped[int]
    fullname:Mapped[str|None] = mapped_column(nullable=True)

Base.metadata.create_all(engine)

Session = sessionmaker(bind = engine,autoflush=False)
session = Session()

user = User(
    name = "Curie Marie",
    age = 25, 
    fullname = "Curie Marie"
)

session.add(user)
session.commit()
1
session.delete(user)
session.commit()
session.close()



# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("test:app",host="0.0.0.0", port=8000,reload=True)