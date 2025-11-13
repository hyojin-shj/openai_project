from PyQt5.QtCore import QObject, pyqtSignal
import traceback
from docx import Document


class FileWorker(QObject):
    finished = pyqtSignal(dict, str)
    error = pyqtSignal(str)

    def __init__(self, client, file_path, user_question):
        super().__init__()
        self.client = client
        self.file_path = file_path
        self.user_question = user_question

    def run(self):
        try:
            # 1) 파일 읽기 및 텍스트 추출
            file_text = ""

            # docx 처리
            if self.file_path.lower().endswith(".docx"):
                doc = Document(self.file_path)
                file_text = "\n".join([p.text for p in doc.paragraphs])

            # doc 처리 (mammoth 사용)
            elif self.file_path.lower().endswith(".doc"):
                try:
                    import mammoth
                    with open(self.file_path, "rb") as doc_file:
                        result = mammoth.extract_raw_text(doc_file)
                        file_text = result.value
                except:
                    file_text = ""

            # txt 처리
            elif self.file_path.lower().endswith(".txt"):
                with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
                    file_text = f.read()

            # pdf 처리
            elif self.file_path.lower().endswith(".pdf"):
                try:
                    from PyPDF2 import PdfReader
                    reader = PdfReader(self.file_path)
                    pages = [page.extract_text() or "" for page in reader.pages]
                    file_text = "\n".join(pages)
                except:
                    file_text = ""
            else:
                file_text = ""

            if not file_text.strip():
                answer = "파일에서 텍스트를 추출할 수 없습니다."
                notes = {"file_answer": answer}
                self.finished.emit(notes, answer)
                return

            # 2) 텍스트 chunk 나누기
            CHUNK_SIZE = 800
            chunks = []
            for i in range(0, len(file_text), CHUNK_SIZE):
                chunks.append(file_text[i:i+CHUNK_SIZE])

            # 3) 각 chunk 에 대해 embedding 생성
            embeddings = []
            for chunk in chunks:
                emb = self.client.embeddings.create(
                    model="text-embedding-3-small",
                    input=chunk
                )
                embeddings.append(emb.data[0].embedding)

            # 4) 질문의 embedding 생성
            query_emb = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=self.user_question
            ).data[0].embedding

            # 5) 유사도 계산 (cosine similarity)
            import numpy as np

            def cosine(a, b):
                a = np.array(a)
                b = np.array(b)
                return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))

            scored = []
            for idx, emb in enumerate(embeddings):
                scored.append((cosine(query_emb, emb), chunks[idx]))

            # 6) 가장 유사한 상위 3개 chunk 선택
            top_chunks = sorted(scored, key=lambda x: x[0], reverse=True)[:3]
            context = "\n\n".join([c[1] for c in top_chunks])

            # 7) 모델에게 context + user question 전달
            prompt = (
                "다음은 파일에서 추출된 관련 있는 내용입니다.\n"
                "이 내용을 기반으로 사용자 질문에 정확하게 답변하세요.\n\n"
                "===== 관련 파일 내용 =====\n"
                f"{context}\n"
                "===== 끝 =====\n\n"
                f"사용자 질문: {self.user_question}"
            )

            response = self.client.responses.create(
                model="gpt-4o-mini",
                input=prompt
            )

            answer = response.output_text or "응답을 해석할 수 없습니다."
            notes = {"file_answer": answer}
            self.finished.emit(notes, answer)

        except Exception as e:
            traceback.print_exc()
            self.error.emit(str(e))