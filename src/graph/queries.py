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

node_props = """
  {
    "labels": "Class",
    "properties": [
      "name",
      "javaDoc",
      "code",
      "updatedAt"
    ]
  },
  {
    "labels": "Method",
    "properties": [
      "className",
      "methodName",
      "code",
      "updatedAt",
      "javaDoc"
    ]
  }
"""
rels = """
  {
    "relationship": "HAS_METHOD",
    "source": "Class",
    "target": [
      "Method"
    ]
  },
  {
    "relationship": "CALLS",
    "source": "Method",
    "target": [
      "Method"
    ]
  }
"""


def get_java_schema_text() -> str:
    return f"""
  This is the schema representation of the Neo4j database.
  Node properties are the following:
  {node_props}
  Relationship point from source to target nodes
  {rels}
  Make sure to respect relationship types and directions
  """

def get_java_message():
    schema = get_java_schema_text()
    return f"""
    Task: Generate Cypher queries to query a Neo4j graph database based on the provided schema definition.
    Instructions:
    Use only the provided relationship types and properties.
    Do not use any other relationship types or properties that are not provided.
    If you cannot generate a Cypher statement based on the provided schema, explain the reason to the user.
    Schema:
    {schema}

    Note: Do not include any explanations or apologies in your responses.
    """