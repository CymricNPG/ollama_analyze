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
from config import LLMConfig
from graph.connection import Neo4jConnection
from graph.graph_query import Neo4jQuery
from llm.llm_access import LLMAccessLayer


def main():
    config = LLMConfig()
    llm_access = LLMAccessLayer(config)
    neo4j_conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "12345678")
    neo4j_query =   Neo4jQuery(llm_access, neo4j_conn)
    # error: neo4j_query.run("What methods do handle the pathfinding?")
    neo4j_query.run("What methods use the class PreMove?")
if __name__ == "__main__":
    main()