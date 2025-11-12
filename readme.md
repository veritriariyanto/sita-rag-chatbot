# RAG API - SITA Manual Book

API berbasis RAG (Retrieval-Augmented Generation) untuk Sistem Informasi Tugas Akhir (SITA) D3 Teknik Informatika menggunakan Google Gemini dan ChromaDB.

## 📋 Daftar Isi

- [Fitur](#fitur)
- [Teknologi](#teknologi)
- [Persyaratan](#persyaratan)
- [Instalasi](#instalasi)
- [Konfigurasi](#konfigurasi)
- [Struktur Project](#struktur-project)
- [Penggunaan](#penggunaan)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## ✨ Fitur

- 🤖 **RAG dengan Gemini 2.0 Flash** - Menggunakan Google Gemini untuk generate jawaban
- 🔍 **Vector Search** - ChromaDB untuk semantic search
- 👥 **Multi-Role Support** - Support Mahasiswa, Dosen, dan Admin
- 🎯 **Role-Based Filtering** - Filter pencarian berdasarkan role
- 📚 **Q&A Format** - Data dalam format pertanyaan-jawaban
- 🚀 **FastAPI** - RESTful API dengan auto-generated docs
- 🔄 **Auto Vector Store** - Otomatis membuat/load vector database

## 🛠️ Teknologi

- **LLM**: Google Gemini 2.0 Flash
- **Embedding**: Sentence Transformers (paraphrase-multilingual-MiniLM-L12-v2)
- **Vector Database**: ChromaDB
- **Framework**: FastAPI
- **Language**: Python 3.10+

## 📦 Persyaratan

- Python 3.10 atau lebih tinggi
- Google API Key (Gemini)
- 4GB RAM minimum
- 2GB disk space untuk model embeddings

## 🚀 Instalasi

### 1. Clone Repository

```bash
git clone <repository-url>
cd RAG
```

### 2. Buat Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

```bash
# Copy example env
copy .example.env .env

# Edit .env dan isi dengan Google API Key Anda
GOOGLE_API_KEY=your_google_api_key_here
```

## ⚙️ Konfigurasi

Edit file `app/config.py` untuk mengubah konfigurasi:

```python
class Settings:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL = "gemini-2.0-flash"
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    VECTOR_DB_PATH = "./chroma_db"
    
    # Data paths per role
    DATA_PATH_MAHASISWA = "data/data_mahasiswa.json"
    DATA_PATH_DOSEN = "data/data_dosen.json"
    DATA_PATH_ADMIN = "data/data_admin.json"
    
    TOP_K_RESULTS = 5  # Jumlah dokumen yang diambil untuk context
```

## 📁 Struktur Project

```
RAG/
├── app/
│   ├── __init__.py
│   ├── config.py           # Konfigurasi aplikasi
│   ├── rag_service.py      # Service untuk RAG logic
│   └── routes.py           # API endpoints
├── data/
│   ├── data_mahasiswa.json # Data Q&A Mahasiswa
│   ├── data_dosen.json     # Data Q&A Dosen
│   └── data_admin.json     # Data Q&A Admin
├── chroma_db/              # Vector database (auto-generated)
├── venv/                   # Virtual environment
├── .env                    # Environment variables
├── .example.env            # Example environment variables
├── .gitignore
├── main.py                 # Entry point aplikasi
├── requirements.txt        # Python dependencies
└── README.md
```

## 🎯 Penggunaan

### Menjalankan Server

```bash
python main.py
```

Server akan berjalan di: **http://localhost:8000**

### Akses Dokumentasi API

Buka browser dan akses:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### 1. Health Check

**GET** `/api/v1/health`

Mengecek status aplikasi dan vector database.

**Response:**
```json
{
  "status": "healthy",
  "model": "gemini-2.0-flash",
  "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
  "vector_db_status": "loaded",
  "data_format": "SITA Q&A JSON (Per Role)",
  "document_count": 73
}
```

### 2. Ask Question

**POST** `/api/v1/ask`

Mengajukan pertanyaan ke sistem RAG.

**Request Body:**
```json
{
  "question": "Bagaimana cara login sebagai admin?",
  "role": "Admin"  // Optional: "Mahasiswa", "Dosen", "Admin", atau null
}
```

**Response:**
```json
{
  "answer": "Untuk login sebagai admin: 1) Buka halaman utama sistem...",
  "sources": [
    {
      "content": "Role: Admin\nCategory: login\nPertanyaan: Bagaimana cara login...",
      "metadata": {
        "type": "qa",
        "role": "Admin",
        "category": "login",
        "question": "Bagaimana cara login sebagai admin?",
        "keywords": "login admin, email admin, password admin"
      }
    }
  ],
  "confidence": "high",
  "total_sources": 3
}
```

## 🧪 Testing

### 1. Testing dengan cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Ask question tanpa role filter
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"Bagaimana cara login?\"}"

# Ask question dengan role filter
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"Bagaimana cara login?\", \"role\": \"Admin\"}"
```

### 2. Testing dengan Python

Buat file `test_api.py`:

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Test health
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Test ask
data = {
    "question": "Bagaimana cara login sebagai admin?",
    "role": "Admin"
}
response = requests.post(f"{BASE_URL}/ask", json=data)
print(response.json()['answer'])
```

### 3. Testing dengan Swagger UI

1. Buka http://localhost:8000/docs
2. Klik endpoint yang ingin ditest
3. Klik "Try it out"
4. Isi request body
5. Klik "Execute"

## 🔧 Troubleshooting

### Vector Store Tidak Update

Jika data JSON berubah tapi vector store tidak update:

```bash
# Hapus vector store
rmdir /s /q chroma_db  # Windows
rm -rf chroma_db       # Linux/Mac

# Restart aplikasi
python main.py
```

### Error: Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Error: Google API Key

Pastikan `.env` berisi API key yang valid:

```bash
GOOGLE_API_KEY=AIzaSy...
```

Get API key di: https://makersuite.google.com/app/apikey

### Error: Memory Issue

Kurangi `TOP_K_RESULTS` di `config.py`:

```python
TOP_K_RESULTS = 3  # Dari 5 ke 3
```

## 📊 Format Data JSON

Setiap file JSON harus mengikuti format berikut:

```json
[
  {
    "id": "adm_001",
    "role": "admin",
    "category": "login",
    "question": "Bagaimana cara login sebagai admin?",
    "answer": "Untuk login sebagai admin: 1) Buka halaman utama...",
    "related_sections": ["login", "dashboard"],
    "keywords": ["login admin", "email admin", "password admin"]
  }
]
```

## 🔄 Update Data

1. Edit file JSON di folder `data/`
2. Hapus folder `chroma_db/`
3. Restart aplikasi

Vector store akan di-rebuild otomatis.

## 👨‍💻 Developer

Dikembangkan untuk SITA - Sistem Informasi Tugas Akhir

## 🤝 Kontribusi

Silakan buat Pull Request atau Issue untuk kontribusi dan bug reports.
