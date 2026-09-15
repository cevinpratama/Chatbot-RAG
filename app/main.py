import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import AsyncGroq


load_dotenv()
app = FastAPI(tittle = "Chatbot Engine")

client = AsyncGroq()

class ChatRequest(BaseModel):
    user_message: str

class ChatResponse(BaseModel):
    bot_reply: str
    
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    messages = [
        {"role": "system", "content": "Anda adalah asisten AI yang ramah, ringkas, dan sangat membantu."},
        {"role": "user", "content": request.user_message}
    ]
    
    try:
        chat_completion = await client.chat.completions.create(
            messages=messages,
            model="groq/compound-mini", 
            temperature=0.7,       
        )
        
        bot_reply = chat_completion.choices[0].message.content
        
    except Exception as e:
        bot_reply = f"Maaf, terjadi kesalahan saat menghubungi AI: {str(e)}"
    
    return ChatResponse(bot_reply=bot_reply)