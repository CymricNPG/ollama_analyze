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

Method documentation generator for Java code using LLM.
"""
from typing import List, Optional

from java.models import JavaCodeData, JavaMethod, JavaUpdateMethod
from config import LLMConfig
from .doc_common import BaseDocumentationGenerator


class MethodDocumentationGenerator(BaseDocumentationGenerator):
    """Generates missing JavaDoc documentation for Java methods."""

    def __init__(self, llm_config: Optional[LLMConfig] = None, output_dir: str = "generated/methods"):
        """
        Initialize the method documentation generator.
        
        Args:
            llm_config: LLM configuration
            output_dir: Directory to save generated documentation files
        """
        super().__init__(llm_config, output_dir)

    def generate_documentation(self, java_data: JavaCodeData) -> List[JavaUpdateMethod]:
        """
        Generate missing documentation for methods.
        
        Args:
            java_data: The Java code data containing methods
            
        Returns:
            List of methods that had documentation generated
        """
        self.logger.info("Starting method documentation generation")

        if not self.is_ready():
            self.logger.error("Method documentation generator is not ready")
            raise RuntimeError("Method documentation generator not ready")

        methods_without_docs = [method for method in java_data.methods if not method.java_doc and self.is_valid_method(method)]

        self.logger.info(f"Found {len(methods_without_docs)} methods without documentation")

        generated_methods = []

        for i, method in enumerate(methods_without_docs, 1):
            self.logger.info(
                f"Processing method {i}/{len(methods_without_docs)}: "
                f"{method.src}"
            )

            # Create context for the method
            context = self._create_method_context(method, java_data)

            # Generate documentation
            documentation = self.javadoc_generator.generate_method_documentation(
                method.code, context
            )

            if documentation:
                new_method = JavaUpdateMethod(src=method.src, java_doc=documentation)
                self.logger.debug(f"Generated docs for {method.src}")

                self._save_to_file(new_method.__to_dict__(), f"{method.src}")
                generated_methods.append(method)
            else:
                self.logger.warning(f"Failed to generate docs for {method.src}")

        self.logger.info(f"Generated files saved to: {self.output_dir}")

        return generated_methods

    def _create_method_context(self, method: JavaMethod, java_data: JavaCodeData) -> str:
        """
        Create context information for a method.
        
        Args:
            method: The JavaMethod object
            java_data: The complete Java code data for additional context
            
        Returns:
            Context string for the method
        """
        context_parts = []

        # Add class information
        parent_class = java_data.get_class_by_name(method.src.class_name)
        if parent_class and parent_class.java_doc:
            context_parts.append(f"Parent class: {method.src.class_name}")
            # Extract first line of class doc for context
            class_doc_first_line = parent_class.java_doc[:256].replace("\n"," ").replace("*","")
            context_parts.append(f"Class purpose: {class_doc_first_line}")

        # Add dependency information
        if method.dst_methods:
            deps = [f"{dep}" for dep in method.dst_methods]
            context_parts.append(f"Method calls: {', '.join(deps[:3])}")  # Limit to first 3

        return ". ".join(context_parts) if context_parts else ""

    def is_valid_method(self, method: JavaMethod) -> bool:
        if self.get_class_name_from_qualified_name(method.src.class_name) == method.src.method_name:
            # constructor
            return False
        invalid_method_names = ["equals", "hashCode", "toString", "clone", "finalize", "wait", "notify", "notifyAll"]
        if method.src.method_name in invalid_method_names:
            return False
        return True

    def get_class_name_from_qualified_name(self, qualified_name: str) -> str:
        """Extract class name from fully qualified name."""
        return qualified_name.split('.')[-1]
