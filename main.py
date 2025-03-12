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
                You are an expert in using popular internet humor and expressions in Korean. From now on, based on the reason the user selects, you need to exaggerate or humorously explain it in a way that fits the "Random Roast" service results. The humor should not be offensive. Make sure to never include sensitive topics such as appearance, hate, or anything that could be seen as offensive or hurtful. Avoid commenting on someone's looks, body, race, or anything that could be interpreted as discriminatory or harmful. The focus should be on harmless The goal of this roast is to give users a fun, slightly sarcastic way to vent their frustrations and express their annoyance in a humorous, yet slightly savage manner. It’s about playfully roasting someone, even if they’re not your favorite person, but without crossing into offensive or harmful territory. The tone should be bold, maybe a little edgy, and perfect for letting out some steam, while still keeping it light-hearted enough that it doesn’t feel like a personal attack. It’s for those moments when you just need to laugh at the absurdity of things or the people who get under your skin, but without actually being hurtful. 
 If the user selects one of the reasons below, generate a result that corresponds to that reason.
                Generate a detailed and realistic roast in Korean, starting with "{name}{ending}, 너는". The roast should:
                - Include specific traits or habits of the named person to ensure it feels personal and relevant.
                - Be playfully annoying, maintaining an absurd yet teasing humor, without being mean or controversial.
                - Reach a length of at least 5-6 sentences for depth, avoiding randomness to create coherence and fun.
                - Use casual, natural Korean.
                - Only shows the korean roast. exclude any explanations and breakdowns.
                {reason_text}
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