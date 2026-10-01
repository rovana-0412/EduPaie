"""
EduPaie — Insertion du jeu de données de test.
15 élèves, 3 classes, 12 paiements variés (soldés, partiels, non payés).
"""
import sqlite3
from pathlib import Path

RACINE = Path(__file__).parent
DB_PATH = RACINE / "data" / "edupaie.db"

# Connexion
connexion = sqlite3.connect(DB_PATH)
connexion.execute("PRAGMA foreign_keys = ON")
curseur = connexion.cursor()

# Nettoyage
curseur.execute("DELETE FROM paiements")
curseur.execute("DELETE FROM eleves")
curseur.execute("DELETE FROM classes")

# =====================================================================
# 1. CLASSES
# =====================================================================
classes = [
    ("6ème A", "6ème", "2026-2027"),
    ("6ème B", "6ème", "2026-2027"),
    ("5ème A", "5ème", "2026-2027"),
]
curseur.executemany(
    "INSERT INTO classes (nom_classe, niveau, annee_scolaire) VALUES (?, ?, ?)",
    classes
)

# =====================================================================
# 2. ELEVES (15 élèves)
# =====================================================================
eleves = [
    # Classe 1 : 6ème A
    ("KOUASSI", "Ami", "2014-03-15", "2026-2027", 150000, 1),
    ("MENSAH", "Kofi", "2014-07-22", "2026-2027", 150000, 1),
    ("AGBEKO", "Sena", "2014-11-08", "2026-2027", 130000, 1),
    ("TCHALLA", "Yawo", "2014-05-30", "2026-2027", 150000, 1),
    ("DOSSEH", "Abla", "2014-09-12", "2026-2027", 120000, 1),
    # Classe 2 : 6ème B
    ("BASSOWA", "Efoe", "2014-02-18", "2026-2027", 150000, 2),
    ("NYAVO", "Afi", "2014-08-25", "2026-2027", 150000, 2),
    ("KPODO", "Messan", "2014-12-01", "2026-2027", 140000, 2),
    ("DUTI", "Akouvi", "2014-06-14", "2026-2027", 150000, 2),
    ("FOFO", "Kossi", "2014-10-07", "2026-2027", 130000, 2),
    # Classe 3 : 5ème A
    ("ADJO", "Kodjo", "2013-04-20", "2026-2027", 170000, 3),
    ("LAWSON", "Yawa", "2013-09-05", "2026-2027", 170000, 3),
    ("AKAKPO", "Komlan", "2013-01-28", "2026-2027", 150000, 3),
    ("SEDDOH", "Essi", "2013-07-11", "2026-2027", 170000, 3),
    ("GBAGUIDI", "Hervé", "2013-11-30", "2026-2027", 160000, 3),
]
curseur.executemany(
    """INSERT INTO eleves 
       (nom, prenom, date_naissance, annee_scolaire, montant_total_du, id_classe) 
       VALUES (?, ?, ?, ?, ?, ?)""",
    eleves
)

# =====================================================================
# 3. PAIEMENTS (variés)
# =====================================================================
paiements = [
    # Élève 1 (soldé)
    ("2026-09-15", 150000, "Mobile Money", "REC-2026-000001", 1),
    # Élève 2 (partiel) : 50 000 / 150 000
    ("2026-09-16", 50000, "Espèces", "REC-2026-000002", 2),
    # Élève 4 (partiel) : 70 000 / 150 000
    ("2026-09-17", 30000, "Espèces", "REC-2026-000003", 4),
    ("2026-10-01", 40000, "Chèque", "REC-2026-000004", 4),
    # Élève 5 (soldé)
    ("2026-09-18", 120000, "Virement", "REC-2026-000005", 5),
    # Élève 7 (partiel) : 100 000 / 150 000
    ("2026-09-20", 100000, "Mobile Money", "REC-2026-000006", 7),
    # Élève 9 (partiel) : 50 000 / 150 000
    ("2026-09-22", 50000, "Espèces", "REC-2026-000007", 9),
    # Élève 10 (soldé)
    ("2026-09-23", 130000, "Mobile Money", "REC-2026-000008", 10),
    # Élève 12 (partiel) : 130 000 / 170 000
    ("2026-09-24", 80000, "Virement", "REC-2026-000009", 12),
    ("2026-10-05", 50000, "Espèces", "REC-2026-000010", 12),
    # Élève 14 (partiel) : 150 000 / 170 000
    ("2026-09-25", 150000, "Chèque", "REC-2026-000011", 14),
    # Élève 15 (soldé)
    ("2026-09-26", 160000, "Mobile Money", "REC-2026-000012", 15),
]
curseur.executemany(
    """INSERT INTO paiements 
       (date_paiement, montant, mode_paiement, numero_recu, id_eleve) 
       VALUES (?, ?, ?, ?, ?)""",
    paiements
)

# Validation
connexion.commit()

# Résumé
curseur.execute("SELECT COUNT(*) FROM classes")
print(f"✅ {curseur.fetchone()[0]} classes insérées")
curseur.execute("SELECT COUNT(*) FROM eleves")
print(f"✅ {curseur.fetchone()[0]} élèves insérés")
curseur.execute("SELECT COUNT(*) FROM paiements")
print(f"✅ {curseur.fetchone()[0]} paiements insérés")

curseur.close()
connexion.close()

print("\n🎉 Base de données peuplée avec succès !")