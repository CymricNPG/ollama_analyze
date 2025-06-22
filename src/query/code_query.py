import re

from chroma.db_access import ChromaAccess
from graph.graph_query import Neo4jQuery
from llm.llm_access import LLMAccessLayer


class CodeQueryOrchestrator:
    def __init__(self, llm: LLMAccessLayer, chroma: ChromaAccess, neo4j_query: Neo4jQuery):
        self.llm = llm
        self.chroma = chroma
        self.neo4j_query = neo4j_query

    def _reformulate_query_for_vector_search(self, user_query: str) -> str:
        system_prompt = """
        Transform the user's question into effective search terms for finding relevant code documentation. 
        This will be used against a vector database to find relevant code snippets.
        
        Guidelines:
        - ALWAYS enclose your Cypher query in a markdown code block with 'vector' language specification
        - Extract key technical terms, class names, method names
        - Include synonyms and related concepts
        - Focus on actionable programming concepts
        - Keep it concise but comprehensive
        - Include maximum of 10 keywords
        - Always start the answer with the user's question
        
        Example:
        User: "How do I handle database connections?"
        Output: 
        ```vector 
        "How do I handle database connections?" 
        database connection management connection pool JDBC SQL database access
        ```
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Transform this query: {user_query}"}
        ]

        result = self.llm.chat_completion(
            model="qwen3:8b",
            temperature=0.1,
            messages=messages
        )
        print(result)
        return self._extract_vector(result)

    def _extract_vector(self, text: str) -> str:
        """Extract vector database queries from markdown code blocks."""
        # Pattern to match ```cypher ... ``` blocks
        pattern = r'```vector\s*\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches[0] if matches else ""

    def _expand_context_via_graph(self, user_query: str, chroma_results) -> list:
        """
        Extract entity names from ChromaDB results and find related entities in Neo4j
        """
        # Extract class/method names from ChromaDB metadata
        entity_names = self._extract_entities_from_chroma_results(chroma_results)

        # Build graph traversal query
        graph_expansion_query = f"""
        Query: {user_query}  
        Starting Classes: {', '.join(entity_names)}
        """
        #     f"""
        # Find all classes, methods, and relationships related to: {', '.join(entity_names)}
        # Include inheritance hierarchies, method calls, and package relationships.
        # """
        # TODO use original query !!! ->
        # Use your existing Neo4jQuery to get related entities
        graph_context = self.neo4j_query.run(graph_expansion_query)

        return graph_context

    def _extract_entities_from_chroma_results(self, chroma_results) -> list:
        """
        Parse ChromaDB results to extract class names, method names, etc.
        """
        # Extract from metadata if available
        entities = [r.get('key') for r in chroma_results]
        return entities

    def _generate_final_answer(self, user_query: str, chroma_results, graph_context) -> str:
        """
        Create comprehensive answer using all gathered context
        """

        # Format ChromaDB results
        vector_context = self._format_chroma_results(chroma_results)

        # Format graph results
        graph_context_formatted = self._format_graph_results(graph_context)

        system_prompt = """
        You are a code analysis assistant. Answer the user's question using the provided context from both documentation and code relationships.
        
        Context includes:
        1. Relevant documentation and code snippets
        2. Related classes, methods, and their relationships
        3. Code structure and dependencies
        
        Provide a comprehensive answer that explains:
        - Direct answers to the question
        - Related code patterns and examples
        - Important relationships and dependencies
        - Best practices if applicable
        """

        user_prompt = f"""
        Original Question: {user_query}
        
        Documentation Context:
        {vector_context}
        
        Code Relationships Context:
        {graph_context_formatted}
        
        Please provide a comprehensive answer based on this codebase information.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return self.llm.chat_completion(
            model="qwen3:14b",
            temperature=0.3,
            messages=messages
        )

    def query_codebase(self, user_query: str) -> str:
        """
        Main method that orchestrates the three-step process
        """

        print("# Reformulate query for vector search")
        reformulated_query = self._reformulate_query_for_vector_search(user_query)

        print("# Search ChromaDB with reformulated query")
        chroma_results = self.chroma.search_documents(reformulated_query)

        print("# Expand context through graph database")
        graph_context = self._expand_context_via_graph(user_query, chroma_results)

        print("# Generate final answer with all context")
        final_answer = self._generate_final_answer(user_query, chroma_results, graph_context)

        return final_answer
