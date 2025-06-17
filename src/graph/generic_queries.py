# Apoc Plugin must be installed
# source https://github.com/tomasonjo/blogs/blob/master/llm/generic_cypher_gpt4.ipynb

query_node_properties = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE NOT type = "RELATIONSHIP" AND elementType = "node"
WITH label AS nodeLabels, collect(property) AS properties
RETURN {labels: nodeLabels, properties: properties} AS output
"""

rel_properties_query = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE NOT type = "RELATIONSHIP" AND elementType = "relationship"
WITH label AS nodeLabels, collect(property) AS properties
RETURN {type: nodeLabels, properties: properties} AS output
"""

rel_query = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE type = "RELATIONSHIP" AND elementType = "node"
RETURN {source: label, relationship: property, target: other} AS output
"""

def schema_text(node_props, rel_props, rels):
    return f"""
  This is the schema representation of the Neo4j database.
  Node properties are the following:
  {node_props}
  Relationship properties are the following:
  {rel_props}
  Relationship point from source to target nodes
  {rels}
  Make sure to respect relationship types and directions
  """

def get_system_message(schema:str):
    return f"""
Task: Generate a Cypher query to retrieve data from a Neo4j graph database.

Instructions:
1. ALWAYS enclose your Cypher query in a markdown code block with 'cypher' language specification
2. Use ONLY the node labels, relationship types, and properties defined in the schema below
3. Use pattern matching (CONTAINS, STARTS WITH, ENDS WITH, or regex) instead of exact name matching
4. Make queries case-insensitive when matching text properties using toLower()
5. Focus on the most relevant data for the user's question
6. If the schema doesn't contain sufficient information, state what's missing

Schema:
{schema}

Guidelines for query construction:
- Use WHERE clauses with CONTAINS for partial text matching: WHERE toLower(n.name) CONTAINS toLower("searchterm")
- Use relationships to traverse the graph meaningfully
- Return the most relevant nodes/relationships for the question
- Limit results if appropriate using LIMIT clause
- Use DISTINCT to avoid duplicates when needed

Example format:
```cypher
MATCH (n:NodeType)-[:RELATIONSHIP_TYPE]->(m:AnotherType)
WHERE toLower(n.name) CONTAINS toLower("keyword")
RETURN n, m
LIMIT 10
```
"""