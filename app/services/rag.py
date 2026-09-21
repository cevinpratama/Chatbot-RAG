import chromadb
from sentence_transformers import SentenceTransformer
import os
from app.core.exceptions import NotFoundException, ServiceUnavailableException, BadRequestException, AppException

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
        if not doc_id.startswith("doc_"):
            raise BadRequestException(
                message="Format ID tidak valid",
                error_code="INVALID_DOC_FORMAT"
            )
        try:
            existing = self.collection.get(ids=[doc_id])
        except Exception as e:
            raise ServiceUnavailableException(
                message=f"Koneksi ke Vector DB gagal: {str(e)}",
                error_code="VECTOR_DB_DOWN"
            )
        try:
            chunk_index = int(doc_id.split("_")[1]) 
        except (IndexError, ValueError):
            raise BadRequestException(
                message="Format angka pada ID tidak valid. Pastikan formatnya 'doc_X' (contoh: doc_0).",
                error_code="INVALID_DOC_INDEX"
            )

        if not existing or not existing.get("ids"):
            raise NotFoundException(
                message=f"Dokumen dengan ID '{doc_id}' tidak ditemukan di database.",
                error_code="DOC_NOT_FOUND"
            )
        
        new_embedding = self.get_embedding(new_text)
        try:
            self.collection.update(
                ids=[doc_id],
                documents=[new_text],
                embeddings=[new_embedding]
            )
        except Exception as e:
            raise ServiceUnavailableException(
            message=f"Gagal mengubah data di Vector DB. Error: {e}",
            error_code="VECTOR_DB_UPDATE_FAILED"
        )
    
        file_path = os.path.join(os.getcwd(), "data", "datarag.txt")

        if not os.path.exists(file_path):
            raise AppException(
            message=f"File referensi sumber tidak ditemukan di server.",
            error_code="SERVER_FILE_MISSING",
            status_code=500
        )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            raise AppException(
            message=f"Gagal membaca file TXT lokal: {str(e)}",
            error_code="FILE_READ_ERROR",
            status_code=500
            )
        non_empty_indices = [idx for idx, line in enumerate(lines) if line.strip()]

        if chunk_index >= len(non_empty_indices):
            raise NotFoundException(
                message=f"Gagal update file TXT: Indeks baris {chunk_index} di luar batas.",
                error_code="TXT_INDEX_OUT_OF_BOUNDS"
            )
        try:
            actual_line_index = non_empty_indices[chunk_index]
            old_text = lines[actual_line_index].strip()
            
            lines[actual_line_index] = new_text + "\n"
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception as e:
            raise AppException(
                message=f"Gagal menulis perubahan ke file TXT: {str(e)}",
                error_code="FILE_WRITE_ERROR",
                status_code=500
            )
        
        return {
                "doc_id": doc_id,
                "old_text": old_text,
                "new_text": new_text,
                "status_db": "updated",
                "status_file": "updated"
            }
    
    
rag_manager = RAGmanager()