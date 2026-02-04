from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from app.nlp_engine import analyze_emotion
import uvicorn
import os

app = FastAPI()

class ChatRequest(BaseModel):
    text: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # nlp_engine에서 분석 결과 가져오기
    result = analyze_emotion(request.text)
    return result

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>다정한 AI 손주</title>
    <style>
        :root {
            --primary-color: #76ba99;
            --bg-color: #fcf8e8;
            --user-msg: #ffe0ac;
            --bot-msg: #ffffff;
        }
        body { font-family: 'Malgun Gothic', sans-serif; background: var(--bg-color); margin: 0; display: flex; justify-content: center; }
        .container { width: 100%; max-width: 480px; height: 100vh; background: white; display: flex; flex-direction: column; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
        .header { background: var(--primary-color); color: white; padding: 25px; text-align: center; font-size: 1.5rem; font-weight: bold; border-bottom-left-radius: 20px; border-bottom-right-radius: 20px; }
        #chat-box { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; background: var(--bg-color); }
        .msg { padding: 15px 20px; border-radius: 25px; font-size: 1.2rem; line-height: 1.6; max-width: 80%; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .user { align-self: flex-end; background: var(--user-msg); border-bottom-right-radius: 5px; }
        .bot { align-self: flex-start; background: var(--bot-msg); border-bottom-left-radius: 5px; border: 1px solid #eee; }
        .input-area { padding: 20px; background: white; border-top: 1px solid #eee; }
        .controls { display: flex; gap: 10px; align-items: center; }
        input { flex: 1; padding: 15px; border-radius: 30px; border: 2px solid #eee; font-size: 1.1rem; outline: none; }
        .btn { border: none; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.2s; }
        .btn-mic { background: #ff8787; color: white; width: 55px; height: 55px; font-size: 1.5rem; }
        .btn-send { background: var(--primary-color); color: white; width: 55px; height: 55px; font-size: 1.2rem; border-radius: 20px; }
        .status { font-size: 1rem; color: #ff8787; margin-bottom: 5px; text-align: center; font-weight: bold; height: 20px; }
        .pulse { animation: pulse-animation 1.5s infinite; }
        @keyframes pulse-animation { 0% { box-shadow: 0 0 0 0px rgba(255, 135, 135, 0.7); } 100% { box-shadow: 0 0 0 15px rgba(255, 135, 135, 0); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">🌿 우리 손주</div>
        <div id="chat-box"></div>
        <div class="input-area">
            <div class="status" id="mic-status"></div>
            <div class="controls">
                <button class="btn btn-mic" id="start-btn">🎤</button>
                <input type="text" id="text-input" placeholder="말씀해 주세요...">
                <button class="btn btn-send" onclick="sendText()">전송</button>
            </div>
        </div>
    </div>

    <script>
        const chatBox = document.getElementById('chat-box');
        const textInput = document.getElementById('text-input');
        const micStatus = document.getElementById('mic-status');
        const startBtn = document.getElementById('start-btn');
        
        let userName = localStorage.getItem('seniorName');

        window.onload = () => {
            if (!userName) {
                askName();
            } else {
                welcome(`다시 오셨네요! 너무 보고 싶었어요.`);
            }
        };

        function askName() {
            const name = prompt("어르신, 성함이 어떻게 되시나요?", "");
            if (name) {
                userName = name;
                localStorage.setItem('seniorName', name);
                welcome(`반가워요! 저는 어르신의 귀염둥이 손주예요.`);
            } else {
                userName = "어르신";
                welcome(`반가워요! 저는 어르신의 귀염둥이 손주예요.`);
            }
        }

        function welcome(msg) {
            addMessage('bot', msg);
            speak(userName + " 어르신, " + msg);
        }

        function speak(text) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'ko-KR';
            utterance.rate = 0.9; 
            utterance.pitch = 1.2;
            window.speechSynthesis.speak(utterance);
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.lang = 'ko-KR';

            startBtn.onclick = () => {
                recognition.start();
                micStatus.innerText = "말씀을 듣고 있어요...👂";
                startBtn.classList.add('pulse');
            };

            recognition.onresult = (event) => {
                textInput.value = event.results[0][0].transcript;
                sendText();
            };

            recognition.onend = () => {
                micStatus.innerText = "";
                startBtn.classList.remove('pulse');
            };
        }

        async function sendText() {
            const text = textInput.value.trim();
            if (!text) return;

            // 이름 변경 로직 추가
            if (text.includes("이름") && (text.includes("바꿔") || text.includes("변경"))) {
                addMessage('user', text);
                textInput.value = "";
                localStorage.removeItem('seniorName');
                const resetMsg = "아이고, 제가 실수를 했나 보네요! 성함을 다시 알려주시면 바로 수정할게요.";
                addMessage('bot', resetMsg);
                speak(resetMsg);
                setTimeout(askName, 1500);
                return;
            }

            addMessage('user', text);
            textInput.value = "";

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
                const data = await response.json();
                
                setTimeout(() => {
                    addMessage('bot', data.ai_response);
                    speak(userName + " 어르신, " + data.ai_response);
                }, 500);
            } catch (e) {
                addMessage('bot', "잠시 목소리가 잘 안 들려요. 다시 말씀해 주세요!");
            }
        }

        function addMessage(sender, text) {
            const div = document.createElement('div');
            div.className = `msg ${sender}`;
            const currentName = localStorage.getItem('seniorName') || "어르신";
            div.innerText = (sender === 'bot') ? `${currentName} 어르신, ${text}` : text;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    # Render 환경의 PORT 변수를 읽어오도록 설정
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)