import os
import dotenv
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QPixmap
from ui.main_window import Ui_MainWindow
from openai import OpenAI
dotenv.load_dotenv()

# 각 기능 페이지들 임포트
from pages.filesearch.file import FilesearchPage
from pages.poem.first_ChatGPT_API import generate_poem_text
from pages.translate.translation import TranslatePage
from pages.image.image_sys import ImagePage
from pages.rudebot.rudebot import RudebotPage
from pages.tts.audio import AudioPage

## 워커 임포트해서 가져오기
from workers.image_worker import ImageWorker
from workers.audio_worker import AudioWorker
from workers.rudebot_worker import RudebotWorker
from workers.file_worker import FileWorker
from workers.translate_worker import TranslateWorker

# --- Main Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.client = OpenAI(api_key=os.getenv("API_KEY"))

        self.translate_page = TranslatePage(self.ui, self.client)
        self.image_page = ImagePage(self.ui, self.client)
        self.filesearch_page = FilesearchPage(self.ui, self.client)
        self.rude_page = RudebotPage(self.ui, self.client)
        self.audio_page = AudioPage(self.ui, self.client)


        # 메뉴 전환
        self.ui.menu_list.currentRowChanged.connect(self.ui.stackedWidget.setCurrentIndex)
        self.ui.poem_generate_btn.clicked.connect(self.generate_poem)
        self.show()

    # --- 시 생성 ---
    def generate_poem(self):
        topic = self.ui.poem_topic_input.text()
        if not topic:
            self.ui.poem_result_view.setText("시의 주제를 입력해주세요.")
            return

        self.ui.poem_generate_btn.setEnabled(False)
        self.ui.poem_result_view.setText("시를 생성 중입니다...")

        try:
            result_text = generate_poem_text(self.client, topic)
            self.ui.poem_result_view.setText(result_text)
        except Exception as e:
            self.ui.poem_result_view.setText(f"오류 발생: {e}")
        finally:
            self.ui.poem_generate_btn.setEnabled(True)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())