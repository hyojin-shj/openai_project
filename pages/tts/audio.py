from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QFileDialog
from workers.audio_worker import AudioWorker


class AudioPage:
    def __init__(self, ui, client):
        self.ui = ui
        self.client = client

        self.ui.audio_note_btn.clicked.connect(self.generate_audio_note)

    def generate_audio_note(self):
        path = self.ui.audio_source_input.text()
        if not path:
            self.ui.audio_source_input.setText("오디오 파일 경로를 입력하세요.")
            return

        # QFileDialog 호출 시 부모는 ui로 설정해야 함
        output_file, _ = QFileDialog.getSaveFileName(
            self.ui, "저장할 파일", "", "Word Document (*.docx)"
        )
        if not output_file:
            return

        self.ui.audio_source_input.setText("노트 생성 중...")

        # QThread & Worker 생성
        self.thread = QThread()
        self.worker = AudioWorker(self.client, path, output_file)

        self.worker.moveToThread(self.thread)

        # run → finished → quit 구조
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.handle_audio_result)
        self.worker.error.connect(self.handle_audio_error)

        # ✨ 종료/정리 로직 (이게 없으면 앱이 죽음)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def handle_audio_result(self, notes, filename):
        self.ui.audio_source_input.setText(f"노트 생성 완료: {filename}")

    def handle_audio_error(self, err):
        self.ui.audio_source_input.setText(f"오류 발생: {err}")