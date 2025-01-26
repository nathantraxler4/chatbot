from select import select
from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import MessageModel

async def create_messages(messages: List[dict], session: AsyncSession) -> MessageModel:
    """
    Create a new message in the database, returning 200 on success.
    """
    try:
        messages_models = [
            MessageModel(
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

async def update_message(message_id: int, new_content: str, session: AsyncSession) -> MessageModel:
    """
    Update message with message_id in the database, returning 200 on success.
    """
    try:
        # Update the message content
        db_message = await session.get(MessageModel, message_id)
        if db_message == None:
            raise HTTPException(
                status_code=404,
                detail=f"Could not find and message with id {message_id}"
            )
        db_message.content = new_content
        await session.commit()
        await session.refresh(db_message)
        print(f"Message with id: {message_id} updated!\n")
        return db_message
    
    except HTTPException as e:
        print(f"Unexpected error creating messages: {e}\n")
        raise e

    except Exception as e:
        print(f"Unexpected error creating messages: {e}\n")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later."
        )
    

