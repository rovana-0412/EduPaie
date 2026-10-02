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

def initialiser_base(db_path=DB_PATH, schema_path=SCHEMA_PATH):
    """Crée une nouvelle base; refuse toujours de toucher à un fichier existant."""
    db_path = Path(db_path)
    schema_path = Path(schema_path)
    if db_path.exists():
        raise FileExistsError(
            f"Base déjà présente, aucune modification effectuée : {db_path}"
        )

    db_path.parent.mkdir(parents=True, exist_ok=True)
    script_sql = schema_path.read_text(encoding="utf-8")
    connexion = sqlite3.connect(db_path)
    try:
        connexion.executescript(script_sql)
        connexion.commit()
    except Exception:
        connexion.close()
        db_path.unlink(missing_ok=True)
        raise
    connexion.close()
    return db_path


if __name__ == "__main__":
    try:
        base_creee = initialiser_base()
    except FileExistsError as exc:
        raise SystemExit(str(exc)) from exc
    print(f"Base de données créée : {base_creee}")