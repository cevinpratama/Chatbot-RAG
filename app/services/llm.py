from groq import AsyncGroq
from dotenv import load_dotenv
from app.services.memory import memory_manager
import os

class LLMService:
    def __init__(self):
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        self.model_name = "qwen/qwen3.8-27b"
        self.prompt = {
                    "role": "system",
                    "content": "Anda adalah asisten AI korporat sundora finance yang profesional."
                }

    async def generate_response(self, user_message: str, session_id: str) -> str:
        """
        Nantinya, logika RAG (pencarian dokumen di Vector DB) 
        akan disisipkan di dalam fungsi ini sebelum memanggil Groq.
        """
        historylama = memory_manager.get_history(session_id)
        messages = [self.prompt] + historylama + [{"role": "user", "content":user_message}]

        try:
            response = await self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                temperature=0.7,
            )
            bot_reply = response.choices[0].message.content
            memory_manager.add_message(session_id, "user", user_message)
            memory_manager.add_message(session_id, "user", bot_reply)

            return bot_reply
        except Exception as e:
            raise Exception(f"Gagal memanggil LLM: {str(e)}")
        

llm_service = LLMService()