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
import glob
import json
import re
import ollama

def dateien_sammeln(basis_pfad, datei_patterns=["*.py", "*.md", "*.txt"], 
                  ignoriere_verzeichnisse=["venv", ".git", "__pycache__"]):
    """Sammelt alle zu analysierenden Dateien"""
    dateien = []
    for pattern in datei_patterns:
        for pfad in glob.glob(f"{basis_pfad}/**/{pattern}", recursive=True):
            if not any(ignore in pfad for ignore in ignoriere_verzeichnisse):
                dateien.append(pfad)
    return dateien

def datei_analysieren(datei_pfad, modell_name="llama2"):
    """Analysiert eine Datei mit Ollama und extrahiert Beschreibung und Schlüsselwörter"""
    with open(datei_pfad, 'r', encoding='utf-8') as f:
        inhalt = f.read()

    prompt = f"""
    Analyze this file and create:
    1. A brief summary (maximum 3 sentences)
    2. A list of 5-10 keywords
    
    Format the output as JSON with the keys 'description' and 'keywords'.
    
    File: {os.path.basename(datei_pfad)}

    ```
    {inhalt[:10000]}  # Limitieren für große Dateien
    ```
    """
    
    # Mit Ollama API
    response = ollama.generate(model=modell_name, prompt=prompt)
    
    # Extrahieren des JSON aus der Antwort
    try:
        # Nach JSON-Format suchen
        json_str = re.search(r'\{.*\}', response['response'], re.DOTALL).group()
        return json.loads(json_str)
    except:
        # Fallback, wenn kein gültiges JSON gefunden wurde
        return {
            "description": "Couldn't create a description for this file.",
            "keywords": []
        }