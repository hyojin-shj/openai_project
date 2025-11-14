# pages/translate/translate_page.py
from PyQt5.QtCore import QThread
from workers.translate_worker import TranslateWorker


class TranslatePage:
    def __init__(self, ui, client):
        self.ui = ui
        self.client = client

        # 버튼 클릭 연결
        self.ui.translate_btn.clicked.connect(self.translate_text)

    def translate_text(self):
        source_text = self.ui.translate_source_input.toPlainText()
        if not source_text:
            self.ui.translate_result_view.setText("번역할 문장을 입력하세요.")
            return

        self.ui.translate_btn.setEnabled(False)
        self.ui.translate_result_view.setText("번역 중입니다...")

        # 스레드 생성
        self.thread = QThread()
        self.worker = TranslateWorker(self.client, source_text)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.handle_result)
        self.worker.error.connect(self.handle_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def handle_result(self, text):
        self.ui.translate_result_view.setText(text)
        self.ui.translate_btn.setEnabled(True)

    def handle_error(self, e):
        self.ui.translate_result_view.setText(f"오류 발생: {e}")
        self.ui.translate_btn.setEnabled(True)