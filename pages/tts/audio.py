from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QFileDialog
from workers.audio_worker import AudioWorker
import traceback


class AudioPage:
    def __init__(self, ui, client):
        self.ui = ui
        self.client = client
        self.thread = None
        self.worker = None

        self.ui.audio_note_btn.clicked.connect(self.generate_audio_note)

    def generate_audio_note(self):
        try:
            path = self.ui.audio_source_input.text()
            if not path:
                self.ui.audio_status_label.setText("오디오 파일 경로를 입력하세요.")
                return

            output_file, _ = QFileDialog.getSaveFileName(
                None,
                "저장할 파일",
                "",
                "Word Document (*.docx)"
            )
            # Ensure .docx extension
            if output_file and not output_file.lower().endswith(".docx"):
                output_file = output_file + ".docx"

            if not output_file:
                return

            label = getattr(self.ui, "audio_status_label", None)
            if label is not None:
                label.setText("노트 생성 중...")
            self.ui.audio_note_btn.setEnabled(False)

            # Thread & Worker
            self.thread = QThread()
            self.worker = AudioWorker(self.client, path, output_file)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.handle_audio_result)
            self.worker.error.connect(self.handle_audio_error)

            self.worker.finished.connect(self._cleanup_thread)
            self.worker.error.connect(self._cleanup_thread)

            self.thread.start()

        except Exception as e:
            traceback.print_exc()
            label = getattr(self.ui, "audio_status_label", None)
            if label is not None:
                label.setText(f"오류 발생: {e}")
            self.ui.audio_note_btn.setEnabled(True)

    def handle_audio_result(self, notes, filename):
        try:
            label = getattr(self.ui, "audio_status_label", None)
            if label is not None:
                label.setText(f"파일 생성 완료: {filename}")
        except Exception as e:
            traceback.print_exc()

    def handle_audio_error(self, err):
        try:
            label = getattr(self.ui, "audio_status_label", None)
            if label is not None:
                label.setText(f"오류 발생: {err}")
        except Exception as e:
            traceback.print_exc()

    def _cleanup_thread(self, *args):
        try:
            if self.thread:
                if self.thread.isRunning():
                    self.thread.quit()
                    self.thread.wait()
                self.thread = None

            if self.worker:
                try:
                    self.worker.deleteLater()
                except Exception:
                    pass
                self.worker = None

            self.ui.audio_note_btn.setEnabled(True)
        except Exception as e:
            traceback.print_exc()
            self.ui.audio_note_btn.setEnabled(True)