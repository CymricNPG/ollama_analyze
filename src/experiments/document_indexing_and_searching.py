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

import chromadb
import os
import json
from sentence_transformers import SentenceTransformer

# Initialize the embedding model
# You can also use OpenAI or other embedding providers with ChromaDB
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize ChromaDB
chroma_client = chromadb.Client()

# Create a collection for your documents
document_collection = chroma_client.create_collection(
    name="code_documentation",
    metadata={"hnsw:space": "cosine"}  # Using cosine similarity
)

def load_documents(output_dir):
    """Load documents from analysis output files"""
    all_documents = {}
    
    # Find all JSON files (excluding documentation.json)
    analysis_files = [f for f in os.listdir(output_dir) 
                     if f.endswith('.json') and f != 'documentation.json']
    
    for file_name in analysis_files:
        file_path = os.path.join(output_dir, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
                all_documents.update(analysis_data)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            
    return all_documents

def index_documents(documents):
    """Index documents into ChromaDB"""
    ids = []
    texts = []
    metadatas = []
    
    for file_path, file_info in documents.items():
        # Create a unique ID for each document
        doc_id = f"doc_{len(ids)}"
        
        # Combine description and keywords for better search
        if isinstance(file_info, dict):
            # Handle both English and German keys for compatibility
            description = file_info.get('description', file_info.get('beschreibung', ''))
            keywords = file_info.get('keywords', file_info.get('schluesselwoerter', []))
            path = file_info.get('path', file_info.get('pfad', file_path))
            
            # Combine text for embedding
            combined_text = f"{description} {' '.join(keywords)}"
            
            # Prepare metadata
            metadata = {
                "file_path": path,
                "keywords": ", ".join(keywords)
            }
            
            ids.append(doc_id)
            texts.append(combined_text)
            metadatas.append(metadata)
    
    # Add documents to collection
    document_collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas
    )
    
    print(f"Indexed {len(ids)} documents in ChromaDB")

def search_documents(query, top_k=5):
    """Search documents using vector similarity"""
    results = document_collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    # Process results
    found_docs = []
    if results and 'metadatas' in results and results['metadatas']:
        for i, metadata in enumerate(results['metadatas'][0]):
            found_docs.append({
                "file_path": metadata["file_path"],
                "keywords": metadata["keywords"],
                "document": results['documents'][0][i],
                "distance": results.get('distances', [[]])[0][i] if results.get('distances') else None
            })
    
    return found_docs

# Example usage
def main():
    output_dir = "./docs_output"
    documents = load_documents(output_dir)
    
    # Index documents
    index_documents(documents)
    
    # Now you can search
    while True:
        query = input("Enter your search query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
            
        results = search_documents(query)
        
        print("\nSearch Results:")
        for i, doc in enumerate(results):
            print(f"\n{i+1}. {doc['file_path']}")
            print(f"   Keywords: {doc['keywords']}")
            print(f"   Summary: {doc['document'][:150]}...")

if __name__ == "__main__":
    main()