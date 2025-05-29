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

from file_analysis_service import dateien_sammeln, datei_analysieren
from python_dependencies import python_abhaengigkeiten_finden


def load_existing_analyses(output_dir):
    """Lädt bereits existierende Analysen und erstellt ein Set von analysierten Dateipfaden."""
    analysierte_dateien = set()

    analyse_dateien = glob.glob(f"{output_dir}/*.json")

    for analyse_datei in analyse_dateien:
        try:
            with open(analyse_datei, 'r', encoding='utf-8') as f:
                analyse_data = json.load(f)
            for datei_pfad in analyse_data.keys():
                analysierte_dateien.add(datei_pfad)

        except Exception as e:
            print(f"Fehler beim Laden von {analyse_datei}: {e}")

    return analysierte_dateien


def save_file_analysis(datei_pfad, analyse_info, ausgabe_verzeichnis):
    """Speichert die Analyse einer einzelnen Datei in einer separaten JSON-Datei mit UUID als Namen."""
    datei_uuid = str(uuid.uuid4())
    ausgabe_pfad = os.path.join(ausgabe_verzeichnis, f"{datei_uuid}.json")

    # Einzelne Dateianalyse speichern
    with open(ausgabe_pfad, 'w', encoding='utf-8') as f:
        json.dump({datei_pfad: analyse_info}, f, ensure_ascii=False, indent=2)

    return ausgabe_pfad

def create_info(datei, llm_modell) :
    print(f"Analysiere {datei}...")
    analyse = datei_analysieren(datei, llm_modell)
    abhaengigkeiten = python_abhaengigkeiten_finden(datei) if datei.endswith('.py') else []

    datei_info = {
        "pfad": datei,  # Pfad zur analysierten Datei speichern
        "beschreibung": analyse["description"],
        "schluesselwoerter": analyse["keywords"],
        "abhaengigkeiten": abhaengigkeiten
    }
    return datei_info

# Analyse in separater Datei speichern

def main():
    # Konfiguration
    projekt_pfad = "../pandas-main"  # Pfad zum zu analysierenden Projektverzeichnis

    ausgabe_verzeichnis = "./docs_output"
    llm_modell = "deepseek-r1:8b"
    llm_modell = "phi4:latest"
    datei_patterns=["*.py", "*.md", "*.txt"]
    datei_patterns=["*.java"]
    ignoriere_verzeichnisse=["venv", ".git", "__pycache__"]
    ignoriere_verzeichnisse=["generated"]
    # Ausgabeverzeichnis erstellen
    os.makedirs(ausgabe_verzeichnis, exist_ok=True)

    # Bereits analysierte Dateien und deren Informationen laden
    analysierte_dateien = load_existing_analyses(ausgabe_verzeichnis)
    print(f"{len(analysierte_dateien)} bereits analysierte Dateien gefunden")

    # Dateien sammeln
    dateien = dateien_sammeln(basis_pfad=projekt_pfad, datei_patterns=datei_patterns, ignoriere_verzeichnisse=ignoriere_verzeichnisse)
    print(f"{len(dateien)} Dateien insgesamt gefunden")

    # Neue Dateien (die noch nicht analysiert wurden) identifizieren
    neue_dateien = [datei for datei in dateien if datei not in analysierte_dateien]
    print(f"{len(neue_dateien)} neue Dateien zu analysieren")

    # Neue Dateien analysieren
    for datei in neue_dateien:
        try:
            datei_info = create_info(datei, llm_modell)
            save_file_analysis(datei, datei_info, ausgabe_verzeichnis)

        except Exception as e:
            print(f"Fehler bei der Analyse von {datei}: {e}")

    print(f"Analyse abgeschlossen.")


if __name__ == "__main__":
    main()