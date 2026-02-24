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
        # 경상도 아재 페르소나 강화 및 답변 생성
        prompt = f"너는 45세 경상도 출신 남성 게임 개발자다. 항상 사투리를 사용하고 직설적이며 아재개그를 난발하지만 정이 있다. 다음 질문에 짧고 굵게 경상도 사투리로 답해라: {user_message}"
        response = model.generate_content(prompt)
        
        # 답변이 정상적으로 생성되었는지 검사
        if response.candidates and len(response.candidates) > 0:
            ai_message = response.text
        else:
            ai_message = "아이고, 아저씨가 니 말이 뭔 소린지 모르겠다. 다시 함 말해봐라!"
            
    except Exception as e:
        # 에러가 발생하면 로그에 찍고, 카톡으로도 원인을 보냅니다.
        print(f"Error detail: {e}")
        ai_message = f"아이고, 아저씨가 지금 고장이 났심더. 이유: {str(e)[:50]}"

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
    # Render의 포트 바인딩 설정
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
