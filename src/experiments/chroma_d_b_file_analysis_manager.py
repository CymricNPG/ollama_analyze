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

import os
import json
import uuid
import glob
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

from file_analysis_service import dateien_sammeln, datei_analysieren
from python_dependencies import python_abhaengigkeiten_finden

# Initialize ChromaDB and embedding model
chroma_client = chromadb.PersistentClient(path="./chroma_db")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def embedding_function(texts):
    return embedding_model.encode(texts).tolist()

def get_collection():
    try:
        return chroma_client.get_collection(
            name="code_documentation",
            embedding_function=embedding_function
        )
    except:
        return chroma_client.create_collection(
            name="code_documentation",
            embedding_function=embedding_function
        )

# Rest of your code follows with appropriate integration points
# ...

def save_file_analysis(datei_pfad, analyse_info, ausgabe_verzeichnis, document_collection):
    """Save file analysis to JSON and index in ChromaDB"""
    # Save to file (your existing code)
    datei_uuid = str(uuid.uuid4())
    ausgabe_pfad = os.path.join(ausgabe_verzeichnis, f"{datei_uuid}.json")
    
    with open(ausgabe_pfad, 'w', encoding='utf-8') as f:
        json.dump({datei_pfad: analyse_info}, f, ensure_ascii=False, indent=2)
    
    # Index in ChromaDB
    doc_id = f"doc_{datei_uuid}"
    description = analyse_info.get('description', analyse_info.get('beschreibung', ''))
    keywords = analyse_info.get('keywords', analyse_info.get('schluesselwoerter', []))
    
    combined_text = f"{description} {' '.join(keywords) if isinstance(keywords, list) else keywords}"
    
    metadata = {
        "file_path": datei_pfad,
        "keywords": ", ".join(keywords) if isinstance(keywords, list) else keywords
    }
    
    document_collection.add(
        ids=[doc_id],
        documents=[combined_text],
        metadatas=[metadata]
    )
    
    return ausgabe_pfad

def main():
    # Your existing code...
    document_collection = get_collection()
    # ...
    
    # When analyzing new files, also index them
    for datei in neue_dateien:
        try:
            # Your existing analysis code...
            
            # Save and index
            save_file_analysis(datei, datei_info, ausgabe_verzeichnis, document_collection)
            
        except Exception as e:
            print(f"Error analyzing {datei}: {e}")
    
    # ...