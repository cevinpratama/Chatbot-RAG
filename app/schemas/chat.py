# app/schemas/chat.py
from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_message: str
    session_id: str = "default_session" 
    new_text: str
    doc_id: str
class ChatResponse(BaseModel):
    bot_reply: str