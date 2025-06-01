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
from config import Config
from doc.update_data import read_class_updates, read_method_updates, update_class_data, update_method_data
from java import builder
from report.JavaDocumentationGenerator import generate_html
from report.JavaHTMLDocumentationGenerator import JavaCodeHTMLGenerator


def main():
    java_data = builder.read_structure("../data/")

    class_updates = read_class_updates(Config.get_classes_output_dir("../data/"))
    method_updates = read_method_updates(Config.get_methods_output_dir("../data/"))
    update_class_data(java_data, class_updates)
    update_method_data(java_data, method_updates)
    generate_html(java_data, "../data/doc_chathpt.html")

    reporter = JavaCodeHTMLGenerator(java_data)
    reporter.generate_html("../data/doc_claude.html")

if __name__ == "__main__":
    main()
