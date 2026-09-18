from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm import llm_service
from app.services.rag import rag_manager

from app.services.modelCheck import tampilkan_model_aktif

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        reply = await llm_service.generate_response(
            user_message=request.user_message,
            session_id=request.session_id
        )
        return ChatResponse(bot_reply=reply)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/listRAG")
def get_list():
    return rag_manager.get_doc()

@router.post("/edit")
def editrag(new_text, doc_id):
    rag_manager.edit_document(doc_id, new_text)

@router.get("/version")
async def get_modversion():
    return await tampilkan_model_aktif()