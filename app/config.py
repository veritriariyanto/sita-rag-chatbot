import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    VECTOR_DB_PATH = "./chroma_db"
    
    # Data paths per role
    DATA_PATH_MAHASISWA = "data/data_mahasiswa.json"
    DATA_PATH_DOSEN = "data/data_dosen.json"
    DATA_PATH_ADMIN = "data/data_admin.json"
    
    TOP_K_RESULTS = 3

settings = Settings()