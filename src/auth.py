"""Authentification de l'administrateur de l'application."""
import hashlib
import hmac
import os
import sqlite3

from src.repository import Database


class AuthService:
    """Crée le compte administrateur initial et vérifie les connexions."""

    ITERATIONS = 600_000
    LONGUEUR_MIN_MOT_DE_PASSE = 10
    LONGUEUR_MAX_IDENTIFIANT = 64

    def __init__(self, db: Database):
        self.db = db

    def initialiser(self):
        """Crée la table d'authentification sans modifier les données scolaires."""
        cur = self.db.curseur()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS administrateur (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                identifiant TEXT NOT NULL UNIQUE,
                sel BLOB NOT NULL,
                empreinte_mot_de_passe BLOB NOT NULL,
                iterations INTEGER NOT NULL
            )
        """)
        self.db.valider()

    def compte_configure(self) -> bool:
        cur = self.db.curseur()
        cur.execute("SELECT 1 FROM administrateur WHERE id = 1")
        return cur.fetchone() is not None

    def creer_compte(self, identifiant: str, mot_de_passe: str):
        """Crée le compte unique après validation de l'identifiant et du mot de passe."""
        identifiant = identifiant.strip().casefold()
        if not 3 <= len(identifiant) <= self.LONGUEUR_MAX_IDENTIFIANT:
            raise ValueError("L'identifiant doit contenir entre 3 et 64 caractères.")
        if len(mot_de_passe) < self.LONGUEUR_MIN_MOT_DE_PASSE:
            raise ValueError("Le mot de passe doit contenir au moins 10 caractères.")
        if self.compte_configure():
            raise ValueError("Le compte administrateur est déjà configuré.")

        sel = os.urandom(16)
        empreinte = hashlib.pbkdf2_hmac(
            "sha256",
            mot_de_passe.encode("utf-8"),
            sel,
            self.ITERATIONS,
        )
        try:
            self.db.curseur().execute(
                """
                INSERT INTO administrateur
                    (id, identifiant, sel, empreinte_mot_de_passe, iterations)
                VALUES (1, ?, ?, ?, ?)
                """,
                (identifiant, sel, empreinte, self.ITERATIONS),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("Le compte administrateur est déjà configuré.") from exc
        self.db.valider()

    def verifier(self, identifiant: str, mot_de_passe: str) -> bool:
        """Vérifie les identifiants sans jamais conserver le mot de passe en clair."""
        cur = self.db.curseur()
        cur.execute(
            """
            SELECT sel, empreinte_mot_de_passe, iterations
            FROM administrateur
            WHERE id = 1 AND identifiant = ?
            """,
            (identifiant.strip().casefold(),),
        )
        compte = cur.fetchone()
        if compte is None:
            return False

        empreinte = hashlib.pbkdf2_hmac(
            "sha256",
            mot_de_passe.encode("utf-8"),
            compte["sel"],
            compte["iterations"],
        )
        return hmac.compare_digest(empreinte, compte["empreinte_mot_de_passe"])
