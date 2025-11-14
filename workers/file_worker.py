from PyQt5.QtCore import QObject, pyqtSignal
import traceback
import time


class FileWorker(QObject):
    finished = pyqtSignal(dict, str)
    error = pyqtSignal(str)

    def __init__(self, client, file_path, user_question, vector_store_id):
        super().__init__()
        self.client = client
        self.file_path = file_path
        self.user_question = user_question
        self.vector_store_id = vector_store_id

    def run(self):
        try:
            with open(self.file_path, "rb") as f:
                uploaded = self.client.files.create(
                    file=f,
                    purpose="assistants"
                )

            file_id = uploaded.id
            add_result = self.client.vector_stores.files.create(
                vector_store_id=self.vector_store_id,
                file_id=file_id
            )

            while True:
                status_list = self.client.vector_stores.files.list(
                    vector_store_id=self.vector_store_id
                )
                if status_list.data and status_list.data[0].status == "completed":
                    break
                time.sleep(1)

            response = self.client.responses.create(
                model="gpt-4.1",
                input=self.user_question,
                tools=[
                    {
                        "type": "file_search",
                        "vector_store_ids": [self.vector_store_id],
                        "max_num_results": 5
                    }
                ],
                include=["file_search_call.results"]
            )

            try:
                answer = response.output_text
            except:
                answer = "응답을 해석할 수 없습니다."

            notes = {
                "file_id": file_id,
                "vector_store_id": self.vector_store_id,
                "answer": answer
            }

            self.finished.emit(notes, answer)

        except Exception as e:
            traceback.print_exc()
            self.error.emit(str(e))
