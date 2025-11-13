import traceback
from PyQt5.QtCore import QObject, pyqtSignal

class RudebotWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, client, question):
        super().__init__()
        self.client = client
        self.question = question

    def run(self):
        try:
            response = self.client.responses.create(
                model="ft:gpt-3.5-turbo-0125:personal::CaKAw4RI",
                input=[
                    {
                        "role": "system",
                        "content": "You are RudeBot — a sarcastic chatbot."
                    },
                    {
                        "role": "user",
                        "content": self.question
                    }
                ]
            )

            text = response.output_text if hasattr(response, "output_text") else "응답이 비어 있습니다."
            self.finished.emit(text)

        except Exception as e:
            traceback.print_exc()
            self.error.emit(str(e))