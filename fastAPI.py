from fastapi import FastAPI
import uvicorn
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
from chatbot_v1.src.LLM_response.main import process_message
from chatbot_v2.Code.main import process_message_v2

app = FastAPI()

class MessageRequest(BaseModel):
    message: str
    context: List[Dict[str, str]]
    sessionId: str 
    stream: bool

@app.post("/v1/chat")
async def chat(request: MessageRequest):
    """
    Endpoint xử lý yêu cầu chat và stream phản hồi.
    """
    if request.stream:
        def stream_response():
            for chunk in process_message(request.message, request.context):
                yield chunk
        
        return StreamingResponse(stream_response(), media_type="text/plain")
    else:
        full_response = "".join(process_message(request.message, request.context))
        return {"response": full_response, "sessionId": request.sessionId, "context": request.context}
    
@app.post("/v2/chat")
async def chat_v2(request: MessageRequest):
    def stream_response():
        try:
            for chunk in process_message_v2(request.message, request.context):
                yield chunk + "\n"
        except Exception as e:
            yield f"Error: {str(e)}\n"

    if request.stream:
        return StreamingResponse(stream_response(), media_type="text/plain")
    else:
        full_response = "".join(process_message_v2(request.message, request.context))
        return {"response": full_response, "sessionId": request.sessionId, "context": request.context}

uvicorn.run(app, host="0.0.0.0", port=8000)