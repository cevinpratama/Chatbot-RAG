import os
import asyncio
from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()
client = AsyncGroq()

async def tampilkan_model_aktif():
    try:
        print("Mengambil daftar model yang aktif di Groq...")
        models = await client.models.list()
        daftar_model = [model.id for model in models.data]
        
        print("\n=== DAFTAR MODEL YANG BISA DIGUNAKAN ===")
        for m in daftar_model:
            print(f"- {m}")
        print("========================================")
        return {"active model": daftar_model}
            
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        return {"error": str(e)}

# asyncio.run(tampilkan_model_aktif())