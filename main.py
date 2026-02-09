import logging
import uvicorn
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# 1. 감정 분석 및 그래프 메모리 모듈 임포트
# (app 폴더 내 nlp_engine.py와 같은 폴더 내 graph_memory.py가 있어야 함)
try:
    from app.nlp_engine import analyze_emotion
    from graph_memory import SeniorGraphMemory
except ImportError as e:
    print(f"모듈 임포트 에러: {e}")

# 2. 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 3. FastAPI 앱 생성 (데코레이터 사용을 위해 함수보다 위에 위치)
app = FastAPI()

# 4. 데이터 모델 정의 (ChatRequest 에러 해결)
class ChatRequest(BaseModel):
    text: str

# 5. 그래프 메모리 초기화
try:
    memory = SeniorGraphMemory()
except Exception as e:
    logger.error(f"Neo4j 연결 실패: {e}")
    memory = None

# 안전한 업데이트를 위한 래퍼 함수
def safe_update_knowledge(text: str):
    if memory:
        try:
            memory.update_knowledge(text)
            logger.info("그래프 업데이트 성공")
        except Exception as e:
            logger.error(f"그래프 업데이트 실패: {e}")

# 6. 채팅 통합 엔드포인트
@app.post("/chat")
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    try:
        # A. 감정 분석
        emotion_result = analyze_emotion(request.text)
        
        # B. 그래프 DB 맥락 조회
        context = ""
        if memory:
            context = memory.get_context(request.text)

        # C. 감정별 너스레 조건문 추가
        if emotion_result == "기쁨":
            prefix = "아이고, 우리 어르신 기분이 좋으시니 저도 덩실덩실 춤이 나요! "
        elif emotion_result == "슬픔":
            prefix = "어르신, 목소리가 조금 적적하시네요. 제가 재롱 좀 피워드릴게요. "
        elif emotion_result == "분노":
            prefix = "누가 우리 어르신을 속상하게 했을까! 제가 다 혼내줄게요. "
        else:
            prefix = "네, 어르신! 말씀 잘 듣고 있어요. "

        # D. 최종 답변 조립
        ai_response = f"{prefix} 아까 말씀하신 '{context}' 얘기도 더 들려주세요!"

        # E. 새로운 지식 비동기 저장
        background_tasks.add_task(safe_update_knowledge, request.text)

        return {"ai_response": ai_response}

    except Exception as e:
        logger.error(f"에러 발생: {e}")
        return {"ai_response": "어르신, 제가 잠시 딴생각을 했나 봐요. 다시 말씀해 주세요!"}

# 7. 메인 화면 (HTML)
@app.get("/", response_class=HTMLResponse)
async def get_index():
    return """
    (이전의 HTML 코드 내용)
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)