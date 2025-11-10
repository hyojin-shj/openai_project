import os
import dotenv
import traceback
import requests
from docx import Document

from filesearch.file import run_file_search  # ✅ 추가
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap

from main_window_ui import Ui_MainWindow
from openai import OpenAI

dotenv.load_dotenv()


# --- 이미지 생성 Worker ---
class ImageWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

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
            self.error.emit(str(e))


# --- 오디오 전사 + 노트 생성 Worker ---
class AudioWorker(QObject):
    finished = pyqtSignal(dict, str)
    error = pyqtSignal(str)

    def __init__(self, client, audio_file_path, output_filename):
        super().__init__()
        self.client = client
        self.audio_file_path = audio_file_path
        self.output_filename = output_filename

    def run(self):
        try:
            # 1. 오디오 전사
            with open(self.audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    response_format="text"
                )
            transcription_text = transcript  # whisper-1 API는 str 반환

            # 2. 요약/노트 생성
            notes = {
                "abstract_summary": self.abstract_summary_extraction(transcription_text),
                "key_points": self.key_points_extraction(transcription_text),
                "action_items": self.action_items_extraction(transcription_text),
                "sentiment": self.sentiment_analysis(transcription_text)
            }

            # 3. docx 저장
            doc = Document()
            for key, value in notes.items():
                heading = ''.join(word.capitalize() for word in key.split('_'))
                doc.add_heading(heading, level=1)
                doc.add_paragraph(value)
                doc.add_paragraph()
            doc.save(self.output_filename)

            self.finished.emit(notes, self.output_filename)

        except Exception as e:
            traceback.print_exc()
            self.error.emit(str(e))

    # --- 기존 MainWindow 메서드 그대로 재사용 가능 ---
    def abstract_summary_extraction(self, text):
        response = self.client.chat.completions.create(
            model="gpt-4",
            temperature=0,
            messages=[
                {"role": "system", "content": "You are a helpful assistant who summarizes text."},
                {"role": "user", "content": f"Summarize the following text: {text}"}
            ]
        )
        return response.choices[0].message.content

    def key_points_extraction(self, text):
        response = self.client.chat.completions.create(
            model="gpt-4",
            temperature=0,
            messages=[
                {"role": "system", "content": "You are a helpful assistant who extracts key points from text."},
                {"role": "user", "content": f"Extract the key points from the following text: {text}"}
            ]
        )
        return response.choices[0].message.content

    def action_items_extraction(self, text):
        response = self.client.chat.completions.create(
            model="gpt-4",
            temperature=0,
            messages=[
                {"role": "system", "content": "You are a helpful assistant who extracts action items from text."},
                {"role": "user", "content": f"Extract the action items from the following text: {text}"}
            ]
        )
        return response.choices[0].message.content

    def sentiment_analysis(self, text):
        response = self.client.chat.completions.create(
            model="gpt-4",
            temperature=0,
            messages=[
                {"role": "system", "content": "You are a helpful assistant who analyzes sentiment of text."},
                {"role": "user", "content": f"Analyze the sentiment of the following text: {text}"}
            ]
        )
        return response.choices[0].message.content


# --- MainWindow ---
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
        self.ui.audio_note_btn.clicked.connect(self.generate_audio_note)
        self.ui.file_btn.clicked.connect(self.handle_file_search)

        self.show()

    # --- 시 생성 ---
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

    # --- 번역 ---
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

    # --- 이미지 생성 ---
    def generate_image(self):
        prompt = self.ui.image_prompt_input.text()
        if not prompt:
            self.ui.image_display_label.setText("이미지 프롬프트를 입력해주세요.")
            return

        self.ui.image_generate_btn.setEnabled(False)
        self.ui.image_display_label.setText("이미지 생성 중입니다...")

        self.image_thread = QThread()
        self.image_worker = ImageWorker(self.client, prompt)
        self.image_worker.moveToThread(self.image_thread)

        self.image_thread.started.connect(self.image_worker.run)
        self.image_worker.finished.connect(self.handle_image_result)
        self.image_worker.error.connect(self.handle_image_error)
        self.image_worker.finished.connect(self.image_thread.quit)
        self.image_worker.finished.connect(self.image_worker.deleteLater)
        self.image_thread.finished.connect(self.image_thread.deleteLater)

        self.image_thread.start()

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

    def handle_image_error(self, error_msg):
        self.ui.image_display_label.setText(f"오류가 발생했습니다: {error_msg}")
        self.ui.image_generate_btn.setEnabled(True)

    # --- 오디오 노트 생성 ---
    def generate_audio_note(self):
        audio_file_path = self.ui.audio_source_input.text()
        if not audio_file_path:
            self.ui.audio_source_input.setText("오디오 파일을 선택해주세요.")
            return

        output_filename = QFileDialog.getSaveFileName(self, "저장할 docx 파일 선택", "", "Word Document (*.docx)")[0]
        if not output_filename:
            self.ui.audio_source_input.setText("파일 선택 취소됨")
            self.ui.audio_note_btn.setEnabled(True)
            return

        self.ui.audio_note_btn.setEnabled(False)
        self.ui.audio_source_input.setText("노트 생성 중...")

        self.audio_thread = QThread()
        self.audio_worker = AudioWorker(self.client, audio_file_path, output_filename)
        self.audio_worker.moveToThread(self.audio_thread)

        self.audio_thread.started.connect(self.audio_worker.run)
        self.audio_worker.finished.connect(self.handle_audio_result)
        self.audio_worker.error.connect(self.handle_audio_error)
        self.audio_worker.finished.connect(self.audio_thread.quit)
        self.audio_worker.finished.connect(self.audio_worker.deleteLater)
        self.audio_thread.finished.connect(self.audio_thread.deleteLater)

        self.audio_thread.start()

    def handle_audio_result(self, notes, filename):
        self.ui.audio_source_input.setText(f"노트 생성 완료: {filename}")
        self.ui.audio_note_btn.setEnabled(True)

    def handle_audio_error(self, error_msg):
        self.ui.audio_source_input.setText(f"오류 발생: {error_msg}")
        self.ui.audio_note_btn.setEnabled(True)

# --- 파일 분석 (page5) ---
    def handle_file_search(self):
        file_path = self.ui.file_input.text()
        question = self.ui.user_input.text()

        if not file_path or not question:
            self.ui.translate_result_view_2.setText("파일 경로와 질문을 모두 입력해주세요.")
            return

        self.ui.translate_result_view_2.setText("파일 분석 중입니다... 잠시만 기다려주세요.")
        QApplication.processEvents() 

        try:
            result_text = run_file_search(file_path, question, self.client)
            self.ui.translate_result_view_2.setText(result_text)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.ui.translate_result_view_2.setText(f"오류 발생: {e}")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())