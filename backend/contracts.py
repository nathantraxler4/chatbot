from pydantic import BaseModel

class PostMessage(BaseModel):
    message: str

class MessageResponse(BaseModel):
    message: str
