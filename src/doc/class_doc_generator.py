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

Class documentation generator for Java code using LLM.
"""

from typing import List, Optional

from java.models import JavaCodeData, JavaClass, JavaUpdateClass
from config import LLMConfig
from .doc_common import BaseDocumentationGenerator


class ClassDocumentationGenerator(BaseDocumentationGenerator):
    """Generates missing JavaDoc documentation for Java classes."""

    def __init__(self, llm_config: Optional[LLMConfig] = None, output_dir: str = "generated/classes"):
        """
        Initialize the class documentation generator.
        
        Args:
            llm_config: LLM configuration
            output_dir: Directory to save generated documentation files
        """
        super().__init__(llm_config, output_dir)

    def generate_documentation(self, java_data: JavaCodeData) -> List[JavaUpdateClass]:
        """
        Generate missing documentation for classes.
        
        Args:
            java_data: The Java code data containing classes
            
        Returns:
            List of classes that had documentation generated
        """
        self.logger.info("Starting class documentation generation")

        if not self.is_ready():
            self.logger.error("Class documentation generator is not ready")
            raise RuntimeError("Class documentation generator not ready")

        classes_without_docs = [cls for cls in java_data.classes if not cls.java_doc]

        self.logger.info(f"Found {len(classes_without_docs)} classes without documentation")

        generated_classes = []

        for i, java_class in enumerate(classes_without_docs, 1):
            self.logger.info(
                f"Processing class {i}/{len(classes_without_docs)}: {java_class.class_name}"
            )

            # Create context for the class
            context = self._create_class_context(java_class, java_data)

            # Generate documentation
            documentation = self.javadoc_generator.generate_class_documentation(
                java_class.code, context
            )

            if documentation:
                new_class = JavaUpdateClass(class_name=java_class.class_name, java_doc=documentation)
                self.logger.debug(f"Generated docs for class {java_class.class_name}")

                # Save to file immediately
                self._save_to_file(new_class.__to_dict__(), java_class.class_name)

                generated_classes.append(new_class)
            else:
                self.logger.warning(f"Failed to generate docs for class {java_class.class_name}")

        # Log final statistics
        self.logger.info(f"Generated files saved to: {self.output_dir}")

        return generated_classes

    def _create_class_context(self, java_class: JavaClass, java_data: JavaCodeData) -> str:
        """
        Create context information for a class.
        
        Args:
            java_class: The JavaClass object
            java_data: The complete Java code data for additional context
            
        Returns:
            Context string for the class
        """
        context_parts = []

        # Add package information if available
        # package_info = extract_package_info(java_class.code)
        # if package_info:
        #     context_parts.append(f"Package: {package_info}")

        # Add method count
        class_methods = java_data.get_methods_by_class(java_class.class_name)
        if class_methods:
            context_parts.append(f"Contains {len(class_methods)} methods")

        return ". ".join(context_parts) if context_parts else ""
