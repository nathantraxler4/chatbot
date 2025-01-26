from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import Message

async def create_messages(messages: List[dict], session: AsyncSession) -> Message:
    """
    Create a new message in the database, returning 200 on success.
    """
    try:
        messages_models = [
            Message(
                author=m["author"],
                content=m["content"]
            ) for m in messages]
        session.add_all(messages_models)
        await session.commit()
        print(f"Messages created: {messages_models}\n")
        return messages_models

    except Exception as e:
        print(f"Unexpected error creating messages: {e}\n")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later."
        )
    
