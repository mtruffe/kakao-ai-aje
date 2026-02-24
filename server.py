import os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# 1. API 키 설정
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# 2. 모델 설정 (가장 안정적인 이중 시도 방식)
def get_model():
    try:
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        return genai.GenerativeModel('gemini-pro')

model = get_model()

@app.route('/', methods=['POST'])
def webhook():
    req = request.get_json()
    user_message = req.get('userRequest', {}).get('utterance', '')

    # [핵심] 메시지에 "아저씨"라는 단어가 있는지 확인합니다.
    if "아저씨" in user_message:
        try:
            # 아저씨라는 호칭을 빼고 질문만 추출해서 보낼 수도 있지만, 
            # 페르소나 유지를 위해 전체 메시지를 보냅니다.
            prompt = f"너는 45세 경상도 출신 남성 게임 개발자다. 사투리로 짧게 답해라: {user_message}"
            response = model.generate_content(prompt)
            
            if response and response.text:
                ai_message = response.text
            else:
                ai_message = "아이고, 아저씨가 지금 딴짓하다가 못 들었다. 다시 함 불러바라!"
        except Exception as e:
            # 404 에러 등 문제 발생 시 예비 모델로 재시도
            try:
                temp_model = genai.GenerativeModel('gemini-pro')
                response = temp_model.generate_content(f"경상도 사투리로 답해: {user_message}")
                ai_message = response.text
            except:
                ai_message = f"아저씨가 지금 좀 아프다... 이유: {str(e)[:30]}"
    else:
        # "아저씨"가 포함되지 않은 메시지에는 아무 대답도 하지 않습니다.
        # 카카오톡 챗봇에서 응답을 안 보내려면 빈 결과를 보내거나 특정 처리를 합니다.
        return jsonify({"version": "2.0", "template": {"outputs": []}})

    # 응답 규격에 맞춰 반환
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
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
