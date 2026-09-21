# app/schemas/chat.py
from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_message: str
    session_id: str = "default_session" 
    
class ChatResponse(BaseModel):
    bot_reply: str

class EditRAG(BaseModel):
    new_text: str
    doc_id: str