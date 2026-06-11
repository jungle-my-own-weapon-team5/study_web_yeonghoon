import time

from typing import Annotated
from fastapi import FastAPI, Request, Query, HTTPException, Cookie, Header
from sqlmodel import Field, Session, SQLModel, create_engine, select

app = FastAPI()

@app.get("/test")
async def asd(asd:Annotated[str, Header()], asf:Annotated[str, Cookie()]):
    return True

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mainp:app",host="0.0.0.0",port=8000,reload = True)