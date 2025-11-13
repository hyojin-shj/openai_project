from PyQt5.QtCore import QThread
from workers.image_worker import ImageWorker
import requests
from PyQt5.QtGui import QPixmap

class ImagePage:
    def __init__(self, ui, client):
        self.ui = ui
        self.client = client

        self.thread = None
        self.worker = None 
        self.ui.image_generate_btn.clicked.connect(self.generate_image)

    def generate_image(self):
        prompt = self.ui.image_prompt_input.text()
        if not prompt:
            self.ui.image_display_label.setText("이미지 프롬프트를 입력하세요.")
            return

        if self.thread is not None and self.thread.isRunning():
            self.ui.image_display_label.setText("이미지 생성 중입니다. 잠시만 기다려주세요.")
            return

        self.ui.image_generate_btn.setEnabled(False)
        self.ui.image_display_label.setText("이미지 생성 중...")


        self.thread = QThread(self.ui)
        self.worker = ImageWorker(self.client, prompt)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.handle_result)
        self.worker.error.connect(self.handle_error)

        self.worker.finished.connect(self._cleanup_thread)
        self.worker.error.connect(self._cleanup_thread)

        self.thread.start()

    def _cleanup_thread(self):
        if self.thread is not None:
            self.thread.quit()
            self.thread.wait()
            self.thread = None

        self.worker = None
        self.ui.image_generate_btn.setEnabled(True)

    def handle_result(self, url):
        try:
            img_data = requests.get(url).content
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            self.ui.image_display_label.setPixmap(pixmap)
        except Exception as e:
            self.ui.image_display_label.setText(f"이미지 로딩 오류: {e}")

    def handle_error(self, e):
        self.ui.image_display_label.setText(f"오류 발생: {e}")
