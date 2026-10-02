"""Tests des sauvegardes chiffrées, isolés dans des bases temporaires."""
import os
import tempfile
import unittest
from pathlib import Path

from src.backup import BackupError, BackupService
from src.repository import Database


class BackupServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.db_path = self.root / "edupaie.db"
        self.db = Database(self.db_path)
        self.db.connecter()
        self.db.connexion.executescript(
            """
            CREATE TABLE classes (id_classe INTEGER PRIMARY KEY);
            CREATE TABLE eleves (
                id_eleve INTEGER PRIMARY KEY,
                id_classe INTEGER REFERENCES classes(id_classe)
            );
            CREATE TABLE paiements (
                id_paiement INTEGER PRIMARY KEY,
                id_eleve INTEGER REFERENCES eleves(id_eleve)
            );
            INSERT INTO classes VALUES (1);
            INSERT INTO eleves VALUES (1, 1);
            INSERT INTO paiements VALUES (1, 1);
            """
        )
        self.db.valider()
        self.service = BackupService(self.db, self.root / "backups")
        self.service.initialiser()
        self.password = "sauvegarde-privee-2026"
        self.service.configurer_mot_de_passe(self.password)

    def tearDown(self):
        self.db.deconnecter()
        self.temp_dir.cleanup()

    def test_password_verification_and_encrypted_backup(self):
        self.assertTrue(self.service.verifier_mot_de_passe(self.password))
        self.assertFalse(self.service.verifier_mot_de_passe("mauvais-mot-de-passe"))

        backup = self.service.creer_sauvegarde_chiffree(
            self.db_path, self.password
        )

        self.assertTrue(backup.is_file())
        self.assertTrue(backup.read_bytes().startswith(self.service.MAGIC))
        self.assertNotIn(b"CREATE TABLE classes", backup.read_bytes())

    def test_rejects_weak_backup_password(self):
        with self.assertRaises(ValueError):
            self.service.configurer_mot_de_passe("court")

    def test_wrong_password_and_tampering_are_rejected(self):
        backup = self.service.creer_sauvegarde_chiffree(
            self.db_path, self.password
        )
        with self.assertRaises(BackupError):
            self.service.restaurer_sauvegarde_chiffree(
                backup, self.db_path, "mauvais-mot-de-passe"
            )

        contenu = bytearray(backup.read_bytes())
        contenu[-1] ^= 1
        backup.write_bytes(contenu)
        with self.assertRaises(BackupError):
            self.service.restaurer_sauvegarde_chiffree(
                backup, self.db_path, self.password
            )

    def test_restore_replaces_database_and_keeps_encrypted_safety_copy(self):
        backup = self.service.creer_sauvegarde_chiffree(
            self.db_path, self.password
        )
        self.db.connexion.execute("INSERT INTO classes VALUES (2)")
        self.db.valider()

        safety_backup = self.service.restaurer_sauvegarde_chiffree(
            backup, self.db_path, self.password
        )

        self.assertIsNotNone(safety_backup)
        self.assertTrue(safety_backup.is_file())
        self.assertEqual(
            self.db.connexion.execute("SELECT COUNT(*) FROM classes").fetchone()[0],
            1,
        )


if __name__ == "__main__":
    unittest.main()
