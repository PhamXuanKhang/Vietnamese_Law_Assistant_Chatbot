from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import time

app = FastAPI()

class MessageRequest(BaseModel):
    message: str  # Tin nhắn của người dùng
    context: List[Dict[str, str]]  # Lịch sử chat
    sessionId: str  # ID phiên người dùng
    stream: bool  # Cờ cho chế độ streaming

@app.post("/chat")
async def chat(request: MessageRequest):
    return 

