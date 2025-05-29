from typing import List, Optional

import logging
from java.models import JavaCodeData, JavaClass, JavaUpdateMethod, MethodSource, JavaUpdateClass
from pathlib import Path
import json

logger = logging.getLogger(__name__)


def update_method_data(java_data: JavaCodeData, method_data: List[JavaUpdateMethod]):
    """
    Update javadoc data of methods in java_data with new data from method_data.
    :param java_data: An instance of `JavaCodeData` containing the existing Java classes and their documentation.
    :type java_data: JavaCodeData

    :param method_data: A list of new or updated objects to be checked for updating documentation.
    :type method_data: List[JavaUpdateMethod]

    """
    # Update existing classes with new documentation
    updated_methods = 0
    for new_method in method_data:
        existing_method = java_data.get_method_by_name(new_method.src)

        if existing_method and not existing_method.java_doc:
            existing_method.java_doc = new_method.java_doc
    updated_methods += 1

    logger.info(f"Updated documentation for {updated_methods} methods.")


def update_class_data(java_data: JavaCodeData, class_data: List[JavaUpdateClass]):
    """
    Update javadoc data of classes in java_data with new data from class_data.
    :param java_data: An instance of `JavaCodeData` containing the existing Java classes and their documentation.
    :type java_data: JavaCodeData

    :param class_data: A list of new or updated `JavaClass` objects to be checked for updating documentation.
    :type class_data: List[JavaClass]

    """
    # Update existing classes with new documentation
    updated_classes = 0
    for new_class in class_data:
        existing_class = java_data.get_class_by_name(new_class.class_name)
        if existing_class and not existing_class.java_doc:
            existing_class.java_doc = new_class.java_doc
            updated_classes += 1

    logger.info(f"Updated documentation for {updated_classes} classes.")


def read_method_file(file_path: Path) -> Optional[JavaUpdateMethod]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return JavaUpdateMethod.__from_dict__(data)
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
    return None


def read_method_updates(directory: str) -> list[JavaUpdateMethod]:
    methods = []
    target_dir = Path(directory)
    json_files = list(target_dir.glob("*.json"))
    for file_path in json_files:
        item = read_method_file(file_path)
        if item:
            methods.append(item)
    return methods


def read_class_file(file_path: Path) -> Optional[JavaUpdateClass]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return JavaUpdateClass.__from_dict__(data)
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
    return None


def read_class_updates(directory: str) -> list[JavaUpdateClass]:
    methods = []
    target_dir = Path(directory)
    json_files = list(target_dir.glob("*.json"))
    for file_path in json_files:
        item = read_class_file(file_path)
        if item:
            methods.append(item)
    return methods
