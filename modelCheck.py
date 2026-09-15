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
        
        print("\n=== DAFTAR MODEL YANG BISA DIGUNAKAN ===")
        for model in models.data:
            print(f"- {model.id}")
        print("========================================")
            
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

asyncio.run(tampilkan_model_aktif())