from pypdf import PdfReader
from .base import BaseExtractor, DocumentExtractionError


class PDFExtractor(BaseExtractor):
    supported_types = [".pdf"]

    def extract(self, file_path: str) -> str:
        try:
            reader = PdfReader(file_path)
            text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
            return "\n".join(text)
        except Exception as e:
            raise DocumentExtractionError(str(e))
