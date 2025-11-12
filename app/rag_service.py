import os
import json
import google.generativeai as genai
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from app.config import settings

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)

class RAGService:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'}
        )
        self.vectorstore = None
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize or load vector store"""
        if os.path.exists(settings.VECTOR_DB_PATH):
            print("📦 Loading existing vector store...")
            self.vectorstore = Chroma(
                persist_directory=settings.VECTOR_DB_PATH,
                embedding_function=self.embeddings
            )
            print(f"✅ Loaded {self.vectorstore._collection.count()} documents")
        else:
            print("🔄 Creating new vector store...")
            self.vectorstore = self._create_vectorstore()
    
    def _load_json_file(self, filepath: str, role_name: str):
        """Load documents from a single JSON file"""
        if not os.path.exists(filepath):
            print(f"⚠️ File not found: {filepath}")
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")
            return []
        
        documents = []
        
        # Data should be array of Q&A objects
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and 'data' in data:
            items = data['data']
        else:
            print(f"⚠️ Invalid JSON structure in {filepath}")
            return []
        
        print(f"   Processing {role_name}: {len(items)} items")
        
        for idx, item in enumerate(items, 1):
            try:
                # Build content from Q&A format
                content_parts = [
                    f"Role: {role_name}",
                    f"Category: {item.get('category', 'N/A')}",
                    f"\nPertanyaan: {item.get('question', '')}",
                    f"\nJawaban: {item.get('answer', '')}"
                ]
                
                # Add keywords
                keywords = item.get('keywords', [])
                if keywords:
                    content_parts.append(f"\nKeywords: {', '.join(keywords)}")
                
                # Add related sections
                related = item.get('related_sections', [])
                if related:
                    content_parts.append(f"Related: {', '.join(related)}")
                
                content = "\n".join(content_parts)
                
                # Create document
                doc = Document(
                    page_content=content,
                    metadata={
                        'id': item.get('id', f"{role_name.lower()}_{idx}"),
                        'type': 'qa',
                        'role': role_name,
                        'category': item.get('category', 'general'),
                        'question': item.get('question', ''),
                        'keywords': ', '.join(keywords),
                        'related_sections': ', '.join(related)
                    }
                )
                documents.append(doc)
            
            except Exception as e:
                print(f"      ⚠️ Error processing item {idx}: {e}")
                continue
        
        print(f"      ✅ {role_name}: {len(documents)} documents loaded")
        return documents
    
    def _load_json_documents(self):
        """Load documents from all JSON files"""
        all_documents = []
        
        print("📖 Loading data from JSON files...\n")
        
        # Load Mahasiswa data
        mahasiswa_docs = self._load_json_file(
            settings.DATA_PATH_MAHASISWA, 
            "Mahasiswa"
        )
        all_documents.extend(mahasiswa_docs)
        
        # Load Dosen data
        dosen_docs = self._load_json_file(
            settings.DATA_PATH_DOSEN,
            "Dosen"
        )
        all_documents.extend(dosen_docs)
        
        # Load Admin data
        admin_docs = self._load_json_file(
            settings.DATA_PATH_ADMIN,
            "Admin"
        )
        all_documents.extend(admin_docs)
        
        print(f"\n✅ Total loaded: {len(all_documents)} documents")
        print(f"   - Mahasiswa: {len(mahasiswa_docs)}")
        print(f"   - Dosen: {len(dosen_docs)}")
        print(f"   - Admin: {len(admin_docs)}")
        
        return all_documents
    
    def _create_vectorstore(self):
        """Create vector store from JSON documents"""
        documents = self._load_json_documents()
        
        if not documents:
            raise ValueError("❌ No documents loaded from JSON files!")
        
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=settings.VECTOR_DB_PATH
        )
        print(f"\n✅ Vector store created with {len(documents)} documents")
        return vectorstore
    
    def answer_question(self, question: str, role_filter: str = None):
        """Answer question using RAG with optional role filtering"""
        # 1. Retrieve relevant documents
        search_kwargs = {"k": settings.TOP_K_RESULTS}
        
        # Add role filter if specified
        if role_filter:
            search_kwargs["filter"] = {"role": role_filter}
        
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs=search_kwargs
        )
        docs = retriever.invoke(question)
        
        # Debug logging
        print(f"\n🔍 Retrieved {len(docs)} documents for: '{question}'")
        if role_filter:
            print(f"   (Filtered by role: {role_filter})")
        
        for i, doc in enumerate(docs, 1):
            role = doc.metadata.get('role', 'N/A')
            category = doc.metadata.get('category', 'N/A')
            print(f"   {i}. [{role}] Category: {category}")
        
        if not docs:
            return {
                'answer': "Maaf, saya tidak menemukan informasi yang relevan dalam dokumentasi SITA.",
                'sources': [],
                'confidence': 'low',
                'total_sources': 0
            }
        
        # 2. Create context from documents
        context_parts = []
        for doc in docs:
            role = doc.metadata.get('role', 'N/A')
            category = doc.metadata.get('category', 'N/A')
            metadata_info = f"[{role} - {category}]"
            
            context_parts.append(f"{metadata_info}\n{doc.page_content}")
        
        context = "\n\n---\n\n".join(context_parts)
        
        # 3. Create enhanced prompt
        role_context = f" khusus untuk role {role_filter}" if role_filter else ""
        
        prompt = f"""Kamu adalah asisten AI untuk Sistem Informasi Tugas Akhir (SITA) D3 Teknik Informatika{role_context}. 

INSTRUKSI:
- Gunakan SEMUA informasi dari konteks yang diberikan untuk menjawab pertanyaan
- Berikan jawaban yang LENGKAP dan DETAIL
- Jika ada langkah-langkah, tampilkan dalam format numbered list
- Jika informasi tidak tersedia dalam konteks, katakan "Maaf, saya tidak menemukan informasi tersebut dalam dokumentasi SITA."

Konteks dari Manual Book SITA:
{context}

Pertanyaan: {question}

Berikan jawaban yang:
1. Jelas dan langsung menjawab pertanyaan
2. Terstruktur dengan numbered list untuk langkah-langkah
3. Menyebutkan informasi penting jika ada
4. Dalam Bahasa Indonesia yang mudah dipahami"""
        
        # 4. Generate answer
        response = self.model.generate_content(prompt)
        
        # Calculate confidence
        confidence = "high" if len(docs) >= 3 else "medium" if len(docs) >= 2 else "low"
        
        return {
            'answer': response.text,
            'sources': [
                {
                    'content': doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                    'metadata': {
                        'type': doc.metadata.get('type', 'qa'),
                        'role': doc.metadata.get('role', 'N/A'),
                        'category': doc.metadata.get('category', 'N/A'),
                        'question': doc.metadata.get('question', 'N/A'),
                        'keywords': doc.metadata.get('keywords', 'N/A')
                    }
                }
                for doc in docs
            ],
            'confidence': confidence,
            'total_sources': len(docs)
        }
    
    def check_health(self):
        """Check service health"""
        return {
            'status': 'healthy',
            'model': settings.GEMINI_MODEL,
            'embedding_model': settings.EMBEDDING_MODEL,
            'vector_db_status': 'loaded' if self.vectorstore else 'not loaded',
            'data_format': 'SITA Q&A JSON (Per Role)',
            'document_count': self.vectorstore._collection.count() if self.vectorstore else 0
        }