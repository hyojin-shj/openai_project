from openai import OpenAI
from dotenv import load_dotenv
import os, traceback

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

client = OpenAI(api_key=os.environ.get("API_KEY"))

FINE_TUNED_MODEL = "ft:gpt-3.5-turbo-0125:personal::CaNk9VIU"


def ask_rudebot(question: str):
    try:
        if not question.strip():
            return "❌ 질문을 입력해주세요!"

        response = client.chat.completions.create(
            model=FINE_TUNED_MODEL,
            messages=[
                {"role": "system", "content": "You are RudeBot — a sarcastic but clever chatbot."},
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content
        print(answer)
        return answer

    except Exception as e:
        print(f"⚠️ 오류 발생: {e}")
        return f"⚠️ 오류 발생: {e}"


if __name__ == "__main__":
    user_question = input("루드봇에게 질문하세요: ")
    answer = ask_rudebot(user_question)
    print(f"\n💬 루드봇의 대답: {answer}")