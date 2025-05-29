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
from doc.doc_generator import JavaDocumentationGenerator
from java import builder
from java.models import JavaCodeData

logger = logging.getLogger(__name__)


def generate_documentation(java_data: JavaCodeData) -> JavaCodeData:
    """Generate missing documentation for Java code."""

    logger.info("Starting documentation generation phase")

    # Get LLM configuration
    llm_config = LLMConfig()

    # Initialize documentation generator
    doc_generator = JavaDocumentationGenerator(llm_config)

    # Generate documentation
    updated_data = doc_generator.generate_missing_documentation(java_data)

    # Print statistics
    stats = doc_generator.get_statistics()
    logger.info(f"Documentation generation completed with {stats.success_rate:.1f}% success rate")

    return updated_data


def main():
    # Set up logging
    builder.Config.setup_logging()

    java_data = builder.read_structure("../data/")
    new_data = generate_documentation(java_data)


if __name__ == "__main__":
    main()
