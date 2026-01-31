import docx
from .base import BaseExtractor, DocumentExtractionError


class DocxExtractor(BaseExtractor):
    supported_types = [".docx"]

    def extract(self, file_path: str) -> str:
        try:
            document = docx.Document(file_path)
            return "\n".join(p.text for p in document.paragraphs)
        except Exception as e:
            raise DocumentExtractionError(str(e))
