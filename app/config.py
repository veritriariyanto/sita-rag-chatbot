import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    # Urutan fallback, dipisah koma: model berikutnya dipakai kalau sebelumnya 503/429
    # GEMINI_MODEL (lama, satu model) tetap didukung: ditaruh paling depan
    GEMINI_MODELS = [m.strip() for m in ",".join(filter(None, [
        os.getenv("GEMINI_MODEL"),
        os.getenv("GEMINI_MODELS", "gemini-3.5-flash-lite,gemini-3.5-flash,gemini-flash-lite-latest"),
    ])).split(",") if m.strip()]
    GEMINI_MODELS = list(dict.fromkeys(GEMINI_MODELS))  # buang duplikat, urutan tetap
    GEMINI_MODEL = GEMINI_MODELS[0]
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    VECTOR_DB_PATH = "./chroma_db"
    
    # Data paths per role
    DATA_PATH_MAHASISWA = "data/data_mahasiswa.json"
    DATA_PATH_DOSEN = "data/data_dosen.json"
    DATA_PATH_ADMIN = "data/data_admin.json"
    
    TOP_K_RESULTS = 3

settings = Settings()