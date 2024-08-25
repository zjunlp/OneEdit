from http.client import HTTPResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
import uvicorn, json, datetime
import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from starlette.middleware.cors import CORSMiddleware
import logging
import time
logging.basicConfig(level=logging.INFO)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"])  


class Query(BaseModel):
    text: str

from src.system import *
import numpy as np
import json
import torch
import random
from typing import List, Optional
from pydantic import BaseModel

from fastapi import status
from fastapi import HTTPException
from pydantic import ValidationError



oneedit = OneEdit('/mnt/xzk/OneEdit/hparams.yaml')

class Message(BaseModel):
    role: str
    content: str

class InputData(BaseModel):
    messages: List[Message]
    stream: bool
    model: str
    temperature: float
    presence_penalty: float
    frequency_penalty: float
    top_p: float

@app.post("/v1/chat/completions")
async def chatQuery(input_data: InputData):
    try:
        if input_data.model == "Chat Mode":
            str = oneedit.generate(input_data.messages[-1].content)
        else:
            str = oneedit.edit_knowledge(input_data.messages[-1].content)
        return Response(
        status_code=200,
        content=str,
        media_type="text/plain"
    )
    except ValidationError as e:
        print(f"Validation error: {e.json()}")
        raise HTTPException(status_code=422, detail=json.loads(e.json()))
    except Exception as e:
        print(f"Other error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"status": "fail", "detail": exc.detail})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    print(f"Request validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"status": "fail", "detail": exc.errors()},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    print(f"General error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "detail": str(exc)},
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=2001)

