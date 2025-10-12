import sys
import os
import dotenv
import openai
import traceback

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal
from main_window_ui import Ui_MainWindow
from PyQt5.QtGui import QPixmap
import requests
from io import BytesIO

# .env 파일에서 환경 변수를 로드합니다.
dotenv.load_dotenv()


# --- 시 생성을 담당할 Worker 스레드 ---
class PoemWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(Exception)

    def __init__(self, client, topic):
        super().__init__()
        self.client = client
        self.topic = topic

    def run(self):
        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant who writes poems in Korean."},
                    {"role": "user", "content": f"{self.topic}라는 주제로 시를 써줘."}
                ]
            )
            result_text = completion.choices[0].message.content
            self.finished.emit(result_text)
        except Exception as e:
            self.error.emit(e)

# --- 번역을 담당할 Worker 스레드 ---
class TranslateWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(Exception)

    def __init__(self, client, source_text):
        super().__init__()
        self.client = client
        self.source_text = source_text

    def run(self):
        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant who translates English to Korean."},
                    {"role": "user", "content": f"Translate the following English text to Korean: {self.source_text}"}
                ]
            )
            result_text = completion.choices[0].message.content
            self.finished.emit(result_text)
        except Exception as e:
            self.error.emit(e)

# --- 이미지 생성을 담당할 Worker 스레드 ---
class ImageWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(Exception)

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
            image_url = response.data[0].url
            self.finished.emit(image_url)
        except Exception as e:
            traceback.print_exc()
            self.error.emit(e)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        from openai import OpenAI
        self.client = OpenAI(api_key=os.getenv("API_KEY"))

        self.ui.menu_list.currentRowChanged.connect(self.ui.stackedWidget.setCurrentIndex)
        self.ui.poem_generate_btn.clicked.connect(self.generate_poem)
        self.ui.translate_btn.clicked.connect(self.translate_text)
        self.ui.image_generate_btn.clicked.connect(self.generate_image)
        self.show()

    def generate_poem(self):
        topic = self.ui.poem_topic_input.text()
        if not topic:
            self.ui.poem_result_view.setText("시의 주제를 입력해주세요.")
            return

        self.ui.poem_generate_btn.setEnabled(False)
        self.ui.poem_result_view.setText(f"'{topic}'에 대한 시를 생성 중입니다...")
        
        self.poem_worker = PoemWorker(client=self.client, topic=topic)
        self.poem_worker.finished.connect(self.handle_poem_result)
        self.poem_worker.error.connect(self.handle_poem_error)
        self.poem_worker.start()

    def handle_poem_result(self, result_text):
        self.ui.poem_result_view.setText(result_text)
        self.ui.poem_generate_btn.setEnabled(True)

    def handle_poem_error(self, e):
        self.ui.poem_result_view.setText(f"오류가 발생했습니다: {e}")
        self.ui.poem_generate_btn.setEnabled(True)

    def translate_text(self):
        source_text = self.ui.translate_source_input.toPlainText()
        if not source_text:
            self.ui.translate_result_view.setText("번역할 문장을 입력해주세요.")
            return

        self.ui.translate_btn.setEnabled(False)
        self.ui.translate_result_view.setText("번역 중입니다...")

        self.translate_worker = TranslateWorker(client=self.client, source_text=source_text)
        self.translate_worker.finished.connect(self.handle_translate_result)
        self.translate_worker.error.connect(self.handle_translate_error)
        self.translate_worker.start()

    def handle_translate_result(self, result_text):
        self.ui.translate_result_view.setText(result_text)
        self.ui.translate_btn.setEnabled(True)

    def handle_translate_error(self, e):
        self.ui.translate_result_view.setText(f"오류가 발생했습니다: {e}")
        self.ui.translate_btn.setEnabled(True)

    def generate_image(self):
        prompt = self.ui.image_prompt_input.text()
        if not prompt:
            self.ui.image_display_label.setText("이미지 프롬프트를 입력해주세요.")
            return

        self.ui.image_generate_btn.setEnabled(False)
        self.ui.image_display_label.setText("이미지 생성 중입니다...")

        self.image_worker = ImageWorker(client=self.client, prompt=prompt)
        self.image_worker.finished.connect(self.handle_image_result)
        self.image_worker.error.connect(self.handle_image_error)
        self.image_worker.start()

    def handle_image_result(self, image_url):
        img_data = requests.get(image_url).content
        pixmap = QPixmap()
        pixmap.loadFromData(img_data)
        self.ui.image_display_label.setPixmap(pixmap)
        self.ui.image_generate_btn.setEnabled(True)

    def handle_image_error(self, e):
        self.ui.image_display_label.setText(f"오류가 발생했습니다: {e}")
        self.ui.image_generate_btn.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

