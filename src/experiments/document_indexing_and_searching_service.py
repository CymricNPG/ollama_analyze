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

# Initialize with persistent storage
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Use a custom embedding function with SentenceTransformer
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def embedding_function(texts):
    return embedding_model.encode(texts).tolist()

# Create or get an existing collection
def get_collection():
    try:
        # Try to get existing collection
        return chroma_client.get_collection(
            name="code_documentation",
            embedding_function=embedding_function
        )
    except:
        # Create new collection if it doesn't exist
        return chroma_client.create_collection(
            name="code_documentation",
            embedding_function=embedding_function,
            metadata={"hnsw:space": "cosine"}
        )

document_collection = get_collection()

def load_and_index_documents(output_dir):
    """Load and index documents from analysis output files"""
    # Get list of documents already in the collection
    if document_collection.count() > 0:
        existing_docs = set()
        # You would need to implement a way to get existing document paths
        # This is simplified - you might need to query and extract from metadata
        
        print(f"Found {len(existing_docs)} documents already indexed")
    else:
        existing_docs = set()
    
    # Load all documents
    new_docs = 0
    analysis_files = [f for f in os.listdir(output_dir) 
                     if f.endswith('.json') and f != 'documentation.json']
    
    for file_name in analysis_files:
        file_path = os.path.join(output_dir, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
                
                for doc_path, doc_info in analysis_data.items():
                    if doc_path in existing_docs:
                        continue  # Skip already indexed documents
                    
                    # Process document for indexing (similar to previous example)
                    # Create a unique ID based on filepath hash
                    doc_id = f"doc_{hash(doc_path)}"
                    
                    # Handle keys in both languages
                    description = doc_info.get('description', doc_info.get('beschreibung', ''))
                    keywords = doc_info.get('keywords', doc_info.get('schluesselwoerter', []))
                    
                    # Combine text for embedding
                    combined_text = f"{description} {' '.join(keywords)}"
                    
                    # Prepare metadata
                    metadata = {
                        "file_path": doc_path,
                        "keywords": ", ".join(keywords) if isinstance(keywords, list) else keywords
                    }
                    
                    # Add to collection
                    document_collection.add(
                        ids=[doc_id],
                        documents=[combined_text],
                        metadatas=[metadata]
                    )
                    
                    new_docs += 1
                    
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"Added {new_docs} new documents to the index")
    return document_collection.count()

# Example usage in a complete system
def main():
    output_dir = "./docs_output"
    
    # Load and index documents
    total_docs = load_and_index_documents(output_dir)
    print(f"Total documents in collection: {total_docs}")
    
    # Interactive search loop
    print("\nVector Search Ready - Enter your questions about the codebase")
    while True:
        query = input("\nSearch query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
            
        results = document_collection.query(
            query_texts=[query],
            n_results=5
        )
        
        print("\nSearch Results:")
        if results and results['metadatas'] and results['metadatas'][0]:
            for i, metadata in enumerate(results['metadatas'][0]):
                print(f"\n{i+1}. File: {metadata['file_path']}")
                print(f"   Keywords: {metadata['keywords']}")
                print(f"   Summary: {results['documents'][0][i][:150]}...")
                if 'distances' in results and results['distances']:
                    print(f"   Relevance: {1 - results['distances'][0][i]:.2f}")  # Convert distance to similarity score
        else:
            print("No matching documents found.")

if __name__ == "__main__":
    main()