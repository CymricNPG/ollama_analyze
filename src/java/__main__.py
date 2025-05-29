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

Main application for reading and print data
"""

from . import builder

def main():
    """Main application entry point."""
    # Set up logging
    builder.Config.setup_logging()

    java_data = builder.read_structure("../data/")

    # Display summary
    builder.print_data_summary(java_data)

    # Example usage
    builder.demonstrate_data_access(java_data)

if __name__ == "__main__":
    main()
