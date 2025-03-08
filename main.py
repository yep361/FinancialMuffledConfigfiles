
from flask import Flask, render_template, request
import os
import google.generativeai as genai

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    print(f"API Key loaded: {api_key[:5]}...")
else:
    print("경고: GEMINI_API_KEY가 설정되지 않았습니다. Secrets 탭에서 API 키를 추가하세요.")

@app.route('/', methods=['GET', 'POST'])
def index():
    roast = None
    name = request.form.get('name', '') if request.method == 'POST' else ''
    level = request.form.get('level', '순한맛') if request.method == 'POST' else '순한맛'

    if request.method == 'POST':
        # Debug output to identify the issue
        print(f"Form data: {request.form}")
        print(f"Name: {name}, Level: {level}")
        
        if not name:
            roast = "이름을 입력해주세요!"
        elif not api_key:
            roast = "API 키가 설정되지 않았습니다. Replit Secrets에 GEMINI_API_KEY를 추가해주세요."
        else:
            try:
                ending = "야" if is_consonant_ended(name) else "아"
                tone = "mild" if level == "순한맛" else "spicy" if level == "매운맛" else "savage"
                prompt = f"""
                Generate a 5-6 sentence roast in Korean starting with "{name}{ending}, 너는". The roast should:
                - Target a quirky, imaginary habit of the named person (not the user) for a "lowkey dislike" vibe.
                - Be playful, random, slightly annoying, no mean/personal/controversial content.
                - Use absurd, teasing humor like "매번 남을 웃게 만든다고 자랑하던데, 사실 노잼의 연속이라서 웃을 때마다 조금 슬퍼져".
                - Adjust tone: {tone} (mild=gentle, spicy=sharp, savage=burn).
                - End with a soft twist like "그만 괴롭히고 잠시 쉬어라. 더 이상 감당 못 해! 🍖".
                - Use casual, natural Korean.
                """
                model = genai.GenerativeModel('gemini-1.0-pro')
                response = model.generate_content(prompt)
                print(f"Raw response: {response}")
                if response and hasattr(response, 'text'):
                    roast = response.text
                else:
                    roast = "응답이 없어요! 모델을 확인해보세요 🍗"
            except Exception as e:
                print(f"Error: {e}")
                roast = "굽기 실패! 다시 시도해 보세요 🍗"

    return render_template('index.html', roast=roast, name=name)

def is_consonant_ended(name):
    if not name:
        return False
    char_code = ord(name[-1])
    if 0xAC00 <= char_code <= 0xD7A3:
        return (char_code - 0xAC00) % 28 > 0
    return False

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
