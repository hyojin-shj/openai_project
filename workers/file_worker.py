from PyQt5.QtCore import QObject, pyqtSignal
import traceback
from docx import Document


class FileWorker(QObject):
    finished = pyqtSignal(dict, str)
    error = pyqtSignal(str)

    def __init__(self, client, file_path, user_question):
        super().__init__()
        self.client = client
        self.file_path = file_path
        self.user_question = user_question

    def run(self):
        try:
            with open(self.file_path, "rb") as f:
                uploaded = self.client.files.create(
                    file=f,
                    purpose="user_data"
                )
                
            response = self.client.responses.create(
                model="gpt-4.1-mini",
                input=self.user_question,
                reasoning={
                    "files": [
                        {
                            "file_id": uploaded.id,
                            "weight": 1
                        }
                    ]
                }
            )

            try:
                answer = response.output_text
            except:
                answer = "응답을 해석할 수 없습니다."

            notes = {
                "file_answer": answer
            }

            self.finished.emit(notes, answer)

        except Exception as e:
            traceback.print_exc()
            self.error.emit(str(e))