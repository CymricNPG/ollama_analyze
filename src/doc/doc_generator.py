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

Documentation generator for Java code using LLM.
"""
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from java.models import JavaCodeData, JavaMethod, JavaClass, MethodReference
from config import LLMConfig
from .javadoc_generator import JavaDocGenerator


@dataclass
class DocumentationStats:
    """Statistics about documentation generation."""
    total_methods_processed: int = 0
    methods_without_docs: int = 0
    successful_generations: int = 0
    failed_generations: int = 0
    classes_without_docs: int = 0
    classes_doc_generated: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate for method documentation."""
        if self.methods_without_docs == 0:
            return 100.0
        return (self.successful_generations / self.methods_without_docs) * 100.0


class JavaDocumentationGenerator:
    """Generates missing JavaDoc documentation for Java code."""

    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """Initialize the documentation generator."""
        self.javadoc_generator = JavaDocGenerator(llm_config)
        self.logger = logging.getLogger(__name__)
        self.stats = DocumentationStats()

    def generate_missing_documentation(self, java_data: JavaCodeData,
                                       include_classes: bool = True) -> JavaCodeData:
        """
        Generate missing documentation for classes and methods.

        Args:
            java_data: The Java code data
            include_classes: Whether to generate docs for classes too

        Returns:
            Updated JavaCodeData with generated documentation
        """
        self.logger.info("Starting documentation generation process")

        # Check if generator is ready
        if not self.javadoc_generator.is_ready():
            self.logger.error("JavaDoc generator is not ready. Please ensure Ollama is running and the model is available.")
            raise RuntimeError("JavaDoc generator not ready")

        # Reset stats
        self.stats = DocumentationStats()

        # Generate documentation for methods
        self._generate_method_documentation(java_data)

        # Generate documentation for classes if requested
        if include_classes:
            self._generate_class_documentation(java_data)

        # Log final statistics
        self._log_final_stats()

        return java_data

    def _generate_method_documentation(self, java_data: JavaCodeData):
        """Generate documentation for methods without JavaDoc."""
        methods_without_docs = [method for method in java_data.methods
                                if not method.java_doc]

        self.stats.methods_without_docs = len(methods_without_docs)
        self.stats.total_methods_processed = len(java_data.methods)

        self.logger.info(f"Found {len(methods_without_docs)} methods without documentation")

        for i, method in enumerate(methods_without_docs, 1):
            self.logger.info(
                f"Processing method {i}/{len(methods_without_docs)}: "
                f"{method.src.class_name}.{method.src.method_name}"
            )

            # Create context for the method
            context = self._create_method_context(method, java_data)

            # Generate documentation
            documentation = self.javadoc_generator.generate_method_documentation(
                method.code, context
            )

            if documentation:
                method.java_doc = documentation
                self.stats.successful_generations += 1
                self.logger.debug(f"Generated docs for {method.src.class_name}.{method.src.method_name}")
            else:
                self.stats.failed_generations += 1
                self.logger.warning(f"Failed to generate docs for {method.src.class_name}.{method.src.method_name}")

    def _generate_class_documentation(self, java_data: JavaCodeData):
        """Generate documentation for classes without JavaDoc."""
        classes_without_docs = [cls for cls in java_data.classes
                                if not cls.java_doc]

        self.stats.classes_without_docs = len(classes_without_docs)

        self.logger.info(f"Found {len(classes_without_docs)} classes without documentation")

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
                java_class.java_doc = documentation
                self.stats.classes_doc_generated += 1
                self.logger.debug(f"Generated docs for class {java_class.class_name}")
            else:
                self.logger.warning(f"Failed to generate docs for class {java_class.class_name}")

    def _create_method_context(self, method: JavaMethod, java_data: JavaCodeData) -> str:
        """Create context information for a method."""
        context_parts = []

        # Add class information
        parent_class = java_data.get_class_by_name(method.src.class_name)
        if parent_class and parent_class.java_doc:
            context_parts.append(f"Parent class: {method.src.class_name}")
            # Extract first line of class doc for context
            class_doc_first_line = parent_class.java_doc.split('\n')[0].strip('/* ')
            context_parts.append(f"Class purpose: {class_doc_first_line}")

        # Add dependency information
        if method.dst_methods:
            deps = [f"{dep.class_name}.{dep.method_name}" for dep in method.dst_methods]
            context_parts.append(f"Method calls: {', '.join(deps[:3])}")  # Limit to first 3

        # Add method signature analysis
        if "public" in method.code:
            context_parts.append("This is a public method")
        elif "private" in method.code:
            context_parts.append("This is a private method")

        if "static" in method.code:
            context_parts.append("This is a static method")

        return ". ".join(context_parts) if context_parts else ""

    def _create_class_context(self, java_class: JavaClass, java_data: JavaCodeData) -> str:
        """Create context information for a class."""
        context_parts = []

        # Add package information if available
        if "package" in java_class.code:
            package_line = [line for line in java_class.code.split('\n')
                            if line.strip().startswith('package')]
            if package_line:
                context_parts.append(f"Package: {package_line[0].strip()}")

        # Add inheritance information
        if "extends" in java_class.code:
            context_parts.append("This class extends another class")

        if "implements" in java_class.code:
            context_parts.append("This class implements interfaces")

        # Add method count
        class_methods = java_data.get_methods_by_class(java_class.class_name)
        if class_methods:
            context_parts.append(f"Contains {len(class_methods)} methods")

        return ". ".join(context_parts) if context_parts else ""

    def _log_final_stats(self):
        """Log the final generation statistics."""
        self.logger.info("Documentation generation completed")
        self.logger.info(f"Methods processed: {self.stats.total_methods_processed}")
        self.logger.info(f"Methods without docs: {self.stats.methods_without_docs}")
        self.logger.info(f"Successful generations: {self.stats.successful_generations}")
        self.logger.info(f"Failed generations: {self.stats.failed_generations}")
        self.logger.info(f"Success rate: {self.stats.success_rate:.1f}%")

        if self.stats.classes_without_docs > 0:
            self.logger.info(f"Classes without docs: {self.stats.classes_without_docs}")
            self.logger.info(f"Class docs generated: {self.stats.classes_doc_generated}")

    def get_statistics(self) -> DocumentationStats:
        """Get the generation statistics."""
        return self.stats
