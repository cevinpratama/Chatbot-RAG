from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(tittle = "Chatbot Engine")

class ChatRequest(BaseModel):
    user_message: str

class ChatResponse(BaseModel):
    bot_reply: str
    
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):

    reply_text = f"Pesan Anda diterima: '{request.user_message}'. (Logika AI belum aktif)"
    
    return ChatResponse(bot_reply=reply_text)