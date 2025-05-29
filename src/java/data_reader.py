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

Module for reading Java code data from JSON files.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from .models import (
    JavaClass, JavaMethod, JavaCodeData,
    MethodSource, MethodReference
)


class JavaDataReader:
    """Reads Java code data from JSON files."""

    def __init__(self):
        """Initialize the data reader."""
        self.logger = logging.getLogger(__name__)

    def read_classes_file(self, file_path: str) -> List[JavaClass]:
        """
        Read Java classes from a JSON file.
        
        Args:
            file_path: Path to the JSON file containing class data
            
        Returns:
            List of JavaClass objects
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
            ValueError: If the data structure is invalid
        """
        self.logger.info(f"Reading classes from file: {file_path}")

        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Classes file not found: {file_path}")

        try:
            with open(file_path_obj, 'r', encoding='utf-8') as file:
                data = file.read().strip()

                # Handle the case where each line is a separate JSON object
                classes = []
                for line in data.split('\n'):
                    line = line.strip()
                    if line:
                        class_data = json.loads(line)
                        java_class = self._parse_class_data(class_data)
                        classes.append(java_class)

                self.logger.info(f"Successfully read {len(classes)} classes")
                return classes

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in classes file: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading classes file: {e}")
            raise

    def read_methods_file(self, file_path: str) -> List[JavaMethod]:
        """
        Read Java methods from a JSON file.
        
        Args:
            file_path: Path to the JSON file containing method data
            
        Returns:
            List of JavaMethod objects
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
            ValueError: If the data structure is invalid
        """
        self.logger.info(f"Reading methods from file: {file_path}")

        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Methods file not found: {file_path}")

        try:
            with open(file_path_obj, 'r', encoding='utf-8') as file:
                data = file.read().strip()

                # Handle the case where each line is a separate JSON object
                methods = []
                for line in data.split('\n'):
                    line = line.strip()
                    if line:
                        method_data = json.loads(line)
                        java_method = self._parse_method_data(method_data)
                        methods.append(java_method)

                self.logger.info(f"Successfully read {len(methods)} methods")
                return methods

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in methods file: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading methods file: {e}")
            raise

    def read_java_data(self, classes_file: str, methods_file: str) -> JavaCodeData:
        """
        Read both classes and methods files and return combined data.
        
        Args:
            classes_file: Path to the classes JSON file
            methods_file: Path to the methods JSON file
            
        Returns:
            JavaCodeData object containing all the data
        """
        self.logger.info("Reading Java code data from files")

        classes = self.read_classes_file(classes_file)
        methods = self.read_methods_file(methods_file)

        code_data = JavaCodeData(classes=classes, methods=methods)

        self.logger.info(
            f"Successfully loaded Java data: {len(classes)} classes, "
            f"{len(methods)} methods"
        )

        return code_data

    def _parse_class_data(self, data: Dict[str, Any]) -> JavaClass:
        """Parse a single class data dictionary into a JavaClass object."""
        try:
            return JavaClass(
                class_name=data['className'],
                java_doc=data.get('javaDoc'),
                code=data['code']
            )
        except KeyError as e:
            raise ValueError(f"Missing required field in class data: {e}")

    def _parse_method_data(self, data: Dict[str, Any]) -> JavaMethod:
        """Parse a single method data dictionary into a JavaMethod object."""
        try:
            # Parse source method information
            src_data = data['src']
            src = MethodSource(
                class_name=src_data['className'],
                method_name=src_data['methodName']
            )

            # Parse destination methods (dependencies)
            dst_methods = []
            for dst_data in data.get('dstMethods', []):
                dst_method = MethodReference(
                    class_name=dst_data['className'],
                    method_name=dst_data['methodName']
                )
                dst_methods.append(dst_method)

            return JavaMethod(
                src=src,
                java_doc=data.get('javaDoc'),
                code=data['code'],
                dst_methods=dst_methods
            )
        except KeyError as e:
            raise ValueError(f"Missing required field in method data: {e}")