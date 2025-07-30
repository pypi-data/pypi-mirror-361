from abc import ABC, abstractmethod

class BaseTool(ABC):
    @abstractmethod
    def can_handle(self, file_path: str, mime_type: str | None) -> bool:
        """Check if the tool can handle the given file based on path and MIME type."""
        pass

    @abstractmethod
    def extract_content(self, file_path: str) -> str:
        """Extract content from the file."""
        pass