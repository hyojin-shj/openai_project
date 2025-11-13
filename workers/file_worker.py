from PyQt5.QtCore import QObject, pyqtSignal
import traceback
from docx import Document


class FileWorker(QObject):
    finished = pyqtSignal(dict, str)
    error = pyqtSignal(Exception)

    def __init__(self, client, file_path, user_question):
        super().__init__()
        self.client = client
        self.file_path = file_path
        self.user_question = user_question

    def run(self):
        try:
            # 파일 업로드
            uploaded = self.client.files.create(
                file=open(self.file_path, "rb"),
                purpose="assistants"
            )

            # 벡터스토어 생성 (파일을 검색 대상으로 유지)
            vector_store = self.client.vector_stores.create(name="user_upload")

            # 업로드 파일을 벡터스토어에 연결
            self.client.vector_stores.file_batches.create(
                vector_store_id=vector_store.id,
                file_ids=[uploaded.id]
            )

            # file_search 도구를 사용하여 질문을 수행 (정적 응답)
            response = self.client.responses.create(
                model="gpt-4.1",
                input=self.user_question,
                tools=[
                    {
                        "type": "file_search",
                        "vector_store_ids": [vector_store.id]
                    }
                ],
                max_output_tokens=800,
            )

            # 응답 텍스트 추출
            if hasattr(response, "output_text") and response.output_text:
                answer = response.output_text
            else:
                try:
                    answer = response.output[0].content[0].text
                except:
                    answer = " 응답을 해석할 수 없습니다."

            notes = {
                "file_answer": answer
            }

            # 결과 전달 (문서 저장 없이 텍스트만 반환)
            self.finished.emit(notes, answer)

        except Exception as e:
            traceback.print_exc()
            self.error.emit(e)