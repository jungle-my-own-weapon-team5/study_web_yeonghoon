from datetime import datetime, timedelta
from typing import Annotated
from dotenv import load_dotenv
import os

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, sessionmaker, mapped_column, Session
from sqlalchemy import create_engine, MetaData, select, func

from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import jwt
from pwdlib import PasswordHash
import secrets

load_dotenv()

app = FastAPI(title="AI Utilization API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_async_engine(f'{os.getenv("DB_NAME")}+{os.getenv("SQL_ENGINE")}://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@localhost:{os.getenv("DATABASE_PORT")}/{os.getenv("POSTGRES_DB")}',echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)

# db_scheme
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    user_id:Mapped[str] = mapped_column(unique=True)
    nick_name:Mapped[str]
    email:Mapped[str]
    password:Mapped[str]
    name:Mapped[str|None] = mapped_column(nullable=True)
    birthday:Mapped[str|None] = mapped_column(nullable=True)
    disabled:Mapped[bool]

class register_form(BaseModel):
    user_id:str
    nick_name:str
    email:str
    password:str
    name:str|None=Field(default=None)
    birthday:str|None=Field(default=None)
    disabled:bool=Field(default=False)

SECRET_KEY = secrets.token_hex(32)
ALGORYTHM = "HS256"
password_hash = PasswordHash.recommended()

DEFAULT_TOKEN_EXPIRE = 30


def get_secret_key():
    return secrets.token_hex(32)



@app.get("/")
def root():
    return {"message": "FastAPI is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/ping")
def ping():
    return {"message": "pong from FastAPI"}

# 회원가입 / 로그인 토큰 테스트

test_db_dict = {
    "wick": {
        "user_id" : "wick",
        "nick_name" : "jhon wick",
        "email" : "wick@naver.com",
        "password" : password_hash.hash("password"),
        "name": "jhon wick",
        "birthday": "1964-09-02",
        "disabled": False,
    }
}

async def get_session()->AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    
    test_object = User(**test_db_dict["wick"])
    
    async with AsyncSessionLocal() as session:
        test_data = await session.scalar(select(User).where(User.user_id == test_db_dict["wick"]["user_id"]))
        if test_data is None:
            session.add(test_object)
            await session.commit()



DUMMY_HASHED_PASSWORD = password_hash.hash("DUMMY")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")


async def get_current_user(token:Annotated[str, Depends(oauth2_scheme)],session:Annotated[AsyncSession,Depends(get_session)]):
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Coul not validate credentials",
        headers = {"WWW-Authenticate":"Bearer"},
    )
    try:
        payload = jwt.decode(token, key = SECRET_KEY, algorithms = ALGORYTHM)
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username = username)
        if token_data.username is None:
            raise credentials_exception
    except:
        raise credentials_exception
    user = await get_user(session, token_data.username)
    if user is None:
        raise credentials_exception
    return user

def currnet_user_activate(current_user:Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code = 400, detail = "Inactive user")
    return current_user

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    username : str|None = None

def verify_password(plain_password:str,hashed_password:str):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password:str):
    return password_hash.hash(password)

async def get_user(session:AsyncSession, username:str)->User|None:
    # user 찾기, 현재는 그냥 dict로 구현
    user = await session.scalar(select(User).where(User.user_id == username))
    if user is not None:
        return user

async def authenticate_user(session:AsyncSession, username:str, password:str)->User:
    user = await get_user(session, username)
    if user is None:
        verify_password(password, DUMMY_HASHED_PASSWORD)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password", 
            headers={"WWW_Authenticate":"Bearer"}
        )
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password", 
            headers={"WWW_Authenticate":"Bearer"}
        )
    return user

def create_access_token(data:dict, expires_delta:timedelta | None = None):
    to_encode = data.copy()
    if expires_delta is None:
        expire_date = datetime.now() + timedelta(minutes = DEFAULT_TOKEN_EXPIRE)
    else:
        expire_date = datetime.now() + expires_delta
    to_encode.update({"exp":expire_date})
    access_token = jwt.encode(to_encode, SECRET_KEY, ALGORYTHM)
    return access_token

@app.get("/user/me")
async def user_info(user:Annotated[User, Depends(currnet_user_activate)]):
    return user


@app.post("/token")
async def get_login_token(formdata:Annotated[OAuth2PasswordRequestForm, Depends()],session:Annotated[AsyncSession, Depends(get_session)])->Token:
    # formdata.grant_type == "password" # 추후 grant_type을 다르게 처리하면 로직 추가 / authorization_code / refresh_token / client_credentials

    username = formdata.username
    password = formdata.password
    userdata = await authenticate_user(session, username, password) # db 고치기
    
    access_token = create_access_token(data = {"sub":userdata.user_id})
    return_token = Token(access_token=access_token, token_type="bearer")

    return return_token

@app.post("/register")
async def register_client(user_data:Annotated[register_form, Body()],session:Annotated[AsyncSession, Depends(get_session)]):
    dup_check = await session.scalar(select(User).where(User.user_id==user_data.user_id))
    if dup_check is not None:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "이미 사용중인 아이디입니다.")
    hashed_password = password_hash.hash(user_data.password)
    user = User(
        user_id = user_data.user_id,
        nick_name = user_data.nick_name,
        email = user_data.email,
        password = hashed_password,
        name = user_data.name,
        birthday = user_data.birthday,
        disabled = user_data.disabled,
    )
    
    session.add(user)
    await session.commit()

    return {"message":"회원가입 완료"}



# @app.get("/refresh_token")
# def refresh_login_token(token:Annotated[str,Depends()]):

# 서버 시작

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app",host="0.0.0.0",port=8000,reload=True)

