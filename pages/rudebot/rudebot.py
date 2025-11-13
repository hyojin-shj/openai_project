from PyQt5.QtCore import QThread
from workers.rudebot_worker import RudebotWorker

class RudebotPage:
    def __init__(self, ui, client):
        self.ui = ui
        self.client = client

        self.ui.rudebot_btn_2.clicked.connect(self.ask_rudebot)

    def ask_rudebot(self):
        question = self.ui.rudebot_input_2.text().strip()
        if not question:
            self.ui.translate_result_view_3.setText(" 질문을 입력하세요!")
            return

        self.ui.rudebot_btn_2.setEnabled(False)
        self.ui.translate_result_view_3.setText("🤖 RudeBot 생각 중...")

        self.thread = QThread()
        self.worker = RudebotWorker(self.client, question)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.handle_result)
        self.worker.error.connect(self.handle_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def handle_result(self, text):
        self.ui.translate_result_view_3.setText(text)
        self.ui.rudebot_btn_2.setEnabled(True)

    def handle_error(self, msg):
        self.ui.translate_result_view_3.setText(f"⚠️ 오류 발생: {msg}")
        self.ui.rudebot_btn_2.setEnabled(True)