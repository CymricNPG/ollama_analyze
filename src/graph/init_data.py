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

from graph.connection import Neo4jConnection
from graph.repository import JavaCodeRepositoryBuilder
from java import builder


def main():
    # Initialize Neo4j connection
    neo4j_conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "12345678")
    
    try:
        # Create repository
        repo = JavaCodeRepositoryBuilder(neo4j_conn)
        
        # Assuming you have your JavaCodeData instance
        builder.Config.setup_logging()

        java_code_data = builder.read_structure("../data/")
        
        # Save to Neo4j
        repo.save_java_code_data(java_code_data)
        
        print("Java code data saved successfully to Neo4j!")
        
    finally:
        neo4j_conn.close()

if __name__ == "__main__":
    main()