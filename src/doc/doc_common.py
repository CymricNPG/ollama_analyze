
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

Common functionality for documentation generation.
"""
import json
import logging
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

from config import LLMConfig
from .javadoc_llm_generator import JavaDocLLMGenerator


class BaseDocumentationGenerator(ABC):
    """Base class for documentation generators with common functionality."""
    
    def __init__(self, llm_config: Optional[LLMConfig] = None, output_dir: str = "generated"):
        """
        Initialize the base documentation generator.
        
        Args:
            llm_config: LLM configuration
            output_dir: Directory to save generated documentation files
        """
        self.javadoc_generator = JavaDocLLMGenerator(llm_config)
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(output_dir)
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def is_ready(self) -> bool:
        """Check if the generator is ready to use."""
        return self.javadoc_generator.is_ready()
    
    def _save_to_file(self, data: Dict[str, Any], entity_name: str):
        """
        Save documentation data to a JSON file.
        
        Args:
            data: The data to save
            entity_name: Name of the entity (for logging)
        """
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            filename = f"{file_id}.json"
            filepath = self.output_dir / filename
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Saved documentation to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to save {entity_name} to file: {e}")
    
    def set_output_directory(self, output_dir: str):
        """
        Set a new output directory for generated files.
        
        Args:
            output_dir: Path to the new output directory
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Output directory set to: {self.output_dir}")
    
    def get_output_directory(self) -> str:
        """Get the current output directory path."""
        return str(self.output_dir)
    
    @abstractmethod
    def generate_documentation(self, *args, **kwargs):
        """Abstract method for generating documentation."""
        pass
