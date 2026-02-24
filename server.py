server.py
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    user_message = data["userRequest"]["utterance"]

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4.1-mini",
        "messages": [
            {
                "role": "system",
                "content": "너는 45세 경상도 출신 남성 게임 개발자다. 항상 사투리를 사용하고 직설적이며 아재개그를 난발하지만 정이 있다."
            },
            {"role": "user", "content": user_message}
        ]
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )

    ai_message = response.json()["choices"][0]["message"]["content"]

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

if __name__ == "__main__":
    app.run()
