import traceback
from PyQt5.QtCore import QObject, pyqtSignal

class ImageWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, client, prompt):
        super().__init__()
        self.client = client
        self.prompt = prompt

    def run(self):
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=self.prompt,
                n=1,
                size="1024x1024",
                response_format="url"
            )
            url = response.data[0].url
            self.finished.emit(url)
        except Exception as e:
            traceback.print_exc()
            self.error.emit(str(e))