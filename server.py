import os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==============================
# 1️⃣ API 키 확인
# ==============================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

genai.configure(api_key=GEMINI_API_KEY)

# ==============================
# 2️⃣ 최신 안정 모델 사용
# ==============================
model = genai.GenerativeModel("gemini-1.5-flash")


# ==============================
# 3️⃣ 카카오 웹훅 엔드포인트
# ==============================
@app.route("/", methods=["POST"])
def webhook():
    try:
        # 카카오 JSON 안전 파싱
        req = request.get_json(force=True)

        if not req:
            return jsonify({"error": "Invalid JSON"}), 400

        user_message = req.get("userRequest", {}).get("utterance", "")

        # "아저씨" 포함될 때만 반응
        if "아저씨" not in user_message:
            return jsonify({
                "version": "2.0",
                "template": {"outputs": []}
            })

        # 프롬프트
        prompt = f"""
        너는 45세 경상도 출신 남성 게임 개발자다.
        사투리로 짧게 한 문장으로만 답해라.
        사용자 말: {user_message}
        """

        response = model.generate_content(prompt)

        # 응답 안전 처리
        ai_message = response.text if response and response.text else \
            "마! 지금 빌드 돌리는 중이다! 좀 있다 오이소!"

        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": ai_message.strip()
                        }
                    }
                ]
            }
        })

    except Exception as e:
        print("🔥 서버 에러 발생:", e)

        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "아재 지금 디버깅 지옥이다! 나중에 온나!"
                        }
                    }
                ]
            }
        })


# ==============================
# 4️⃣ Render 실행용
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
