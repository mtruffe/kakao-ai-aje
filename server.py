import os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# 환경변수에서 Gemini 키 로드
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# 404 에러 해결을 위해 모델명을 명확히 지정합니다.
# 'gemini-1.5-flash' 대신 'models/gemini-1.5-flash'를 사용합니다.
model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')

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
        
        # 404 에러가 해결되었다면 response.text를 읽어옵니다.
        # 만약 차단되거나 응답이 없으면 안전하게 예외처리합니다.
        if response and response.text:
            ai_message = response.text
        else:
            ai_message = "아이고, 아저씨가 니 말이 뭔 소린지 모르겠다. 다시 함 말해봐라!"
            
    except Exception as e:
        # 에러 발생 시 로그를 남기고 사용자에게 알림
        print(f"Error detail: {e}")
        # 에러 메시지가 너무 길면 잘라서 보여줍니다.
        ai_message = f"아이고, 아저씨가 지금 고장이 났심더. 이유: {str(e)[:100]}"

    # 카카오톡 응답 규격 반환
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
