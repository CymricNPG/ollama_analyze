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
import ollama

def frage_beantworten(frage, dateien_info, graph, modell_name="llama2"):
    """Beantwortet eine Frage basierend auf den Dokumenten und dem Abhängigkeitsgraphen"""
    
    # Relevante Dokumente finden
    relevante_dateien = []
    for datei, info in dateien_info.items():
        # Einfacher Keyword-Match (kann durch Vektorähnlichkeit verbessert werden)
        if any(kw in frage.lower() for kw in info.get('schluesselwoerter', [])):
            relevante_dateien.append(datei)
    
    # Top 5 relevanteste Dateien auswählen
    relevante_dateien = relevante_dateien[:5]
    
    # Kontext für LLM erstellen
    kontext = "\n\n".join([
        f"Datei: {os.path.basename(datei)}\n"
        f"Beschreibung: {dateien_info[datei]['beschreibung']}\n"
        f"Schlüsselwörter: {', '.join(dateien_info[datei].get('schluesselwoerter', []))}"
        for datei in relevante_dateien
    ])
    
    # Abhängigkeitsinformationen hinzufügen
    abhaengigkeiten_info = ""
    for datei in relevante_dateien:
        if datei in graph:
            eingehende = list(graph.predecessors(datei))
            ausgehende = list(graph.successors(datei))
            
            abhaengigkeiten_info += f"\nDatei {os.path.basename(datei)} Abhängigkeiten:\n"
            if eingehende:
                abhaengigkeiten_info += f"- Wird verwendet von: {', '.join(os.path.basename(d) for d in eingehende)}\n"
            if ausgehende:
                abhaengigkeiten_info += f"- Verwendet: {', '.join(os.path.basename(d) for d in ausgehende)}\n"
    
    # Prompt erstellen
    prompt = f"""
    Basierend auf den folgenden Dokumenten und deren Abhängigkeiten, beantworte diese Frage:
    
    Frage: {frage}
    
    Dokumente:
    {kontext}
    
    Abhängigkeiten:
    {abhaengigkeiten_info}
    
    Antworte klar und präzise, basierend nur auf den bereitgestellten Informationen.
    """
    
    # Mit Ollama API
    response = ollama.generate(model=modell_name, prompt=prompt)
    return response['response']