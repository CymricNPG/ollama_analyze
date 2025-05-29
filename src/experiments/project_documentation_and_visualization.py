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

from src.document_question_answering import frage_beantworten
from src.file_analysis_service import dateien_sammeln, datei_analysieren

import networkx as nx
import matplotlib.pyplot as plt

from src.python_dependencies import python_abhaengigkeiten_finden, dependency_graph_erstellen


def main():
    # Konfiguration
    projekt_pfad = "../pandas-main"  # Pfad zum zu analysierenden Projektverzeichnis
    ausgabe_verzeichnis = "./docs_output"
    llm_modell = "deepseek-r1:8b"
    
    # Ausgabeverzeichnis erstellen
    os.makedirs(ausgabe_verzeichnis, exist_ok=True)
    
    # Dateien sammeln
    dateien = dateien_sammeln(projekt_pfad)
    print(f"{len(dateien)} Dateien gefunden")
    
    # Dateien analysieren
    dateien_info = {}
    for datei in dateien:
        print(f"Analysiere {datei}...")
        analyse = datei_analysieren(datei, llm_modell)
        abhaengigkeiten = python_abhaengigkeiten_finden(datei) if datei.endswith('.py') else []
        
        dateien_info[datei] = {
            "beschreibung": analyse["beschreibung"],
            "schluesselwoerter": analyse["schluesselwoerter"],
            "abhaengigkeiten": abhaengigkeiten
        }
    
    # Ergebnisse speichern
    with open(f"{ausgabe_verzeichnis}/dokumentation.json", 'w', encoding='utf-8') as f:
        json.dump(dateien_info, f, ensure_ascii=False, indent=2)
    
    # Dependency-Graph erstellen
    graph = dependency_graph_erstellen(dateien_info)
    
    # Graph speichern (für Visualisierungstools wie Gephi)
    nx.write_gexf(graph, f"{ausgabe_verzeichnis}/dependencies.gexf")
    
    # Einfache Visualisierung erstellen
    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_size=500, font_size=8)
    plt.savefig(f"{ausgabe_verzeichnis}/graph.png")
    
    # Interaktive Abfrage
    print("\nDokumentation und Graph erstellt. Sie können nun Fragen stellen.")
    while True:
        frage = input("\nFrage (oder 'exit' zum Beenden): ")
        if frage.lower() == 'exit':
            break
        
        antwort = frage_beantworten(frage, dateien_info, graph, llm_modell)
        print(f"\nAntwort:\n{antwort}")

