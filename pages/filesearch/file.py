from PyQt5.QtCore import QThread
from workers.file_worker import FileWorker


class FilesearchPage:
    def __init__(self, ui, client):
        self.ui = ui
        self.client = client

        self.thread = None 
        self.worker = None

        self.ui.file_btn.clicked.connect(self.start_file_search)

    def start_file_search(self):
        file_path = self.ui.file_input.text()
        question = self.ui.user_input.text()

        if not file_path or not question:
            self.ui.translate_result_view_2.setText("파일과 질문을 입력하세요.")
            return

        if self.thread is not None and self.thread.isRunning():
            self.ui.translate_result_view_2.setText("이미 파일 분석 중입니다. 잠시만 기다려주세요.")
            return

        self.ui.translate_result_view_2.setText("파일 분석 중입니다...")

        self.thread = QThread()
        self.worker = FileWorker(self.client, file_path, question)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.handle_finished)
        self.worker.error.connect(self.handle_error)

        self.worker.finished.connect(self._cleanup_thread)
        self.worker.error.connect(self._cleanup_thread)

        self.thread.start()

    def _cleanup_thread(self, *args):
        if self.thread is not None:
            self.thread.quit()
            self.thread.wait()
            self.thread = None

        self.worker = None

    def handle_finished(self, result, answer):
        try:
            self.ui.translate_result_view_2.setText(result.get("file_answer", answer))
        except Exception as e:
            print("UI update error:", e)

    def handle_error(self, e):
        self.ui.translate_result_view_2.setText(f"오류 발생: {e}")