import os
from .pdf import PDFExtractor
from .docx import DocxExtractor
from .txt import TxtExtractor
from .base import DocumentExtractionError

EXTRACTORS = [
    PDFExtractor(),
    DocxExtractor(),
    TxtExtractor(),
]


def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    for extractor in EXTRACTORS:
        if ext in extractor.supported_types:
            return extractor.extract(file_path)

    raise DocumentExtractionError(f"Unsupported file type: {ext}")
