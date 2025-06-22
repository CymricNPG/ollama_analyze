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

Main application for querying data
"""
from chroma.db_access import ChromaAccess
from graph.connection import Neo4jConnection
from graph.graph_query import Neo4jQuery
from llm.llm_access import LLMAccessLayer
from query.code_query import CodeQueryOrchestrator


def main():
    query = "How is the stopping of trains in stations implemented?"
    chroma = ChromaAccess()
    llm = LLMAccessLayer()
    neo4j_connection = Neo4jConnection("bolt://localhost:7687", "neo4j", "12345678")
    neo4j = Neo4jQuery(llm, neo4j_connection)
    orchestrator = CodeQueryOrchestrator(llm, chroma, neo4j)
    result = orchestrator.query_codebase(query)
    print(result)


if __name__ == "__main__":
    main()
