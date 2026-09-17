from groq import AsyncGroq
from dotenv import load_dotenv
from app.services.memory import memory_manager
from app.services.rag import rag_manager
import os

class LLMService:
    def __init__(self):
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        self.model_name = "groq/compound-mini"

    async def generate_response(self, user_message: str, session_id: str) -> str:

        retrieved_context = rag_manager.retrieve_context(query=user_message, k=2)
        
        augmented_system_prompt = f"""Anda adalah asisten virtual perusahaan yang akurat dan sopan.
        Anda HANYA boleh menjawab pertanyaan berdasarkan KONTEKS yang diberikan di bawah ini.
        Jika jawaban tidak ditemukan di dalam KONTEKS, katakan "Maaf, saya tidak menemukan informasi tersebut di dokumen kebijakan perusahaan." Jangan pernah mengarang jawaban.
        --- KONTEKS DOKUMEN ---
        {retrieved_context}
        -----------------------
        """
        system_message = {"role": "system", "content": augmented_system_prompt}
        past_history = memory_manager.get_history(session_id)
        messages = [system_message] + past_history + [{"role": "user", "content": user_message}]

        try:
            response = await self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                temperature=0.3,
            )
            bot_reply = response.choices[0].message.content
            memory_manager.add_message(session_id, "user", user_message)
            memory_manager.add_message(session_id, "user", bot_reply)

            return bot_reply
        except Exception as e:
            raise Exception(f"Gagal memanggil LLM: {str(e)}")
        

llm_service = LLMService()