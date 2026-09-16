from groq import AsyncGroq
from dotenv import load_dotenv
import os

class LLMService:
    def __init__(self):
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        self.model_name = "qwen/qwen3.8-27b"

    async def generate_response(self, user_message: str, session_id: str) -> str:
        """
        Nantinya, logika RAG (pencarian dokumen di Vector DB) 
        akan disisipkan di dalam fungsi ini sebelum memanggil Groq.
        """
 
        messages = [
            {"role": "system", "content": "Anda adalah asisten AI korporat sundora finance yang profesional."},
            {"role": "user", "content": user_message}
        ]

        try:
            response = await self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Gagal memanggil LLM: {str(e)}")

llm_service = LLMService()