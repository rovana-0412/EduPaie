"""Tests du compte administrateur et de l'écran de connexion."""
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialog, QLineEdit

from src.auth import AuthService
from src.backup import BackupService
from src.repository import Database
from src.ui.login_dialog import LoginDialog


class AuthServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temp_dir.name) / "test.db")
        self.db.connecter()
        self.auth = AuthService(self.db)
        self.auth.initialiser()
        self.backup = BackupService(self.db)
        self.backup.initialiser()

    def tearDown(self):
        self.db.deconnecter()
        self.temp_dir.cleanup()

    def test_first_run_creates_a_salted_password_hash(self):
        self.assertFalse(self.auth.compte_configure())

        self.auth.creer_compte("Gestionnaire", "motdepasse-solide")

        row = self.db.curseur().execute(
            "SELECT identifiant, sel, empreinte_mot_de_passe "
            "FROM administrateur WHERE id = 1"
        ).fetchone()
        self.assertEqual(row["identifiant"], "gestionnaire")
        self.assertEqual(len(row["sel"]), 16)
        self.assertNotEqual(row["empreinte_mot_de_passe"], b"motdepasse-solide")
        self.assertTrue(self.auth.verifier("GESTIONNAIRE", "motdepasse-solide"))
        self.assertFalse(self.auth.verifier("gestionnaire", "incorrect"))

    def test_rejects_weak_password_and_second_account(self):
        with self.assertRaises(ValueError):
            self.auth.creer_compte("admin", "court")
        self.assertFalse(self.auth.compte_configure())

        self.auth.creer_compte("admin", "motdepasse-solide")
        with self.assertRaises(ValueError):
            self.auth.creer_compte("autre", "autre-mot-de-passe")

    def test_password_reset_preserves_admin_identifier_and_school_data(self):
        self.auth.creer_compte("Gestionnaire", "motdepasse-solide")
        self.backup.configurer_mot_de_passe("sauvegarde-secrete-2026")
        self.db.connexion.executescript(
            """
            CREATE TABLE classes (id_classe INTEGER PRIMARY KEY, nom TEXT);
            CREATE TABLE eleves (id_eleve INTEGER PRIMARY KEY, nom TEXT);
            CREATE TABLE paiements (id_paiement INTEGER PRIMARY KEY, montant INTEGER);
            INSERT INTO classes VALUES (1, '6eme A');
            INSERT INTO eleves VALUES (1, 'Kouassi');
            INSERT INTO paiements VALUES (1, 50000);
            """
        )
        self.db.valider()

        self.auth.reinitialiser_mot_de_passe("nouveau-mot-de-passe")

        self.assertFalse(self.auth.verifier("gestionnaire", "motdepasse-solide"))
        self.assertTrue(self.auth.verifier("GESTIONNAIRE", "nouveau-mot-de-passe"))
        self.assertEqual(
            self.db.curseur().execute(
                "SELECT identifiant FROM administrateur WHERE id = 1"
            ).fetchone()["identifiant"],
            "gestionnaire",
        )
        self.assertEqual(
            self.db.curseur().execute(
                "SELECT montant FROM paiements WHERE id_paiement = 1"
            ).fetchone()[0],
            50000,
        )
        self.assertTrue(
            self.backup.verifier_mot_de_passe("sauvegarde-secrete-2026")
        )

    def test_password_reset_requires_a_configured_account_and_strong_password(self):
        with self.assertRaisesRegex(ValueError, "au moins 10"):
            self.auth.reinitialiser_mot_de_passe("tropcourt")
        with self.assertRaisesRegex(ValueError, "Aucun compte"):
            self.auth.reinitialiser_mot_de_passe("motdepasse-nouveau")

    def test_login_dialog_accepts_only_valid_credentials(self):
        self.auth.creer_compte("admin", "motdepasse-solide")
        self.backup.configurer_mot_de_passe("sauvegarde-secrete-2026")
        dialog = LoginDialog(self.auth, self.backup)

        dialog.champ_identifiant.setText("admin")
        dialog.champ_mot_de_passe.setText("incorrect")
        dialog._soumettre()
        self.assertNotEqual(dialog.result(), QDialog.DialogCode.Accepted)
        self.assertIn("Identifiant ou mot de passe incorrect.", dialog.message.text())
        self.assertEqual(dialog.champ_mot_de_passe.text(), "incorrect")

        dialog.champ_mot_de_passe.setText("motdepasse-solide")
        dialog.champ_mot_de_passe_sauvegarde.setText("sauvegarde-secrete-2026")
        dialog._soumettre()
        self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)
        self.assertEqual(
            dialog.mot_de_passe_sauvegarde,
            "sauvegarde-secrete-2026",
        )

    def test_empty_login_fields_show_specific_prompts(self):
        self.auth.creer_compte("admin", "motdepasse-solide")
        self.backup.configurer_mot_de_passe("sauvegarde-secrete-2026")
        dialog = LoginDialog(self.auth, self.backup)

        dialog._soumettre()
        self.assertEqual(dialog.message.text(), "Saisissez votre identifiant.")

        dialog.champ_identifiant.setText("admin")
        dialog._soumettre()
        self.assertEqual(
            dialog.message.text(),
            "Saisissez votre mot de passe de connexion.",
        )

    def test_first_run_dialog_requires_matching_passwords(self):
        dialog = LoginDialog(self.auth, self.backup)
        dialog.champ_identifiant.setText("admin")
        dialog.champ_mot_de_passe.setText("motdepasse-solide")
        dialog.champ_confirmation.setText("autre-mot-de-passe")
        dialog._soumettre()

        self.assertFalse(self.auth.compte_configure())
        self.assertEqual(
            dialog.message.text(),
            "Les mots de passe ne correspondent pas.",
        )

    def test_first_run_also_configures_a_distinct_backup_password(self):
        dialog = LoginDialog(self.auth, self.backup)
        dialog.champ_identifiant.setText("admin")
        dialog.champ_mot_de_passe.setText("motdepasse-solide")
        dialog.champ_confirmation.setText("motdepasse-solide")
        dialog.champ_mot_de_passe_sauvegarde.setText("sauvegarde-secrete-2026")
        dialog.champ_confirmation_sauvegarde.setText("sauvegarde-secrete-2026")

        dialog._soumettre()

        self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)
        self.assertTrue(self.backup.verifier_mot_de_passe("sauvegarde-secrete-2026"))

    def test_invalid_backup_password_does_not_create_account_and_allows_retry(self):
        dialog = LoginDialog(self.auth, self.backup)
        dialog.champ_identifiant.setText("admin")
        dialog.champ_mot_de_passe.setText("motdepasse-solide")
        dialog.champ_confirmation.setText("motdepasse-solide")
        dialog.champ_mot_de_passe_sauvegarde.setText("sauvegarde-secrete-2026")
        dialog.champ_confirmation_sauvegarde.setText("motdepasse-different")

        dialog._soumettre()

        self.assertFalse(self.auth.compte_configure())
        self.assertFalse(self.backup.mot_de_passe_configure())
        self.assertEqual(
            dialog.message.text(),
            "Les mots de passe de sauvegarde ne correspondent pas.",
        )

        dialog.champ_confirmation_sauvegarde.setText("sauvegarde-secrete-2026")
        dialog._soumettre()

        self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)
        self.assertTrue(self.auth.compte_configure())
        self.assertTrue(self.backup.mot_de_passe_configure())

    def test_login_refuses_the_wrong_backup_password(self):
        self.auth.creer_compte("admin", "motdepasse-solide")
        self.backup.configurer_mot_de_passe("sauvegarde-secrete-2026")
        dialog = LoginDialog(self.auth, self.backup)
        dialog.champ_identifiant.setText("admin")
        dialog.champ_mot_de_passe.setText("motdepasse-solide")
        dialog.champ_mot_de_passe_sauvegarde.setText("autre-sauvegarde")

        dialog._soumettre()

        self.assertNotEqual(dialog.result(), QDialog.DialogCode.Accepted)
        self.assertEqual(
            dialog.message.text(),
            "Le mot de passe de sauvegarde est incorrect.",
        )

    def test_password_visibility_buttons_toggle_each_field(self):
        dialog = LoginDialog(self.auth, self.backup)
        champs = (
            (dialog.champ_mot_de_passe, dialog.bouton_voir_mot_de_passe),
            (
                dialog.champ_confirmation,
                dialog.bouton_voir_confirmation,
            ),
            (
                dialog.champ_mot_de_passe_sauvegarde,
                dialog.bouton_voir_mot_de_passe_sauvegarde,
            ),
            (
                dialog.champ_confirmation_sauvegarde,
                dialog.bouton_voir_confirmation_sauvegarde,
            ),
        )

        for champ, bouton in champs:
            with self.subTest(champ=champ):
                self.assertEqual(champ.echoMode(), QLineEdit.EchoMode.Password)
                self.assertEqual(bouton.text(), "")
                icone_masquee = bouton.icon().cacheKey()
                bouton.click()
                self.assertEqual(champ.echoMode(), QLineEdit.EchoMode.Normal)
                self.assertNotEqual(bouton.icon().cacheKey(), icone_masquee)
                bouton.click()
                self.assertEqual(champ.echoMode(), QLineEdit.EchoMode.Password)

    def test_existing_account_can_configure_backup_password_on_first_login(self):
        self.auth.creer_compte("admin", "motdepasse-solide")
        dialog = LoginDialog(self.auth, self.backup)
        dialog.champ_identifiant.setText("admin")
        dialog.champ_mot_de_passe.setText("motdepasse-solide")
        dialog.champ_mot_de_passe_sauvegarde.setText("sauvegarde-secrete-2026")
        dialog.champ_confirmation_sauvegarde.setText("sauvegarde-secrete-2026")

        dialog._soumettre()

        self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)
        self.assertTrue(self.backup.mot_de_passe_configure())


if __name__ == "__main__":
    unittest.main()
