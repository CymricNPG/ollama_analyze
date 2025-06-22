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

from neo4j.exceptions import CypherSyntaxError

from graph import queries
from graph.connection import Neo4jConnection
from graph.generic_queries import get_system_message, schema_text
from graph.queries import get_java_message, JavaMethodNode
from llm.llm_access import LLMAccessLayer
import re
from pystreamapi import Stream

class Neo4jQuery:
    def __init__(self, llm: LLMAccessLayer, neo4j_connection: Neo4jConnection):
        self.llm = llm
        self.neo4j_connection = neo4j_connection

    def query_database(self, neo4j_query:str, params={})-> list[ JavaMethodNode]:
        result = self.neo4j_connection.query(neo4j_query, params)
        nodes = (Stream.of(result)
                 .map(lambda x: x.get("n"))
                 .map(lambda x: JavaMethodNode.from_node(x))
                 .to_list())
        return nodes

    def _construct_cypher(self, question, history=None):
        messages = [
            {"role": "system", "content": get_system_message(get_java_message())},
            {"role": "user", "content": question},
        ]
        # Used for Cypher healing flows
        if history:
            messages.extend(history)

        completions = self.llm.chat_completion(
            model="qwen3:14b",  # deepseek-r1:14b",
            temperature=0.0,
            messages=messages
        )
        return completions

    def run(self, question):
        return self._run(question, None, True)

    def _run(self, question, history=None, retry=True):
        # Construct Cypher statement
        cypher = self._construct_cypher(question, history)
        print(cypher)
        cypher = self._extract_cypher(cypher)
        print("Found: "+cypher)
        try:
            return self.query_database(cypher)
        # Self-healing flow
        except CypherSyntaxError as e:
            # If out of retries
            if not retry:
                return "Invalid Cypher syntax"
            # Self-healing Cypher flow by providing specific error
            print("Retrying")
            return self.run(
                question,
                [
                    {"role": "assistant", "content": cypher},
                    {
                        "role": "user",
                        "content": f"""This query returns an error: {str(e)} 
                            Give me a improved query that works without any explanations or apologies""",
                    },
                ],
                retry=False
            )

    def _extract_cypher(self, text: str) -> str:
        """Extract Cypher queries from markdown code blocks."""
        # Pattern to match ```cypher ... ``` blocks
        pattern = r'```cypher\s*\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches[0] if matches else ""
