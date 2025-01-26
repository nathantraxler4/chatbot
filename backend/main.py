from dotenv import load_dotenv
load_dotenv()

from typing import Dict, List
from fastapi.responses import JSONResponse

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from contracts import PostMessage, MessageResponse
from database import get_session
from crud_message import create_messages

app = FastAPI()

@app.exception_handler(ConnectionError)
async def database_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Service Error"}
    )

@app.post("/message")
async def post_message(body: PostMessage, session: AsyncSession = Depends(get_session)) -> MessageResponse:
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
            
    messages: List[Dict[str, str]] = [
        {"author": "user", "content": body.message},
        {"author": "chatbot", "content": body.message}
    ]
    await create_messages(messages, session)
    return  MessageResponse(message=messages[1]["content"])
