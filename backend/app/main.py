from datetime import datetime, timedelta
from typing import Annotated

from sqlalchemy.orm import DeclarativeBase, Mapped, sessionmaker, mapped_column, Session
from sqlalchemy import create_engine, MetaData, select, func

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import jwt
from pwdlib import PasswordHash
import secrets



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

engine = create_engine("postgresql+psycopg2://app:1q2w3e4r!@localhost:5432/ai_app")

SessionLocal = sessionmaker(bind = engine, autocommit=False, autoflush=False)

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

session = SessionLocal()
Base.metadata.create_all(bind=engine)
test_object = User(**test_db_dict["wick"])
test_data = session.scalar(select(User).where(User.user_id == test_db_dict["wick"]["user_id"]))
if test_data is None:
    session.add(test_object)
    session.commit()
session.close()




DUMMY_HASHED_PASSWORD = password_hash.hash("DUMMY")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def get_current_user(token:Annotated[str, Depends(oauth2_scheme)],session:Annotated[Session,Depends(get_session)]):
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
    user = get_user(session, token_data.username)
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

def get_user(session:Session, username:str):
    # user 찾기, 현재는 그냥 dict로 구현
    user = session.scalar(select(User).where(User.user_id == username))
    if user is not None:
        return user

def authenticate_user(session:Session, username:str, password:str)->User:
    user = get_user(session, username)
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
async def get_login_token(formdata:Annotated[OAuth2PasswordRequestForm, Depends()])->Token:
    # formdata.grant_type == "password" # 추후 grant_type을 다르게 처리하면 로직 추가 / authorization_code / refresh_token / client_credentials

    username = formdata.username
    password = formdata.password
    userdata = authenticate_user(session, username, password) # db 고치기
    
    access_token = create_access_token(data = {"sub":userdata.user_id})
    return_token = Token(access_token=access_token, token_type="bearer")

    return return_token



# @app.get("/refresh_token")
# def refresh_login_token(token:Annotated[str,Depends()]):

# 서버 시작

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app",host="0.0.0.0",port=8000,reload=True)

