from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from google.genai import errors
from app.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()

class QuestionRequest(BaseModel):
    question: str
    role: Optional[str] = None  # "Mahasiswa", "Dosen", "Admin", or None for all
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Bagaimana cara login sebagai admin?",
                "role": ""
            }
        }

class AnswerResponse(BaseModel):
    answer: str
    sources: list
    confidence: str
    total_sources: int

@router.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    """
    Answer question with optional role filtering
    
    - **question**: Pertanyaan yang ingin ditanyakan
    - **role**: Optional filter by role (Mahasiswa, Dosen, Admin)
    """
    try:
        result = rag_service.answer_question(
            question=request.question,
            role_filter=request.role
        )
        return result
    except errors.APIError as e:
        # Teruskan status Gemini (mis. 503 overload, 429 quota) agar client bisa retry
        raise HTTPException(status_code=e.code or 502, detail=e.message or str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def health_check():
    """Health check endpoint"""
    return rag_service.check_health()