import os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# 1. API 키 설정
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# 2. 모델 설정: 12b 대신 더 가볍고 빠른 4b 모델을 우선 사용합니다.
# 4b 모델이 대답 속도가 훨씬 빨라서 5초 타임아웃을 피하기 좋습니다.
model = genai.GenerativeModel('gemma-3-4b-it')

@app.route('/', methods=['POST'])
def webhook():
    req = request.get_json()
    user_message = req.get('userRequest', {}).get('utterance', '')

    if "아저씨" in user_message:
        try:
            # 아저씨가 너무 길게 말하면 또 타임아웃 걸리니까 '최대한 짧게'를 강조합니다.
            prompt = f"너는 45세 경상도 아재 게임 개발자다. 아주 짧게 한 문장으로 사투리로 답해라: {user_message}"
            
            # 답변 생성 (대기 시간을 줄이기 위해 설정을 추가할 수도 있습니다)
            response = model.generate_content(prompt)
            
            if response and response.text:
                ai_message = response.text
            else:
                ai_message = "마! 지금 서버가 좀 느리네. 다시 함 물어바라!"
                
        except Exception as e:
            # 에러 발생 시 아주 짧은 고정 멘트만 던집니다.
            ai_message = "아이고, 아저씨 지금 바쁘다! 나중에 온나!"
    else:
        return jsonify({"version": "2.0", "template": {"outputs": []}})

    return jsonify({
        "version": "2.0",
        "template": { "outputs": [{ "simpleText": { "text": ai_message } }] }
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
