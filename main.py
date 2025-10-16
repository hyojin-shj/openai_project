import sys
import os
import dotenv
import traceback
import requests
from io import BytesIO

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap

from main_window_ui import Ui_MainWindow
from openai import OpenAI

dotenv.load_dotenv()


# --- 이미지 생성을 담당할 Worker (스레드 필요) ---
class ImageWorker(QObject):
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
        self.client = OpenAI(api_key=os.getenv("API_KEY"))

        # 메뉴 전환
        self.ui.menu_list.currentRowChanged.connect(self.ui.stackedWidget.setCurrentIndex)

        # 버튼 이벤트
        self.ui.poem_generate_btn.clicked.connect(self.generate_poem)
        self.ui.translate_btn.clicked.connect(self.translate_text)
        self.ui.image_generate_btn.clicked.connect(self.generate_image)

        self.show()

    # --- 시 생성 (스레드 X) ---
    def generate_poem(self):
        topic = self.ui.poem_topic_input.text()
        if not topic:
            self.ui.poem_result_view.setText("시의 주제를 입력해주세요.")
            return

        self.ui.poem_generate_btn.setEnabled(False)
        self.ui.poem_result_view.setText(f"'{topic}'에 대한 시를 생성 중입니다...")

        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant who writes poems in Korean."},
                    {"role": "user", "content": f"{topic}라는 주제로 시를 써줘."}
                ]
            )
            result_text = completion.choices[0].message.content
            self.ui.poem_result_view.setText(result_text)
        except Exception as e:
            self.ui.poem_result_view.setText(f"오류가 발생했습니다: {e}")
        finally:
            self.ui.poem_generate_btn.setEnabled(True)

    # --- 번역 (스레드 X) ---
    def translate_text(self):
        source_text = self.ui.translate_source_input.toPlainText()
        if not source_text:
            self.ui.translate_result_view.setText("번역할 문장을 입력해주세요.")
            return

        self.ui.translate_btn.setEnabled(False)
        self.ui.translate_result_view.setText("번역 중입니다...")

        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant who translates English to Korean."},
                    {"role": "user", "content": f"Translate the following English text to Korean: {source_text}"}
                ]
            )
            result_text = completion.choices[0].message.content
            self.ui.translate_result_view.setText(result_text)
        except Exception as e:
            self.ui.translate_result_view.setText(f"오류가 발생했습니다: {e}")
        finally:
            self.ui.translate_btn.setEnabled(True)

    # --- 이미지 생성 (스레드 O) ---
    def generate_image(self):
        prompt = self.ui.image_prompt_input.text()
        if not prompt:
            self.ui.image_display_label.setText("이미지 프롬프트를 입력해주세요.")
            return

        self.ui.image_generate_btn.setEnabled(False)
        self.ui.image_display_label.setText("이미지 생성 중입니다...")

        self.thread = QThread()
        self.worker = ImageWorker(self.client, prompt)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.handle_image_result)
        self.worker.error.connect(self.handle_image_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def handle_image_result(self, image_url):
        try:
            img_data = requests.get(image_url).content
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            self.ui.image_display_label.setPixmap(pixmap)
        except Exception as e:
            self.ui.image_display_label.setText(f"이미지를 불러오는데 실패했습니다: {e}")
        finally:
            self.ui.image_generate_btn.setEnabled(True)

    def handle_image_error(self, e):
        self.ui.image_display_label.setText(f"오류가 발생했습니다: {e}")
        self.ui.image_generate_btn.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())