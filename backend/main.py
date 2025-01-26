from dotenv import load_dotenv
import uvicorn
load_dotenv()

from typing import Dict, List
from fastapi.responses import JSONResponse

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from contracts import MessageExchange, PostMessage, MessageContract
from database import get_session
from crud_message import create_messages, update_message

app = FastAPI()

@app.exception_handler(ConnectionError)
async def database_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Service Error"}
    )

@app.post("/message")
async def post_message(body: PostMessage, session: AsyncSession = Depends(get_session)) -> MessageExchange:
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
            
    messages: List[Dict[str, str]] = [
        {"author": "user", "content": body.message},
        {"author": "chatbot", "content": body.message}
    ]
    messages = await create_messages(messages, session)
    return  MessageExchange.from_models(messages)

@app.put("/message/{message_id}")
async def put_message(message_id: int, body: PostMessage, session: AsyncSession = Depends(get_session)) -> MessageContract:
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    updated_message = await update_message(message_id, body.message, session)
    return MessageContract.from_model(updated_message)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
