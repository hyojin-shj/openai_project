from PyQt5.QtCore import QObject, pyqtSignal
from openai import OpenAI
import traceback


class ImageWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, client: OpenAI, prompt: str):
        super().__init__()
        self.client = client
        self.prompt = prompt

    def run(self):
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=self.prompt,
                size="1024x1024",
                n=1,
                response_format="url"
            )

            url = response.data[0].url
            if not url:
                raise Exception("이미지 URL을 가져올 수 없습니다.")

            self.finished.emit(url)

        except Exception as e:
            traceback.print_exc()
            self.error.emit(str(e))