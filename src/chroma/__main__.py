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
from chroma.db_access import ChromaAccess
from java import builder
from java.models import JavaCodeData


def create_documents(data:JavaCodeData)->dict[str, str]:
    result = {}
    for clazz in data.classes:
        result[clazz.class_name]= clazz.java_doc
    for method in data.methods:
        result[str(method.src)] = method.java_doc
    return result

def main():
    chroma = ChromaAccess()
    print("Chroma DB connected")
    data = builder.read_structure("../data/")
    print("Data read")
    documents = create_documents(data)
    print("Documents created")
    chroma.index_documents(documents)


if __name__ == "__main__":
    main()
