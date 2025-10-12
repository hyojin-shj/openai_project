import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget,
    QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton,
    QComboBox, QLineEdit, QTextEdit
)
from openai import OpenAI
from dotenv import load_dotenv

# .env에서 API 키 로드
load_dotenv()
client = OpenAI(api_key=os.getenv("API_KEY"))

class ImageGenerationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # 행 1: 모델, 크기, 개수
        row1_layout = QHBoxLayout()
        model_label = QLabel('이미지 생성 모델', self)
        self.model_combo = QComboBox(self)
        self.model_combo.addItems(['dall-e-3', 'dall-e-2'])
        row1_layout.addWidget(model_label)
        row1_layout.addWidget(self.model_combo)

        size_label = QLabel('이미지 생성 크기', self)
        self.size_combo = QComboBox(self)
        self.size_combo.addItems(['1024x1024', '1792x1024', '1024x1792'])
        row1_layout.addWidget(size_label)
        row1_layout.addWidget(self.size_combo)

        number_label = QLabel('이미지 생성 개수', self)
        self.number_edit = QLineEdit(self)
        self.number_edit.setText('1')
        row1_layout.addWidget(number_label)
        row1_layout.addWidget(self.number_edit)

        # 행 2: 프롬프트 입력
        row2_layout = QHBoxLayout()
        prompt_label = QLabel('프롬프트 입력', self)
        self.prompt_edit = QLineEdit(self)
        self.prompt_edit.setMinimumHeight(50)
        row2_layout.addWidget(prompt_label)
        row2_layout.addWidget(self.prompt_edit)

        # 행 3: 버튼
        row3_layout = QHBoxLayout()
        self.generate_button = QPushButton('이미지 생성', self)
        row3_layout.addWidget(self.generate_button)
        self.generate_button.clicked.connect(self.generate_image)

        # 행 4: 결과 출력
        row4_layout = QVBoxLayout()
        url_label = QLabel('이미지 생성 결과(URL)', self)
        self.url_output = QTextEdit(self)
        self.url_output.setReadOnly(True)
        row4_layout.addWidget(url_label)
        row4_layout.addWidget(self.url_output)

        # 전체 레이아웃 추가
        main_layout.addLayout(row1_layout)
        main_layout.addLayout(row2_layout)
        main_layout.addLayout(row3_layout)
        main_layout.addLayout(row4_layout)

        self.setLayout(main_layout)
        self.setWindowTitle('이미지 생성 프로그램')
        self.resize(600, 400)
        self.show()

    def generate_image(self):
        model = self.model_combo.currentText()
        size = self.size_combo.currentText()
        num = int(self.number_edit.text())
        prompt = self.prompt_edit.text()

        self.url_output.setPlainText("이미지 생성 중입니다... 잠시만 기다려주세요!")

        try:
            response = client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                n=num
            )

            urls = [data.url for data in response.data]
            result_text = "\n\n".join(urls)
            self.url_output.setPlainText(result_text)

        except Exception as e:
            self.url_output.setPlainText(f"⚠️ 오류 발생: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageGenerationApp()
    sys.exit(app.exec_())