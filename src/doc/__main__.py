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

from config import Config, LLMConfig
from doc.class_doc_generator import ClassDocumentationGenerator
from doc.method_doc_generator import MethodDocumentationGenerator
from doc.update_data import update_class_data
from java import builder
from java.models import JavaCodeData
from .update_data import read_class_updates, read_method_updates, update_class_data, update_method_data

logger = logging.getLogger(__name__)


def generate_documentation(java_data: JavaCodeData, base_dir: str = '.'):
    """Generate missing documentation for Java code."""

    logger.info("Starting documentation generation phase")

    # Get LLM configuration
    llm_config = LLMConfig()

    # Initialize documentation generator
    class_doc_generator = ClassDocumentationGenerator(llm_config, Config.get_classes_output_dir(base_dir))
    method_doc_generator = MethodDocumentationGenerator(llm_config, Config.get_methods_output_dir(base_dir))

    # Generate documentation
    class_data = class_doc_generator.generate_documentation(java_data)
    update_class_data(java_data, class_data)
    method_doc_generator.generate_documentation(java_data)


def main():
    # Set up logging
    builder.Config.setup_logging()

    java_data = builder.read_structure("../data/")

    class_updates = read_class_updates(Config.get_classes_output_dir("../data/"))
    method_updates = read_method_updates(Config.get_methods_output_dir("../data/"))
    update_class_data(java_data, class_updates)
    update_method_data(java_data, method_updates)

    generate_documentation(java_data, "../data/")


if __name__ == "__main__":
    main()
