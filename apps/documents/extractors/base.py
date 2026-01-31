class DocumentExtractionError(Exception):
    pass


class BaseExtractor:
    supported_types = []

    def extract(self, file_path: str) -> str:
        raise NotImplementedError
