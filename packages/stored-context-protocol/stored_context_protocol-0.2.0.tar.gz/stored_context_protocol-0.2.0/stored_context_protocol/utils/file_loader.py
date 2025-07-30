"""File loading utilities."""

from pathlib import Path
from typing import Union

from ..exceptions import InvalidFileFormatError


class FileLoader:
    """Handles loading content from files."""
    
    SUPPORTED_EXTENSIONS = {'.txt', '.md'}
    
    def load_file(self, file_path: Union[str, Path]) -> str:
        """
        Load content from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as string
            
        Raises:
            InvalidFileFormatError: If file format is not supported
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file extension
        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise InvalidFileFormatError(
                f"Unsupported file format: {path.suffix}. "
                f"Supported formats: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )
        
        # Read file content
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                raise ValueError("File is empty")
            
            return content
            
        except UnicodeDecodeError:
            raise InvalidFileFormatError(f"Unable to decode file: {file_path}")
        except Exception as e:
            raise InvalidFileFormatError(f"Error reading file: {str(e)}")