from dotenv import load_dotenv
load_dotenv()
from jose import JWTError
import uvicorn
import os
from typing import Dict, List
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware

from contracts import MessageExchange, PostMessage, MessageContract
from database import get_session
from crud_message import create_messages, update_message, delete_message

from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cors_headers = {
    "Access-Control-Allow-Origin": "http://localhost:5173",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
}

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try: 
            token = request.headers.get("Authorization")
            if token:
                token = token.split(" ")[-1]  # Remove "Bearer" part
                try:
                    request.state.user = supabase.auth.get_user(token)
                except JWTError:
                    raise HTTPException(status_code=401, detail="Invalid token")
            else:
                raise HTTPException(status_code=401, detail="Authorization token missing")
            
            response = await call_next(request)
            return response
    
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail},
                headers=cors_headers,
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"},
                headers=cors_headers,
            )
        
app.add_middleware(AuthMiddleware)

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

@app.delete("/message/{message_id}")
async def remove_message(message_id: int, session: AsyncSession = Depends(get_session)) -> bool:
    is_deleted = await delete_message(message_id, session)
    return is_deleted

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
