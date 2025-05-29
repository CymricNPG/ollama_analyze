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

Utility functions for Java code analysis.
"""
import re
from typing import List, Set
from models import JavaCodeData, JavaClass, JavaMethod


class JavaCodeAnalyzer:
    """Utility class for analyzing Java code data."""

    @staticmethod
    def extract_class_names_from_code(code: str) -> Set[str]:
        """
        Extract referenced class names from Java code.

        Args:
            code: Java source code

        Returns:
            Set of class names found in the code
        """
        # Simple regex to find class references
        # This is a basic implementation and may need refinement
        class_pattern = r'\b([A-Z][a-zA-Z0-9]*(?:\.[A-Z][a-zA-Z0-9]*)*)\b'
        matches = re.findall(class_pattern, code)

        # Filter out common Java keywords and primitives
        java_keywords = {
            'String', 'Integer', 'Boolean', 'Double', 'Float', 'Long',
            'Object', 'Class', 'System', 'Math', 'Collections', 'Arrays'
        }

        return {match for match in matches if match not in java_keywords}

    @staticmethod
    def find_classes_without_documentation(java_data: JavaCodeData) -> List[JavaClass]:
        """Find all classes that don't have JavaDoc documentation."""
        return [cls for cls in java_data.classes if not cls.java_doc]

    @staticmethod
    def find_methods_without_documentation(java_data: JavaCodeData) -> List[JavaMethod]:
        """Find all methods that don't have JavaDoc documentation."""
        return [method for method in java_data.methods if not method.java_doc]

    @staticmethod
    def get_dependency_graph(java_data: JavaCodeData) -> dict:
        """
        Create a dependency graph of methods.

        Returns:
            Dictionary mapping method identifiers to their dependencies
        """
        graph = {}

        for method in java_data.methods:
            method_id = f"{method.src.class_name}.{method.src.method_name}"
            dependencies = [
                f"{dep.class_name}.{dep.method_name}"
                for dep in method.dst_methods
            ]
            graph[method_id] = dependencies

        return graph

    @staticmethod
    def calculate_complexity_metrics(java_data: JavaCodeData) -> dict:
        """
        Calculate basic complexity metrics for the codebase.

        Returns:
            Dictionary with various metrics
        """
        total_classes = len(java_data.classes)
        total_methods = len(java_data.methods)

        # Count methods per class
        methods_per_class = {}
        for method in java_data.methods:
            class_name = method.src.class_name
            methods_per_class[class_name] = methods_per_class.get(class_name, 0) + 1

        # Calculate averages
        avg_methods_per_class = (
            sum(methods_per_class.values()) / len(methods_per_class)
            if methods_per_class else 0
        )

        # Count total dependencies
        total_dependencies = sum(len(method.dst_methods) for method in java_data.methods)
        avg_dependencies_per_method = (
            total_dependencies / total_methods if total_methods > 0 else 0
        )

        return {
            'total_classes': total_classes,
            'total_methods': total_methods,
            'average_methods_per_class': round(avg_methods_per_class, 2),
            'total_dependencies': total_dependencies,
            'average_dependencies_per_method': round(avg_dependencies_per_method, 2),
            'classes_without_docs': len(JavaCodeAnalyzer.find_classes_without_documentation(java_data)),
            'methods_without_docs': len(JavaCodeAnalyzer.find_methods_without_documentation(java_data))
        }
