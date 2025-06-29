from pathlib import Path

class FolderScanner:
    def __init__(self, directory: Path):
        self.directory = directory

    def get_pdf_paths(self) -> list[Path]:
        return list(self.directory.glob("*.pdf"))
