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
    roast = request.args.get('roast', None)  # URL 쿼리 파라미터에서 roast 가져오기
    name = request.form.get('name', '') if request.method == 'POST' else request.args.get('name', '')
    level = request.form.get('level', '순한맛') if request.method == 'POST' else '순한맛'
    reason = request.form.get('reason', '랜덤') if request.method == 'POST' else '랜덤'
    other_reason = request.form.get('other_reason', '') if request.method == 'POST' else ''

    if request.method == 'POST':
        print(f"Form data: {request.form}")
        print(f"Name: {name}, Level: {level}, Reason: {reason}")

        if not name:
            roast = "이름을 입력해주세요!"
        elif not api_key:
            roast = "API 키가 설정되지 않았습니다. Replit Secrets에 GEMINI_API_KEY를 추가해주세요."
        else:
            try:
                ending = "야" if is_consonant_ended(name) else "아"
                tone = "mild" if level == "순한맛" else "spicy" if level == "매운맛" else "savage"

                # Determine the reason to use in the prompt
                reason_text = ""
                if reason == "기타" and other_reason:
                    reason_text = f"특정 행동 특성: {other_reason}을(를) 중심으로"
                elif reason != "랜덤":
                    reason_text = f"특정 행동 특성: {reason}을(를) 중심으로"

                prompt = f"""
                당신은 한국어 유머와 표현에 능숙한 expert writer입니다. 다음 지시사항에 따라 꼭 첫 줄이 "{name}, 너는"으로 시작하는 재미있는 로스트 메시지를 생성해주세요.

                1. 반드시 메시지의 첫 문장은 "{name}, 너는"으로 시작해야 합니다.
                2. 사용자가 선택한 이유("{reason}")에 집중하여 그 특성을 현실적이고 구체적이게 작성해주세요.
                3. 사용자가 선택한 이유에 대해 공감하며 상황을 유머러스하게 풀어냅니다. 사용자가 겪고 있는 감정을 이해하고, 이를 유머로 표현해 가벼운 방식으로 짜증을 풀 수 있도록 도와주세요.
                4. savage하지만 기분나쁘거나 상처를 주지 않는 톤으로 작성하세요.
                5. 최소 5-6문장 이상으로 구체적이고 일관성 있게 작성하세요.
                6. 자연스러운 한국어 일상 표현을 사용하세요.
                7. 외모, 인종, 성별, 종교, 정치 등 민감한 주제는 절대 언급하지 마세요. 과장되거나 생소한 표현은 사용하지 마세요.
                8. 응답에는 한국어 로스트 내용만 포함하고, 설명이나 영어 번역은 추가하지 마세요.

                {reason_text}

                이제 "{name}, 너는"으로 시작하는 재미있는 로스트를 생성해주세요.
                """
                model = genai.GenerativeModel('gemini-2.0-flash')  # Updated model
                response = model.generate_content(prompt)
                print(f"Raw response: {response}")
                if response and hasattr(response, 'text'):
                    roast = response.text  # AI의 응답 가져오기
                else:
                    roast = "응답이 없어요! 모델을 확인해보세요 🍗"
            except Exception as e:
                print(f"Error: {e}")
                roast = f"굽기 실패! 오류: {e} 다시 시도해 보세요 🍗"

    # 결과가 있는 경우, 해당 결과를 URL 파라미터로 전달
    share_url = None
    if roast:
        share_url = f"{request.url_root}?name={name}&roast={roast}"
    
    return render_template('index.html', roast=roast, name=name, share_url=share_url)

def is_consonant_ended(name):
    if not name:
        return False
    char_code = ord(name[-1])
    if 0xAC00 <= char_code <= 0xD7A3:
        return (char_code - 0xAC00) % 28 > 0
    return False

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)