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

import re
import networkx as nx
import os

def python_abhaengigkeiten_finden(datei_pfad):
    """Identifiziert Import-Abhängigkeiten in Python-Dateien"""
    if not datei_pfad.endswith('.py'):
        return []
    
    abhaengigkeiten = []
    try:
        with open(datei_pfad, 'r', encoding='utf-8') as f:
            inhalt = f.read()
        
        # Imports finden
        import_patterns = [
            r'^import\s+(\w+)',
            r'^from\s+(\w+)\s+import',
            r'^import\s+(\w+\.\w+)'
        ]
        
        for zeile in inhalt.split('\n'):
            zeile = zeile.strip()
            for pattern in import_patterns:
                matches = re.findall(pattern, zeile)
                abhaengigkeiten.extend(matches)
        
        return abhaengigkeiten
    except Exception as e:
        print(f"Fehler bei {datei_pfad}: {e}")
        return []

def dependency_graph_erstellen(dateien_info):
    """Erstellt einen Dependency-Graph basierend auf den Dateianalysen"""
    graph = nx.DiGraph()
    
    # Alle Dateien als Knoten hinzufügen
    for datei in dateien_info:
        graph.add_node(datei, 
                       label=os.path.basename(datei),
                       description=dateien_info[datei].get('beschreibung', ''))
    
    # Abhängigkeiten als Kanten hinzufügen
    for datei, info in dateien_info.items():
        if 'abhaengigkeiten' in info:
            for abhaengigkeit in info['abhaengigkeiten']:
                # Modulnamen zu tatsächlichen Dateipfaden zuordnen (vereinfacht)
                for ziel_datei in dateien_info:
                    if ziel_datei.endswith(f"{abhaengigkeit}.py"):
                        graph.add_edge(datei, ziel_datei)
    
    return graph