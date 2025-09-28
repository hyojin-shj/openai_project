from openai import OpenAI
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# [수정 1] 클래스 이름 오타 수정 (Trnaslator -> Translator)
class Translator:
    # [수정 2] __init__ 메서드 이름 수정 (양쪽에 밑줄 두 개)
    def __init__(self):
        self.client = OpenAI(
            # [수정 3] 환경 변수 이름을 "OPENAI_API_KEY"로 변경 (더 일반적인 방식)
            api_key=os.environ.get("API_KEY")
        )

    # [수정 4] translate_to_korean 메서드를 클래스 안으로 들여쓰기
    def translate_to_korean(self, english_sentence):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You will be provided with a sentence in English, and your task is to translate it into Korean"},
                {"role": "user", "content": english_sentence}
            ],
            temperature=0.7,
            max_tokens=64,
            top_p=1
        )
        return response.choices[0].message.content

def main():
    # [수정 5] 클래스와 인스턴스 변수 이름 구분 (translator 인스턴스 생성)
    translator = Translator()
    # [수정 6] 사용자가 직접 문장을 입력하도록 input() 함수 사용
    english_sentence = input("번역할 영어 문장을 입력하세요: ")
    korean_translation = translator.translate_to_korean(english_sentence)
    print("번역 결과:", korean_translation)

# [수정 7] 파이썬 스크립트를 실행하기 위한 시작점 추가
if __name__ == "__main__":
    main()