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

"""
import logging
import sys
from pathlib import Path

from config import Config
from .data_reader import JavaDataReader
from .models import JavaCodeData
from .update_data import read_class_updates, read_method_updates, update_class_data, update_method_data
from .utils import is_valid_method, is_valid_class

logger = logging.getLogger(__name__)


def remove_unwanted(java_data: JavaCodeData):
    base = JavaCodeData(classes=[data for data in java_data.classes if is_valid_class(data)],
                        methods=[data for data in java_data.methods if is_valid_method(data)])
    return base


def read_structure(base_path: str = ".") -> JavaCodeData:
    """Main application entry point."""

    logger.info("Starting Java Code Analysis Application")

    try:
        # Initialize the data reader
        reader = JavaDataReader()

        # Get file paths
        classes_file, methods_file = Config.get_data_files_path(base_path)

        # Check if files exist
        if not Path(classes_file).exists():
            logger.error(f"Classes file not found: {classes_file}")
            sys.exit(1)

        if not Path(methods_file).exists():
            logger.error(f"Methods file not found: {methods_file}")
            sys.exit(1)

        # Read the Java code data
        logger.info("Reading Java code data...")
        java_data = reader.read_java_data(classes_file, methods_file)

        logger.info("Read completed successfully")

        class_updates = read_class_updates(Config.get_classes_output_dir(base_path))
        method_updates = read_method_updates(Config.get_methods_output_dir(base_path))
        update_class_data(java_data, class_updates)
        update_method_data(java_data, method_updates)

        java_data = remove_unwanted(java_data)

        logger.info(
            f"Java code data read successfully. Total classes: {len(java_data.classes)}, total methods: {len(java_data.methods)}"
        )

        return java_data
    except Exception as e:
        logger.error(f"Read failed: {e}")
        sys.exit(1)


def print_data_summary(java_data: JavaCodeData):
    """Print a summary of the loaded data."""
    print("\n" + "=" * 50)
    print("JAVA CODE DATA SUMMARY")
    print("=" * 50)
    print(f"Total Classes: {len(java_data.classes)}")
    print(f"Total Methods: {len(java_data.methods)}")

    print("\nClasses:")
    for java_class in java_data.classes:
        doc_status = "✓" if java_class.java_doc else "✗"
        print(f"  {doc_status} {java_class.class_name}")

    print("\nMethods by Class:")
    class_method_count = {}
    for method in java_data.methods:
        class_name = method.src.class_name
        class_method_count[class_name] = class_method_count.get(class_name, 0) + 1

    for class_name, count in class_method_count.items():
        print(f"  {class_name}: {count} methods")


def demonstrate_data_access(java_data: JavaCodeData):
    """Demonstrate how to access the loaded data."""
    print("\n" + "=" * 50)
    print("DATA ACCESS EXAMPLES")
    print("=" * 50)

    if java_data.classes:
        # Show first class details
        first_class = java_data.classes[0]
        print(f"\nFirst Class: {first_class.class_name}")
        print(f"Has JavaDoc: {'Yes' if first_class.java_doc else 'No'}")
        print(f"Code length: {len(first_class.code)} characters")

        # Show methods for this class
        class_methods = java_data.get_methods_by_class(first_class.class_name)
        print(f"Methods in this class: {len(class_methods)}")

        for method in class_methods:
            print(f"  - {method.src.method_name}")
            if method.dst_methods:
                print(f"    Dependencies: {len(method.dst_methods)}")
                for dep in method.dst_methods:
                    print(f"      → {dep.class_name}.{dep.method_name}")

    if java_data.methods:
        # Show method with most dependencies
        method_with_most_deps = max(java_data.methods, key=lambda m: len(m.dst_methods))
        print(f"\nMethod with most dependencies:")
        print(f"  {method_with_most_deps.src.class_name}.{method_with_most_deps.src.method_name}")
        print(f"  Dependencies: {len(method_with_most_deps.dst_methods)}")
