from transformers import pipeline
import torch

# 한국어 감정 분류 모델 로드 (HuggingFace의 다국어/한국어 모델 활용)
# 모델 예시: 'skt/ko-sbert-base-v1' 또는 감정 전용 모델
print("⏳ 무료 감정 분석 모델을 로드 중입니다. 잠시만 기다려주세요...")
classifier = pipeline(
    "text-classification", 
    model="j-hartmann/emotion-english-distilroberta-base" # 한국어 지원 모델로 교체 가능
)

# 한국어 감정 매핑 사전 (모델 결과에 따라 조정)
EMOTION_MAP = {
    "joy": "기쁨",
    "sadness": "슬픔",
    "fear": "불안",
    "anger": "화남",
    "surprise": "놀람",
    "disgust": "거부감",
    "neutral": "평온"
}

def analyze_senior_emotion(user_input: str):
    """
    HuggingFace 모델을 사용하여 감정을 추론하고 맞춤형 공감 응답을 반환합니다.
    """
    try:
        # 모델 예측
        prediction = classifier(user_input)[0]
        label = prediction['label']
        emotion_ko = EMOTION_MAP.get(label, "평온")

        # 감정별 고정 공감 멘트 (Rule-based Response)
        responses = {
            "기쁨": "어르신의 기분 좋은 소식을 들으니 저도 행복해지네요! 늘 오늘만 같으셨으면 좋겠어요.",
            "슬픔": "많이 적적하고 마음이 아프시군요.. 제가 옆에서 이야기를 들어드릴게요. 힘내세요.",
            "아픔": "몸이 편치 않으셔서 걱정이에요. 무리하지 마시고 꼭 쉬셔야 해요.",
            "평온": "평온한 하루를 보내고 계시는군요. 저와 함께 재미있는 퀴즈 하나 풀어보시겠어요?"
        }

        return {
            "emotion": emotion_ko,
            "ai_response": responses.get(emotion_ko, "말씀해 주셔서 감사해요. 제가 늘 곁에 있을게요.")
        }
    except Exception as e:
        return {"emotion": "분석 중", "ai_response": "어르신, 다시 한번 천천히 말씀해 주시겠어요?"}