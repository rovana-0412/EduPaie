"""Sauvegardes SQLite chiffrées et restauration vérifiée."""
import base64
import hashlib
import hmac
import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from contextlib import closing

from cryptography.fernet import Fernet, InvalidToken

from src.repository import Database


class BackupError(Exception):
    """Erreur explicite lors d'une sauvegarde ou d'une restauration."""


class BackupService:
    ITERATIONS = 600_000
    LONGUEUR_MIN_MOT_DE_PASSE = 12
    MAGIC = b"EDUPAIE-BACKUP\x01"
    LONGUEUR_SEL = 16
    NOMBRE_SAUVEGARDES_MAX = 30

    def __init__(self, db: Database, dossier_sauvegardes: Optional[Path] = None):
        self.db = db
        self.dossier_sauvegardes = (
            Path(dossier_sauvegardes)
            if dossier_sauvegardes is not None
            else Path(db.db_path).parent / "backups"
        )

    def initialiser(self):
        """Crée le stockage de vérification du mot de passe dédié."""
        self.db.curseur().execute(
            """
            CREATE TABLE IF NOT EXISTS mot_de_passe_sauvegarde (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                sel BLOB NOT NULL,
                empreinte BLOB NOT NULL,
                iterations INTEGER NOT NULL
            )
            """
        )
        self.db.valider()

    def mot_de_passe_configure(self) -> bool:
        cur = self.db.curseur()
        cur.execute("SELECT 1 FROM mot_de_passe_sauvegarde WHERE id = 1")
        return cur.fetchone() is not None

    def configurer_mot_de_passe(self, mot_de_passe: str):
        if len(mot_de_passe) < self.LONGUEUR_MIN_MOT_DE_PASSE:
            raise ValueError(
                "Le mot de passe de sauvegarde doit contenir au moins "
                f"{self.LONGUEUR_MIN_MOT_DE_PASSE} caractères."
            )
        if self.mot_de_passe_configure():
            raise ValueError("Le mot de passe de sauvegarde est déjà configuré.")

        sel = os.urandom(self.LONGUEUR_SEL)
        empreinte = self._derive(mot_de_passe, sel, self.ITERATIONS)
        self.db.curseur().execute(
            """
            INSERT INTO mot_de_passe_sauvegarde (id, sel, empreinte, iterations)
            VALUES (1, ?, ?, ?)
            """,
            (sel, empreinte, self.ITERATIONS),
        )
        self.db.valider()

    def verifier_mot_de_passe(self, mot_de_passe: str) -> bool:
        cur = self.db.curseur()
        cur.execute(
            """
            SELECT sel, empreinte, iterations
            FROM mot_de_passe_sauvegarde WHERE id = 1
            """
        )
        row = cur.fetchone()
        if row is None:
            return False
        empreinte = self._derive(mot_de_passe, row["sel"], row["iterations"])
        return hmac.compare_digest(empreinte, row["empreinte"])

    @staticmethod
    def _derive(mot_de_passe: str, sel: bytes, iterations: int) -> bytes:
        return hashlib.pbkdf2_hmac(
            "sha256", mot_de_passe.encode("utf-8"), sel, iterations, dklen=32
        )

    @classmethod
    def _chiffrement(cls, mot_de_passe: str, sel: bytes) -> Fernet:
        cle = cls._derive(mot_de_passe, sel, cls.ITERATIONS)
        return Fernet(base64.urlsafe_b64encode(cle))

    def creer_sauvegarde_chiffree(
        self, chemin_base: Path, mot_de_passe: str
    ) -> Path:
        """Crée une copie SQLite cohérente et la chiffre avant de l'écrire."""
        return self._creer_sauvegarde_chiffree(
            chemin_base, mot_de_passe, verifier_mot_de_passe=True
        )

    def _creer_sauvegarde_chiffree(
        self,
        chemin_base: Path,
        mot_de_passe: str,
        verifier_mot_de_passe: bool,
    ) -> Path:
        chemin_base = Path(chemin_base)
        if not chemin_base.is_file():
            raise BackupError(f"Base de données introuvable : {chemin_base}")
        if verifier_mot_de_passe and not self.verifier_mot_de_passe(mot_de_passe):
            raise BackupError("Le mot de passe de sauvegarde est incorrect.")

        self.dossier_sauvegardes.mkdir(parents=True, exist_ok=True)
        fichier_temporaire_db = None
        fichier_temporaire_chiffre = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=self.dossier_sauvegardes, suffix=".sqlite", delete=False
            ) as temp_db:
                fichier_temporaire_db = Path(temp_db.name)

            with closing(sqlite3.connect(chemin_base)) as source, closing(
                sqlite3.connect(fichier_temporaire_db)
            ) as destination:
                source.backup(destination)

            donnees_db = fichier_temporaire_db.read_bytes()
            sel = os.urandom(self.LONGUEUR_SEL)
            contenu_chiffre = self.MAGIC + sel + self._chiffrement(
                mot_de_passe, sel
            ).encrypt(donnees_db)

            horodatage = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            sortie = self.dossier_sauvegardes / f"edupaie-{horodatage}.enc"
            with tempfile.NamedTemporaryFile(
                dir=self.dossier_sauvegardes,
                prefix=".edupaie-",
                suffix=".tmp",
                delete=False,
            ) as temp_chiffre:
                fichier_temporaire_chiffre = Path(temp_chiffre.name)
                temp_chiffre.write(contenu_chiffre)
                temp_chiffre.flush()
                os.fsync(temp_chiffre.fileno())
            os.replace(fichier_temporaire_chiffre, sortie)
            fichier_temporaire_chiffre = None
            self._purger_anciennes_sauvegardes()
            return sortie
        except (OSError, sqlite3.Error) as exc:
            raise BackupError(f"Échec de la sauvegarde chiffrée : {exc}") from exc
        finally:
            if fichier_temporaire_db is not None:
                fichier_temporaire_db.unlink(missing_ok=True)
            if fichier_temporaire_chiffre is not None:
                fichier_temporaire_chiffre.unlink(missing_ok=True)

    def _purger_anciennes_sauvegardes(self):
        sauvegardes = sorted(
            self.dossier_sauvegardes.glob("edupaie-*.enc"),
            key=lambda chemin: chemin.stat().st_mtime,
            reverse=True,
        )
        for ancienne in sauvegardes[self.NOMBRE_SAUVEGARDES_MAX:]:
            ancienne.unlink()

    def restaurer_sauvegarde_chiffree(
        self, chemin_sauvegarde: Path, chemin_base: Path, mot_de_passe: str
    ) -> Optional[Path]:
        """Vérifie puis restaure une base; protège d'abord l'actuelle par chiffrement."""
        chemin_sauvegarde = Path(chemin_sauvegarde)
        chemin_base = Path(chemin_base)
        try:
            contenu = chemin_sauvegarde.read_bytes()
        except OSError as exc:
            raise BackupError(f"Impossible de lire la sauvegarde : {exc}") from exc

        longueur_entete = len(self.MAGIC) + self.LONGUEUR_SEL
        if len(contenu) <= longueur_entete or not contenu.startswith(self.MAGIC):
            raise BackupError("Le fichier n'est pas une sauvegarde EduPaie valide.")
        sel = contenu[len(self.MAGIC):longueur_entete]
        try:
            donnees_db = self._chiffrement(mot_de_passe, sel).decrypt(
                contenu[longueur_entete:]
            )
        except InvalidToken as exc:
            raise BackupError(
                "Mot de passe incorrect ou sauvegarde altérée."
            ) from exc

        chemin_base.parent.mkdir(parents=True, exist_ok=True)
        fichier_temporaire = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=chemin_base.parent, suffix=".restore", delete=False
            ) as temp:
                fichier_temporaire = Path(temp.name)
                temp.write(donnees_db)
                temp.flush()
                os.fsync(temp.fileno())
            self._verifier_base_restauree(fichier_temporaire)

            sauvegarde_securite = None
            if chemin_base.is_file():
                sauvegarde_securite = self._creer_sauvegarde_chiffree(
                    chemin_base,
                    mot_de_passe,
                    verifier_mot_de_passe=False,
                )
            connexion_ouverte = self.db.connexion is not None
            if connexion_ouverte:
                self.db.deconnecter()
            try:
                os.replace(fichier_temporaire, chemin_base)
                fichier_temporaire = None
            finally:
                if connexion_ouverte:
                    self.db.connecter()
            return sauvegarde_securite
        except (OSError, sqlite3.Error) as exc:
            raise BackupError(f"Échec de la restauration : {exc}") from exc
        finally:
            if fichier_temporaire is not None:
                fichier_temporaire.unlink(missing_ok=True)

    @staticmethod
    def _verifier_base_restauree(chemin: Path):
        with closing(sqlite3.connect(chemin)) as connexion:
            resultat = connexion.execute("PRAGMA integrity_check").fetchone()[0]
            if resultat != "ok":
                raise BackupError("La sauvegarde restaurée est corrompue.")
            tables = {
                row[0]
                for row in connexion.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            if not {"classes", "eleves", "paiements"}.issubset(tables):
                raise BackupError("La sauvegarde ne contient pas les tables EduPaie.")
            violations = connexion.execute("PRAGMA foreign_key_check").fetchall()
            if violations:
                raise BackupError("La sauvegarde contient des références invalides.")
