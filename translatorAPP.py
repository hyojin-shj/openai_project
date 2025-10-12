import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSlot, pyqtSignal, QObject

# 교안 20페이지: 'translation_input_app' 모듈에서 Translator 클래스를 가져옵니다.
from translation_input_app import Translator

# 교안 21페이지: 백그라운드 작업의 신호를 정의하는 클래스
class TranslateWorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(str)

# 교안 22페이지: 번역 작업을 처리할 QRunnable 클래스
class TranslateWorker(QRunnable):
    def __init__(self, text):
        super().__init__()
        self.text = text
        self.signals = TranslateWorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            translator = Translator()
            translated_text = translator.translate_to_korean(self.text)
            self.signals.result.emit(translated_text)
        except Exception as e:
            self.signals.error.emit((e,))
        finally:
            # try/except와 관계없이 작업이 끝나면 항상 finished 신호를 보냅니다.
            self.signals.finished.emit()

# 교안 9페이지, 23페이지: 메인 애플리케이션 클래스
class TranslatorApp(QWidget):
    def __init__(self):
        super().__init__()
        # 교안 23페이지의 순서에 따라 UI를 먼저 초기화합니다.
        self.initUI()
        self.thread_pool = QThreadPool() # 스레드 풀 생성

    # 교안 10~15페이지: 사용자 인터페이스 초기화 메서드
    def initUI(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout()

        # 상단 레이아웃
        top_layout = QHBoxLayout()
        lbl_input = QLabel('영어문장을 입력해주세요.')
        lbl_output = QLabel('한글 번역 결과')
        top_layout.addWidget(lbl_input)
        top_layout.addStretch(1)
        top_layout.addWidget(lbl_output)

        # 중앙 레이아웃
        center_layout = QHBoxLayout()
        self.text_input = QTextEdit()
        self.text_output = QTextEdit()
        center_layout.addWidget(self.text_input)
        center_layout.addWidget(self.text_output)

        # 하단 레이아웃
        bottom_layout = QHBoxLayout()
        self.translate_button = QPushButton('번역 요청 버튼')
        self.translate_button.clicked.connect(self.translate_text)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.translate_button)

        # 전체 레이아웃에 추가
        main_layout.addLayout(top_layout)
        main_layout.addLayout(center_layout)
        main_layout.addLayout(bottom_layout)

        # 메인 윈도우 설정
        self.setLayout(main_layout)
        self.setWindowTitle('영어 -> 한글 번역기')
        self.setGeometry(300, 300, 800, 400)
        self.show()

    # 교안 24페이지: 텍스트 번역 메서드 (스레드 사용 버전)
    def translate_text(self):
        input_text = self.text_input.toPlainText()
        worker = TranslateWorker(input_text)
        worker.signals.result.connect(self.display_translation)
        worker.signals.error.connect(self.handle_error)
        self.thread_pool.start(worker)

    # 교안 25페이지: 화면 출력 메서드
    def display_translation(self, translated_text):
        # 교안에 명시된 대로 "(번역됨)" 텍스트를 추가합니다.
        self.text_output.setPlainText(translated_text + " (번역됨)")

    def handle_error(self, error):
        self.text_output.setPlainText(f"Error: {error}")

# 교안 17페이지: 메인 실행 코드
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TranslatorApp()
    sys.exit(app.exec_())
