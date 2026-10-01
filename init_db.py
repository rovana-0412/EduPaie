"""
EduPaie — Script d'initialisation de la base de données SQLite.
Exécute le fichier schema.sql pour créer les tables.
"""
import sqlite3
from pathlib import Path

# Chemins
RACINE = Path(__file__).parent
DB_PATH = RACINE / "data" / "edupaie.db"
SCHEMA_PATH = RACINE / "schema.sql"

# Créer le dossier data/ s'il n'existe pas
DB_PATH.parent.mkdir(exist_ok=True)

# Lire le script SQL
with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    script_sql = f.read()

# Connexion et exécution
connexion = sqlite3.connect(DB_PATH)
connexion.executescript(script_sql)
connexion.commit()
connexion.close()

print(f"✅ Base de données créée : {DB_PATH}")