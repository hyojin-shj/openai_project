from openai import OpenAI
from dotenv import load_dotenv
import os, traceback

load_dotenv()

def run_file_search(file_path: str, user_question: str, client=None) -> str:
    """
    PyQt의 main.py에서 호출할 수 있도록 변환된 함수형 버전.
    파일 경로와 질문을 받아 파일 검색 결과를 문자열로 반환.
    """
    client = client or OpenAI(api_key=os.getenv("API_KEY"))

    if not os.path.exists(file_path):
        return "❌ 파일을 찾을 수 없으니, 경로를 확인해주세요."

    try:
        # 1️⃣ 파일 업로드
        file = client.files.create(
            file=open(file_path, "rb"),
            purpose="assistants"
        )

        # 2️⃣ 벡터스토어 생성
        vector_store = client.vector_stores.create(name="user_upload")

        # 3️⃣ 업로드된 파일을 벡터스토어에 연결
        client.vector_stores.file_batches.create(
            vector_store_id=vector_store.id,
            file_ids=[file.id]
        )

        # 4️⃣ 실시간 스트리밍으로 파일 기반 질문 응답
        result_text = ""
        with client.responses.stream(
            model="gpt-4.1",
            input=user_question,
            tools=[{
                "type": "file_search",
                "vector_store_ids": [vector_store.id]
            }]
        ) as stream:
            for event in stream:
                if event.type == "response.output_text.delta":
                    result_text += event.delta
                elif event.type == "response.refusal.delta":
                    result_text += "[거부]" + event.delta

            final = stream.get_final_response()
            return result_text.strip() or "⚠️ 응답이 비어 있습니다."

    except Exception as e:
        traceback.print_exc()
        return f"⚠️ 오류 발생: {e}"