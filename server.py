import os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# 환경변수에서 Gemini 키 로드
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# 404 에러 및 v1beta 문제를 방지하기 위한 가장 안정적인 설정입니다.
# models/ 를 제거하고 모델명만 적거나, 라이브러리가 추천하는 기본형을 사용합니다.
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    # 혹시나 해서 예비용으로 pro 모델도 준비해둡니다.
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
        
        # 404 에러가 해결되었다면 response.text를 읽어옵니다.
        # v1beta 에러 시 response 객체 자체가 비어있을 수 있어 세밀하게 체크합니다.
        if response and hasattr(response, 'text'):
            ai_message = response.text
        else:
            ai_message = "아이고, 아저씨가 니 말이 뭔 소린지 모르겠다. 다시 함 말해봐라!"
            
    except Exception as e:
        # 에러 발생 시 로그를 남기고 사용자에게 알림
        print(f"Error detail: {e}")
        # 에러 메시지를 카톡으로 보내서 원인을 최종 확인합니다.
        ai_message = f"아저씨가 고장났심더. 이유: {str(e)[:50]}"

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
