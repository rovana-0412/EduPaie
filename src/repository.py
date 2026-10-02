"""
EduPaie — Repository (accès aux données SQLite).
Encapsule toutes les requêtes SQL pour les entités Classe, Eleve, Paiement.
"""
import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple

from src.constants import (
    ANNEE_SCOLAIRE_DEFAUT,
    CLASSES_ETABLISSEMENT,
    niveau_de_classe,
    ordre_classe,
)
from src.models import Classe, Eleve, Paiement, SoldeEleve


class Database:
    """Gère la connexion à la base de données SQLite."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.connexion: Optional[sqlite3.Connection] = None

    def connecter(self):
        """Ouvre la connexion et active les clés étrangères."""
        self.connexion = sqlite3.connect(self.db_path)
        self.connexion.execute("PRAGMA foreign_keys = ON")
        self.connexion.row_factory = sqlite3.Row

    def deconnecter(self):
        """Ferme la connexion."""
        if self.connexion:
            self.connexion.close()
            self.connexion = None

    def curseur(self) -> sqlite3.Cursor:
        if not self.connexion:
            raise RuntimeError("Connexion non ouverte. Appelez connecter() d'abord.")
        return self.connexion.cursor()

    def valider(self):
        if self.connexion:
            self.connexion.commit()


class ClasseRepository:
    """Accès aux données de la table classes."""

    def __init__(self, db: Database):
        self.db = db

    def lister_toutes(self) -> List[Classe]:
        cur = self.db.curseur()
        cur.execute("SELECT * FROM classes")
        classes = [Classe(**dict(row)) for row in cur.fetchall()]
        return sorted(classes, key=lambda classe: ordre_classe(classe.nom_classe))

    def ajouter_classes_etablissement(
        self, annee_scolaire: str = ANNEE_SCOLAIRE_DEFAUT
    ):
        """Ajoute les classes standard manquantes sans modifier les inscriptions."""
        cur = self.db.curseur()
        cur.executemany(
            """
            INSERT OR IGNORE INTO classes (nom_classe, niveau, annee_scolaire)
            VALUES (?, ?, ?)
            """,
            [
                (nom, niveau_de_classe(nom), annee_scolaire)
                for nom in CLASSES_ETABLISSEMENT
            ],
        )
        self.db.valider()

    def ajouter(self, nom_classe: str, niveau: str, annee_scolaire: str) -> int:
        """Ajoute une classe et retourne son identifiant."""
        try:
            cur = self.db.curseur()
            cur.execute(
                """
                INSERT INTO classes (nom_classe, niveau, annee_scolaire)
                VALUES (?, ?, ?)
                """,
                (nom_classe, niveau, annee_scolaire),
            )
        except sqlite3.IntegrityError as exc:
            if "UNIQUE constraint failed" not in str(exc):
                raise
            raise ValueError(
                f"La classe « {nom_classe} » existe déjà pour l'année "
                f"scolaire {annee_scolaire}."
            ) from exc
        self.db.valider()
        return cur.lastrowid

    def trouver_par_id(self, id_classe: int) -> Optional[Classe]:
        cur = self.db.curseur()
        cur.execute("SELECT * FROM classes WHERE id_classe = ?", (id_classe,))
        row = cur.fetchone()
        return Classe(**dict(row)) if row else None


class EleveRepository:
    """Accès aux données de la table eleves."""

    def __init__(self, db: Database):
        self.db = db

    def lister_tous(self) -> List[Eleve]:
        cur = self.db.curseur()
        cur.execute("SELECT * FROM eleves ORDER BY nom, prenom")
        return [Eleve(**dict(row)) for row in cur.fetchall()]

    def trouver_par_id(self, id_eleve: int) -> Optional[Eleve]:
        cur = self.db.curseur()
        cur.execute("SELECT * FROM eleves WHERE id_eleve = ?", (id_eleve,))
        row = cur.fetchone()
        return Eleve(**dict(row)) if row else None

    def rechercher_par_nom(self, terme: str) -> List[Eleve]:
        cur = self.db.curseur()
        cur.execute(
            "SELECT * FROM eleves WHERE nom LIKE ? OR prenom LIKE ? ORDER BY nom",
            (f"%{terme}%", f"%{terme}%")
        )
        return [Eleve(**dict(row)) for row in cur.fetchall()]

    def ajouter(self, eleve: Eleve) -> int:
        cur = self.db.curseur()
        cur.execute("""
            INSERT INTO eleves (nom, prenom, date_naissance, annee_scolaire, montant_total_du, id_classe)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (eleve.nom, eleve.prenom, eleve.date_naissance,
              eleve.annee_scolaire, eleve.montant_total_du, eleve.id_classe))
        self.db.valider()
        return cur.lastrowid

    def modifier(self, eleve: Eleve):
        cur = self.db.curseur()
        cur.execute("""
            UPDATE eleves SET nom = ?, prenom = ?, date_naissance = ?,
                              annee_scolaire = ?, montant_total_du = ?, id_classe = ?
            WHERE id_eleve = ?
        """, (eleve.nom, eleve.prenom, eleve.date_naissance,
              eleve.annee_scolaire, eleve.montant_total_du, eleve.id_classe,
              eleve.id_eleve))
        self.db.valider()

    def supprimer(self, id_eleve: int):
        cur = self.db.curseur()
        cur.execute("DELETE FROM eleves WHERE id_eleve = ?", (id_eleve,))
        self.db.valider()


class PaiementRepository:
    """Accès aux données de la table paiements."""

    def __init__(self, db: Database):
        self.db = db

    def lister_par_eleve(self, id_eleve: int) -> List[Paiement]:
        cur = self.db.curseur()
        cur.execute(
            """
            SELECT * FROM paiements
            WHERE id_eleve = ?
            ORDER BY date_paiement DESC, id_paiement DESC
            """,
            (id_eleve,)
        )
        return [Paiement(**dict(row)) for row in cur.fetchall()]

    def somme_par_eleve(self, id_eleve: int) -> float:
        cur = self.db.curseur()
        cur.execute(
            "SELECT COALESCE(SUM(montant), 0) FROM paiements WHERE id_eleve = ?",
            (id_eleve,)
        )
        return float(cur.fetchone()[0])

    def ajouter(self, paiement: Paiement) -> int:
        cur = self.db.curseur()
        cur.execute("""
            INSERT INTO paiements (date_paiement, montant, mode_paiement, numero_recu, id_eleve)
            VALUES (?, ?, ?, ?, ?)
        """, (paiement.date_paiement, paiement.montant,
              paiement.mode_paiement, paiement.numero_recu, paiement.id_eleve))
        self.db.valider()
        return cur.lastrowid

    def prochain_numero_recu(self, annee: int) -> str:
        """Retourne le prochain numéro après le plus grand numéro existant."""
        cur = self.db.curseur()
        prefixe = f"REC-{annee}-"
        cur.execute(
            """
            SELECT COALESCE(MAX(CAST(substr(numero_recu, ?) AS INTEGER)), 0)
            FROM paiements
            WHERE numero_recu LIKE ?
              AND length(substr(numero_recu, ?)) > 0
              AND substr(numero_recu, ?) NOT GLOB '*[^0-9]*'
            """,
            (len(prefixe) + 1, f"{prefixe}%", len(prefixe) + 1, len(prefixe) + 1),
        )
        return f"{prefixe}{int(cur.fetchone()[0]) + 1:06d}"

    def ajouter_avec_numero_recu(
        self, paiement: Paiement, annee: int
    ) -> Tuple[int, str]:
        """Attribue et insère le numéro dans une transaction SQLite exclusive."""
        connexion = self.db.connexion
        if connexion is None:
            raise RuntimeError("Connexion non ouverte. Appelez connecter() d'abord.")

        connexion.execute("BEGIN IMMEDIATE")
        try:
            numero_recu = self.prochain_numero_recu(annee)
            cur = connexion.execute(
                """
                INSERT INTO paiements
                    (date_paiement, montant, mode_paiement, numero_recu, id_eleve)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    paiement.date_paiement,
                    paiement.montant,
                    paiement.mode_paiement,
                    numero_recu,
                    paiement.id_eleve,
                ),
            )
            connexion.commit()
            return cur.lastrowid, numero_recu
        except Exception:
            connexion.rollback()
            raise

    def compter_recus_annee(self, annee: int) -> int:
        """Compte le nombre de reçus émis pour une année donnée."""
        cur = self.db.curseur()
        cur.execute(
            "SELECT COUNT(*) FROM paiements WHERE numero_recu LIKE ?",
            (f"REC-{annee}-%",)
        )
        return int(cur.fetchone()[0])

    def trouver_par_id(self, id_paiement: int) -> Optional[Paiement]:
        cur = self.db.curseur()
        cur.execute("SELECT * FROM paiements WHERE id_paiement = ?", (id_paiement,))
        row = cur.fetchone()
        return Paiement(**dict(row)) if row else None