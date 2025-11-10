import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import google.generativeai as genai

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
    raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

genai.configure(api_key=GEMINI_API_KEY)

# 모델 초기화
model = genai.GenerativeModel('gemini-pro')


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    response: str


@app.get("/api/ai/health")
async def root():
    return {"message": "BudgetOps AI Chat API"}


@app.post("/api/ai/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    채팅 메시지를 받아서 Gemini API로 처리하고 응답을 반환합니다.
    히스토리가 있으면 대화 맥락을 유지합니다.
    """
    try:
        # 대화 히스토리 구성
        history = []
        if request.history:
            for msg in request.history:
                # Gemini API 형식에 맞게 히스토리 구성
                if msg.role == "user":
                    history.append({"role": "user", "parts": [msg.content]})
                elif msg.role == "assistant":
                    history.append({"role": "model", "parts": [msg.content]})
        
        # 채팅 세션 시작
        if history:
            chat = model.start_chat(history=history)
        else:
            chat = model.start_chat(history=[])
        
        # 현재 메시지 전송
        response = chat.send_message(request.message)
        
        return ChatResponse(response=response.text)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채팅 처리 중 오류가 발생했습니다: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

