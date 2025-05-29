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

Data models for representing Java code structure.
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class JavaClass:
    """Represents a Java class with its metadata."""
    class_name: str
    java_doc: Optional[str]
    code: str

    def __post_init__(self):
        """Validate and clean data after initialization."""
        if not self.class_name:
            raise ValueError("Class name cannot be empty")

        # Clean up javadoc - remove if it's just whitespace
        if self.java_doc and not self.java_doc.strip():
            self.java_doc = None


@dataclass
class MethodReference:
    """Represents a reference to a method in another class."""
    class_name: str
    method_name: str

    def __post_init__(self):
        """Validate data after initialization."""
        if not self.class_name or not self.method_name:
            raise ValueError("Class name and method name cannot be empty")


@dataclass
class MethodSource:
    """Represents the source method information."""
    class_name: str
    method_name: str

    def __post_init__(self):
        """Validate data after initialization."""
        if not self.class_name or not self.method_name:
            raise ValueError("Class name and method name cannot be empty")


@dataclass
class JavaMethod:
    """Represents a Java method with its metadata and dependencies."""
    src: MethodSource
    java_doc: Optional[str]
    code: str
    dst_methods: List[MethodReference]

    def __post_init__(self):
        """Validate and clean data after initialization."""
        if not self.code.strip():
            raise ValueError("Method code cannot be empty")

        # Clean up javadoc - remove if it's just whitespace
        if self.java_doc and not self.java_doc.strip():
            self.java_doc = None

        # Ensure dst_methods is a list
        if self.dst_methods is None:
            self.dst_methods = []


@dataclass
class JavaCodeData:
    """Container for all Java code data."""
    classes: List[JavaClass]
    methods: List[JavaMethod]

    def __post_init__(self):
        """Validate data after initialization."""
        if self.classes is None:
            self.classes = []
        if self.methods is None:
            self.methods = []

    def get_class_by_name(self, class_name: str) -> Optional[JavaClass]:
        """Find a class by its name."""
        for java_class in self.classes:
            if java_class.class_name == class_name:
                return java_class
        return None

    def get_methods_by_class(self, class_name: str) -> List[JavaMethod]:
        """Get all methods for a specific class."""
        return [method for method in self.methods
                if method.src.class_name == class_name]

    def get_method_dependencies(self, class_name: str, method_name: str) -> List[MethodReference]:
        """Get all method dependencies for a specific method."""
        for method in self.methods:
            if (method.src.class_name == class_name and
                    method.src.method_name == method_name):
                return method.dst_methods
        return []