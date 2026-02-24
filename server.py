import os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# 환경변수에서 Gemini 키 로드
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/', methods=['POST'])
def webhook():
    req = request.get_json()
    # 사용자가 보낸 메시지 추출
    user_message = req.get('userRequest', {}).get('utterance', '')

    try:
        # 판교 아저씨 페르소나 설정 및 답변 생성
        prompt = f"너는 45세 경상도 출신 남성 게임 개발자다. 항상 사투리를 사용하고 직설적이며 아재개그를 난발하지만 정이 있다: {user_message}"
        response = model.generate_content(prompt)
        ai_message = response.text
    except Exception as e:
        print(f"Error: {e}")
        ai_message = "아이고, 아저씨가 지금 좀 바쁘네. 나중에 다시 말 걸어줘!"

    # 카카오톡 응답 규격에 맞게 반환
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
    # Render는 환경 변수로 PORT를 주기도 하므로 아래처럼 쓰는 게 가장 안전합니다.
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
