import os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# 1. API 키 설정
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# 2. 모델 설정 (404 에러를 잡기 위한 이중 안전장치)
# 라이브러리 버전에 따라 모델명을 찾는 방식이 다르기 때문에 둘 다 시도합니다.
try:
    # 최신 라이브러리 방식
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    try:
        # 구버전 라이브러리 방식
        model = genai.GenerativeModel('models/gemini-1.5-flash')
    except Exception:
        # 정 안되면 가장 안정적인 프로 모델 사용
        model = genai.GenerativeModel('gemini-pro')

@app.route('/', methods=['POST'])
def webhook():
    req = request.get_json()
    # 사용자가 보낸 메시지 추출
    user_message = req.get('userRequest', {}).get('utterance', '')

    try:
        # 경상도 아재 페르소나 설정
        prompt = f"너는 45세 경상도 출신 남성 게임 개발자다. 항상 사투리를 사용하고 직설적이며 아재개그를 난발하지만 정이 있다. 다음 질문에 짧고 굵게 경상도 사투리로 답해라: {user_message}"
        
        # 답변 생성
        response = model.generate_content(prompt)
        
        # 답변 읽기 (안전한 접근)
        if response and response.candidates:
            # response.text가 오류날 경우를 대비해 직접 part 추출
            ai_message = response.candidates[0].content.parts[0].text
        else:
            ai_message = "아이고, 아저씨가 니 말이 뭔 소린지 모르겠다. 다시 함 말해봐라!"
            
    except Exception as e:
        print(f"Error detail: {e}")
        # 에러 메시지가 너무 길면 짤라서 보여줌
        ai_message = f"아저씨 고장났다! 이유: {str(e)[:100]}"

    # 카카오톡 응답 규격
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": ai_message
                    }
                }
            ]
        }
    })

if __name__ == '__main__':
    # Render 포트 바인딩
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
