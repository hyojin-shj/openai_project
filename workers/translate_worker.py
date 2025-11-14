from PyQt5.QtCore import QObject, QThread, pyqtSignal
import traceback

class TranslateWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(Exception)

    def __init__(self, client, text):
        super().__init__()
        self.client = client
        self.text = text

    def run(self):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Translate English to Korean."},
                    {"role": "user", "content": self.text}
                ]
            )
            result = response.choices[0].message.content
            self.finished.emit(result)

        except Exception as e:
            traceback.print_exc()
            self.error.emit(e)