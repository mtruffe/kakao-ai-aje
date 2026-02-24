import os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# 1. API 키 설정
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# 2. Gemma 3 모델 설정 (지인분이 추천해주신 모델로 교체)
# gemma-3-12b-it은 성능과 속도 밸런스가 가장 좋습니다.
try:
    model = genai.GenerativeModel('gemma-3-12b-it')
except:
    # 혹시 몰라 다른 Gemma 3 모델도 예비용으로 설정
    try:
        model = genai.GenerativeModel('gemma-3-4b-it')
    except:
        model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/', methods=['POST'])
def webhook():
    req = request.get_json()
    user_message = req.get('userRequest', {}).get('utterance', '')

    # "아저씨"라고 부를 때만 대답
    if "아저씨" in user_message:
        try:
            prompt = f"너는 45세 경상도 출신 남성 게임 개발자다. 사투리로 짧고 굵게 답해라: {user_message}"
            response = model.generate_content(prompt)
            
            if response and response.text:
                ai_message = response.text
            else:
                ai_message = "마! 아저씨가 지금 서버 돌리느라 바쁘다. 좀 이따 온나!"
                
        except Exception as e:
            print(f"Error detail: {e}")
            ai_message = f"아저씨 엔진 터졌다! 이유: {str(e)[:50]}"
    else:
        # 아저씨 안 부르면 조용히
        return jsonify({"version": "2.0", "template": {"outputs": []}})

    return jsonify({
        "version": "2.0",
        "template": { "outputs": [{ "simpleText": { "text": ai_message } }] }
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
