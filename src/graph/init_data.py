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
from java import builder
from java.models import JavaCodeData, JavaClass, JavaMethod, MethodReference
from graph.connection import Neo4jConnection


class JavaCodeRepositoryBuilder:
    def __init__(self, neo4j_connection: Neo4jConnection):
        self.db = neo4j_connection

    def _clean_database(self):
        """Completely clean the Neo4j database"""
        query = "MATCH (n) DETACH DELETE n"
        self.db.write_transaction(query)

    def save_java_code_data(self, java_code_data: JavaCodeData):
        """Save complete Java code data to Neo4j"""
        # clean database
        self._clean_database()

        # Create constraints and indexes
        self._create_constraints()

        # Save classes
        for java_class in java_code_data.classes:
            self._save_class(java_class)

        # Save methods
        for method in java_code_data.methods:
            self._save_method(method)

        # Create relationships
        for method in java_code_data.methods:
            self._create_method_relationships(method)

    def _create_constraints(self):
        """Create unique constraints for nodes"""
        constraints = [
            "CREATE CONSTRAINT class_name_unique IF NOT EXISTS FOR (c:Class) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT method_unique IF NOT EXISTS FOR (m:Method) REQUIRE (m.className, m.methodName) IS UNIQUE"
        ]

        for constraint in constraints:
            try:
                self.db.query(constraint)
            except Exception as e:
                print(f"Constraint creation warning: {e}")

    def _save_class(self, java_class: JavaClass):
        """Save a Java class to Neo4j"""
        query = """
        MERGE (c:Class {name: $class_name})
        SET c.javaDoc = $java_doc,
            c.code = $code,
            c.updatedAt = datetime()
        """

        parameters = {
            'class_name': java_class.class_name,
            'java_doc': java_class.java_doc,
            'code': java_class.code
        }

        self.db.write_transaction(query, parameters)

    def _save_method(self, method: JavaMethod):
        """Save a Java method to Neo4j"""
        query = """
        MERGE (m:Method {className: $class_name, methodName: $method_name})
        SET m.javaDoc = $java_doc,
            m.code = $code,
            m.updatedAt = datetime()
        WITH m
        MATCH (c:Class {name: $class_name})
        MERGE (c)-[:HAS_METHOD]->(m)
        """

        parameters = {
            'class_name': method.src.class_name,
            'method_name': method.src.method_name,
            'java_doc': method.java_doc,
            'code': method.code
        }

        self.db.write_transaction(query, parameters)

    def _create_method_relationships(self, method: JavaMethod):
        """Create relationships between methods"""
        if not method.dst_methods:
            return

        for dst_method in method.dst_methods:
            query = """
            MATCH (source:Method {className: $src_class, methodName: $src_method})
            MERGE (target:Method {className: $dst_class, methodName: $dst_method})
            MERGE (source)-[:CALLS]->(target)
            """

            parameters = {
                'src_class': method.src.class_name,
                'src_method': method.src.method_name,
                'dst_class': dst_method.class_name,
                'dst_method': dst_method.method_name
            }

            self.db.write_transaction(query, parameters)


def main():
    # Initialize Neo4j connection
    neo4j_conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "12345678")

    try:
        # Create repository
        repo = JavaCodeRepositoryBuilder(neo4j_conn)

        builder.Config.setup_logging()

        java_code_data = builder.read_structure("../data/")

        # Save to Neo4j
        repo.save_java_code_data(java_code_data)

        print("Java code data saved successfully to Neo4j!")

    finally:
        neo4j_conn.close()


if __name__ == "__main__":
    main()
