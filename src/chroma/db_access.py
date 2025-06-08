
import chromadb
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions

class ChromaAccess :
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path="../data/chroma_db")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Create a collection for your documents
        self.document_collection = self._get_collection()

    # Create or get an existing collection
    def _get_collection(self):
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        try:
            # Try to get existing collection
            return self.chroma_client.get_collection(
                name="code_documentation",
                embedding_function=sentence_transformer_ef
            )
        except:
            # Create new collection if it doesn't exist
            return self.chroma_client.create_collection(
                name="code_documentation",
                embedding_function=sentence_transformer_ef,
                metadata={"hnsw:space": "cosine"}
            )

    def index_documents(self, documents: dict[str, str]):
        """Index documents into ChromaDB"""
        ids = []
        texts = []
        metadatas = []

        for key, text in documents.items():
            if text is None:
                continue
            # Create a unique ID for each document
            doc_id = f"doc_{len(ids)}"
            ids.append(doc_id)
            texts.append(text)
            metadatas.append({"key":key})

        # Add documents to collection
        self.document_collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )

        print(f"Indexed {len(ids)} documents in ChromaDB")
#
    def search_documents(self, query, top_k=5):
        """Search documents using vector similarity"""
        results = self.document_collection.query(
            query_texts=[query],
            n_results=top_k
        )

        # Process results
        found_docs = []
        if results and 'metadatas' in results and results['metadatas']:
            for i, metadata in enumerate(results['metadatas'][0]):
                found_docs.append( metadata)

        return found_docs
#
# # Example usage
# def main():
#     output_dir = "./docs_output"
#     documents = load_documents(output_dir)
#
#     # Index documents
#     index_documents(documents)
#
#     # Now you can search
#     while True:
#         query = input("Enter your search query (or 'exit' to quit): ")
#         if query.lower() == 'exit':
#             break
#
#         results = search_documents(query)
#
#         print("\nSearch Results:")
#         for i, doc in enumerate(results):
#             print(f"\n{i+1}. {doc['file_path']}")
#             print(f"   Keywords: {doc['keywords']}")
#             print(f"   Summary: {doc['document'][:150]}...")
#
# if __name__ == "__main__":
#     main()