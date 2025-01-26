from typing import Tuple
from pydantic import BaseModel

from models import MessageModel

class PostMessage(BaseModel):
    message: str

class MessageContract(BaseModel):
    id: int
    author: str
    message: str

    @classmethod
    def from_model(
        self,
        message_model: MessageModel
    ) -> "MessageExchange":
        """
        Alternative constructor to create MessageContract from MessageModel.
        """
        
        return MessageContract(id=message_model.id, author=message_model.author, message=message_model.content)

class MessageExchange(BaseModel):
    exchange: Tuple[MessageContract, MessageContract]

    @classmethod
    def from_models(
        self,
        message_models: Tuple[MessageModel, MessageModel],
    ) -> "MessageExchange":
        """
        Alternative constructor to create MessageExchange from MessageModel instances.
        """
        if len(message_models) != 2:
            raise ValueError("Exactly two messages and two IDs are required.")
        
        message_contracts = (
            MessageContract.from_model(message_models[0]),
            MessageContract.from_model(message_models[1])
        )
        return self(exchange=message_contracts)
