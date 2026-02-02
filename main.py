from fastapi import FastAPI, Query
from app.external_api import get_nearby_pharmacy  # 위에서 만든 함수 불러오기
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# 바로 여기가 "엔드포인트 연결" 코드입니다!
@app.get("/pharmacy")
async def find_pharmacy(city: str, area: str):
    # external_api.py에 있는 함수를 실행해서 데이터를 받아옴
    result = get_nearby_pharmacy(city, area)
    return result