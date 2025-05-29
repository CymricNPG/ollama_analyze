
"""
Copyright (C) 2025 Roland Spatzenegger

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Configuration settings for the Java code analysis application.
"""
import logging
from pathlib import Path
from dataclasses import dataclass


class Config:
    """Application configuration."""

    # File paths
    CLASSES_FILE = "java_classes.json"
    METHODS_FILE = "java_methods.json"
    OUTPUT_DIR = "generated"

    # Logging configuration
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def setup_logging(cls):
        """Set up logging configuration."""
        logging.basicConfig(
            level=cls.LOG_LEVEL,
            format=cls.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('java_code_analyzer.log')
            ]
        )

    @classmethod
    def get_data_files_path(cls, base_path: str = ".") -> tuple[str, str]:
        """
        Get the full paths to data files.

        Args:
            base_path: Base directory path where data files are located

        Returns:
            Tuple of (classes_file_path, methods_file_path)
        """
        base = Path(base_path)
        classes_file = base / cls.CLASSES_FILE
        methods_file = base / cls.METHODS_FILE

        return str(classes_file), str(methods_file)

    @classmethod
    def get_output_dir(cls, base_path: str = ".") -> str:
        base = Path(base_path)
        return str(base / cls.OUTPUT_DIR)


@dataclass
class LLMConfig:
    """Configuration for the LLM client."""
    host: str = "http://localhost:11434"
    model: str = "qwen3:8b"
    timeout: float = 60.0
    max_retries: int = 3
    temperature: float = 0.3
    top_p: float = 0.9
