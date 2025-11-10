import os
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import google.generativeai as genai

# .env 파일 로드 (프로젝트 루트에서)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="BudgetOps AI Chat API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY 환경 변수가 설정되지 않았습니다."
    )

genai.configure(api_key=GEMINI_API_KEY)

# 모델 초기화
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")
model = genai.GenerativeModel(MODEL_NAME)

# 세션 저장소 (메모리 기반, 프로덕션에서는 Redis나 DB 사용 권장)
chat_sessions: dict[str, genai.ChatSession] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # 세션 ID가 없으면 새 세션 생성


class ChatResponse(BaseModel):
    response: str
    session_id: str


class SessionResponse(BaseModel):
    session_id: str


@app.get("/api/ai/health")
async def root():
    return {"message": "BudgetOps AI Chat API"}


@app.post("/api/ai/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    사용자 질의를 받아서 Gemini API로 처리하고 응답 반환
    session_id가 제공되면 기존 세션을 사용, 없으면 새 세션 생성
    """
    try:
        # 세션 ID가 없거나 존재하지 않으면 새 세션 생성
        if not request.session_id or request.session_id not in chat_sessions:
            session_id = str(uuid.uuid4())
            chat_session = model.start_chat(history=[])
            chat_sessions[session_id] = chat_session
        else:
            session_id = request.session_id
            chat_session = chat_sessions[session_id]
        
        # 메시지 전송
        response = chat_session.send_message(request.message)
        
        return ChatResponse(
            response=response.text,
            session_id=session_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채팅 처리 중 오류가 발생했습니다: {str(e)}")


@app.post("/api/ai/chat/session", response_model=SessionResponse)
async def create_session():
    """
    새로운 채팅 세션 생성
    """
    session_id = str(uuid.uuid4())
    chat_session = model.start_chat(history=[])
    chat_sessions[session_id] = chat_session
    return SessionResponse(session_id=session_id)


@app.delete("/api/ai/chat/session/{session_id}")
async def delete_session(session_id: str):
    """
    채팅 세션 삭제
    """
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        return {"message": "세션이 삭제되었습니다."}
    else:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

