from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

class Translator:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get("API_KEY")
        )

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
    translator = Translator()
    english_sentence = input("번역할 영어 문장을 입력하세요: ")
    korean_translation = translator.translate_to_korean(english_sentence)
    print("번역 결과:", korean_translation)

if __name__ == "__main__":
    main()