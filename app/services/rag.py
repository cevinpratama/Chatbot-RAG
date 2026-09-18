import chromadb
from sentence_transformers import SentenceTransformer
import os
import hashlib

class RAGmanager:
    def __init__(self):
        print("Memuat embedding model (wait for sec..)")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        db_path = os.path.join(os.getcwd(), "chroma_db")
        self.chroma_client =chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(name="kebijakan_perusahaan")

    def  get_embedding(self, text:str) -> list:
        """Fungsi pembantu: Mengubah teks menjadi deretan angka (vektor)"""
        return self.embedding_model.encode(text).tolist()

    def ingest_document(self, file_path: str):
        """Fase 1: INGESTION (Membaca file -> Memotong -> Menyimpan ke Vector DB)"""
        if not os.path.exists(file_path):
            print(f"File {file_path} tidak ditemukan!")
            return
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        chunks = [line.strip() for line in lines if line.strip()]

        if self.collection.count() > 0:
            print(f"Database sudah berisi {self.collection.count()} dokumen. Ingestion dilewati.")
            return
        
        print(f"Menyerap {len(chunks)} potongan dokumen ke Vector DB...")
        ids = []
        embeddings = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            vector = self.get_embedding(chunk)
            
            ids.append(f"doc_{i}")
            embeddings.append(vector)
            metadatas.append({"sumber": "datarag.txt"})
            
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        print("Ingestion Selesai!")

    def retrieve_context(self, query: str, k: int = 2) -> str:
        """Fase 2: RETRIEVAL (Mencari dokumen paling relevan dengan pertanyaan)"""
        query_vector = self.get_embedding(query)
        
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=k
        )
        
        retrieved_docs = results["documents"][0]
        
        context = "\n".join(retrieved_docs)
        return context

    def get_doc(self):
        data = self.collection.get()
        ids = data.get("ids",[])
        document = data.get("documents", [])

        if not ids:
            print("kosong bos")
            return []
        print(f"ada {len(ids)} data dalam database")
        for doc_id, doc_text in zip(ids, document):
            print(f"ID :{doc_id} | Text :{doc_text}")
        return list(zip(ids, document))
    
    def edit_document(self, doc_id: str, new_text: str):
        """Mengedit baris tertentu berdasarkan ID, baik di txt maupun di ChromaDB"""
        new_embedding = self.get_embedding(new_text)
        try:
            self.collection.update(
                ids=[doc_id],
                documents=[new_text],
                embeddings=[new_embedding]
            )
            print(f"Vektor DB: Data dengan ID '{doc_id}' berhasil diubah.")
        except Exception as e:
            print(f"Gagal mengubah data di Vector DB. Pastikan ID benar. Error: {e}")
            return
        file_path = os.path.join(os.getcwd(), "data", "datarag.txt")
        if not os.path.exists(file_path):
            print(f"File {file_path} tidak ditemukan untuk diupdate!")
            return
            
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        try:
            chunk_index = int(doc_id.split("_")[1]) 
        except (IndexError, ValueError):
            print("Format ID tidak valid. Pastikan formatnya 'doc_X' (contoh: doc_0).")
            return

        non_empty_indices = [idx for idx, line in enumerate(lines) if line.strip()]
        
        if chunk_index < len(non_empty_indices):
            actual_line_index = non_empty_indices[chunk_index]
            lines[actual_line_index] = new_text + "\n"
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            print(f"File TXT: Baris teks untuk ID '{doc_id}' berhasil diperbarui ke file {file_path}.")
        else:
            print(f"Gagal update file TXT: Indeks {chunk_index} di luar batas baris file.")

    
    
rag_manager = RAGmanager()