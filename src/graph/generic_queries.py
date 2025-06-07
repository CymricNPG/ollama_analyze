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
    Task: Generate Cypher queries to query a Neo4j graph database based on the provided schema definition.
    Instructions:
    Use only the provided relationship types and properties.
    Do not use any other relationship types or properties that are not provided.
    If you cannot generate a Cypher statement based on the provided schema, explain the reason to the user.
    Schema:
    {schema}

    Note: Do not include any explanations or apologies in your responses.
    """
