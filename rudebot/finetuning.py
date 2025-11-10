from openai import OpenAI
from dotenv import load_dotenv
import os, traceback

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

client = OpenAI(api_key=os.environ.get("API_KEY"))
training_file_path = os.path.join(os.path.dirname(__file__), "data10.jsonl")

if not os.path.exists(training_file_path):
    raise FileNotFoundError(f"학습 데이터 파일이 없습니다: {training_file_path}")

try:
    print("학습 데이터 업로드 중...")
    train_file = client.files.create(
        file=open(training_file_path, "rb"),
        purpose="fine-tune"
    )
    print(f"파일 업로드 완료: {train_file.id}")

except Exception as e:
    print(" 파일 업로드 중 오류 발생:")
    traceback.print_exc()
    exit()

try:
    print(" 새로운 Fine-tuning 작업 시작...")
    fine_tune = client.fine_tuning.jobs.create(
        model="gpt-3.5-turbo-0125", 
        training_file=train_file.id
    )

    print(f"🚀 튜닝 작업 생성 완료! Job ID: {fine_tune.id}")
    print("👉 아래 명령으로 상태를 추적하세요:")
    print(f"   openai api fine_tuning.jobs.get -i {fine_tune.id}")

except Exception as e:
    print("튜닝 작업 생성 중 오류 발생:")
    traceback.print_exc()