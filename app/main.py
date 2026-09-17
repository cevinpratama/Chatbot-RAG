from fastapi import FastAPI
import os
from dotenv import load_dotenv
load_dotenv()
from app.services.rag import rag_manager

from app.api.chat import router as chat_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Enterprise RAG Chatbot API",
        description="Backend chatbot terskala dengan arsitektur modular.",
        version="1.0.0"
    )
    data_file_path = os.path.join(os.getcwd(), "data", "datarag.txt")
    rag_manager.ingest_document(data_file_path)

    app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])

    return app

app = create_app()