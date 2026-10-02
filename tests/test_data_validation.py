"""Tests des validations de dates et de la numérotation des reçus."""
import tempfile
import unittest
import sqlite3
from contextlib import closing
from pathlib import Path
import shutil
import subprocess
import sys

from init_db import initialiser_base
from src.constants import ANNEE_SCOLAIRE_DEFAUT, CLASSES_ETABLISSEMENT
from src.date_utils import valider_date_iso
from src.models import Eleve
from src.repository import (
    ClasseRepository,
    Database,
    EleveRepository,
    PaiementRepository,
)
from src.service import EleveService, PaiementService


class DateValidationTests(unittest.TestCase):
    def test_accepts_real_iso_date_and_rejects_invalid_calendar_dates(self):
        self.assertEqual(
            valider_date_iso("2024-02-29").isoformat(),
            "2024-02-29",
        )
        for valeur in ("2026-99-99", "2026-02-29", "20260315", "2014-3-15"):
            with self.subTest(valeur=valeur):
                with self.assertRaises(ValueError):
                    valider_date_iso(valeur)


class ServiceValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        initialiser_base(self.db_path)
        self.db = Database(self.db_path)
        self.db.connecter()
        self.db.connexion.execute(
            "INSERT INTO classes (nom_classe, niveau, annee_scolaire) "
            "VALUES ('6ème A', '6ème', '2026-2027')"
        )
        self.db.connexion.execute(
            """
            INSERT INTO eleves
                (nom, prenom, date_naissance, annee_scolaire, montant_total_du, id_classe)
            VALUES ('KOUASSI', 'Ami', '2014-03-15', '2026-2027', 1000, 1)
            """
        )
        self.db.valider()
        self.eleve_repo = EleveRepository(self.db)
        self.paiement_repo = PaiementRepository(self.db)
        self.service = PaiementService(self.eleve_repo, self.paiement_repo)

    def tearDown(self):
        self.db.deconnecter()
        self.temp_dir.cleanup()

    def test_student_service_rejects_impossible_date(self):
        eleve = Eleve(
            id_eleve=None,
            nom="KOUASSI",
            prenom="Ami",
            date_naissance="2026-99-99",
            annee_scolaire="2026-2027",
            montant_total_du=1000,
            id_classe=1,
        )
        with self.assertRaisesRegex(ValueError, "date valide"):
            EleveService(self.eleve_repo).ajouter(eleve)

    def test_payment_service_rejects_impossible_date(self):
        with self.assertRaisesRegex(ValueError, "date valide"):
            self.service.enregistrer_paiement(
                1, 100, "Espèces", "2026-99-99"
            )
        self.assertEqual(self.paiement_repo.somme_par_eleve(1), 0)

    def test_receipt_number_uses_maximum_existing_value_after_a_gap(self):
        self.db.connexion.executemany(
            """
            INSERT INTO paiements
                (date_paiement, montant, mode_paiement, numero_recu, id_eleve)
            VALUES ('2026-09-01', 1, 'Espèces', ?, 1)
            """,
            [("REC-2026-000001",), ("REC-2026-000003",)],
        )
        self.db.valider()

        paiement = self.service.enregistrer_paiement(
            1, 100, "Espèces", "2026-09-02"
        )

        self.assertEqual(paiement.numero_recu, "REC-2026-000004")

    def test_adding_standard_classes_is_idempotent_and_preserves_records(self):
        repository = ClasseRepository(self.db)
        repository.ajouter_classes_etablissement()
        repository.ajouter_classes_etablissement()

        rows = self.db.curseur().execute(
            "SELECT nom_classe, annee_scolaire FROM classes ORDER BY id_classe"
        ).fetchall()
        names = [row["nom_classe"] for row in rows]
        self.assertEqual(tuple(names), CLASSES_ETABLISSEMENT)
        self.assertTrue(
            all(row["annee_scolaire"] == ANNEE_SCOLAIRE_DEFAUT for row in rows)
        )
        self.assertEqual(
            self.db.curseur().execute(
                "SELECT COUNT(*) FROM eleves"
            ).fetchone()[0],
            1,
        )
        self.assertEqual(
            self.db.curseur().execute(
                "SELECT COUNT(*) FROM classes"
            ).fetchone()[0],
            len(CLASSES_ETABLISSEMENT),
        )

    def test_custom_class_can_be_added_and_duplicate_is_rejected(self):
        repository = ClasseRepository(self.db)

        id_classe = repository.ajouter(
            "1ère E", "1ère", "2026-2027"
        )
        classe = repository.trouver_par_id(id_classe)

        self.assertEqual(classe.nom_classe, "1ère E")
        self.assertEqual(classe.niveau, "1ère")
        self.assertEqual(classe.annee_scolaire, "2026-2027")
        with self.assertRaisesRegex(ValueError, "existe déjà"):
            repository.ajouter("1ère E", "1ère", "2026-2027")

        id_autre_annee = repository.ajouter(
            "1ère E", "1ère", "2027-2028"
        )
        self.assertNotEqual(id_classe, id_autre_annee)


class InitDatabaseSafetyTests(unittest.TestCase):
    def test_initializer_refuses_existing_database_without_changing_it(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "edupaie.db"
            initialiser_base(chemin)

            with closing(sqlite3.connect(chemin)) as connexion:
                connexion.execute(
                    "INSERT INTO classes (nom_classe, niveau, annee_scolaire) "
                    "VALUES ('Test', 'Test', '2026-2027')"
                )
                connexion.commit()

            with self.assertRaises(FileExistsError):
                initialiser_base(chemin)

            with closing(sqlite3.connect(chemin)) as connexion:
                nombre = connexion.execute("SELECT COUNT(*) FROM classes").fetchone()[0]
            self.assertEqual(nombre, 1)

    def test_demo_seed_refuses_to_clear_an_existing_database(self):
        racine_projet = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as dossier:
            racine_temp = Path(dossier)
            for nom in ("init_db.py", "seed_db.py", "schema.sql"):
                shutil.copyfile(racine_projet / nom, racine_temp / nom)
            repertoire_src = racine_temp / "src"
            repertoire_src.mkdir()
            (repertoire_src / "__init__.py").write_text("", encoding="utf-8")
            shutil.copyfile(
                racine_projet / "src" / "constants.py",
                repertoire_src / "constants.py",
            )

            initialisation = subprocess.run(
                [sys.executable, "init_db.py"],
                cwd=racine_temp,
                capture_output=True,
                text=True,
            )
            self.assertEqual(initialisation.returncode, 0, initialisation.stderr)
            insertion = subprocess.run(
                [sys.executable, "seed_db.py"],
                cwd=racine_temp,
                capture_output=True,
                text=True,
            )
            self.assertEqual(insertion.returncode, 0, insertion.stderr)

            refus = subprocess.run(
                [sys.executable, "seed_db.py"],
                cwd=racine_temp,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(refus.returncode, 0)
            self.assertIn("aucune donnée n'a été modifiée", refus.stderr)

            with closing(
                sqlite3.connect(racine_temp / "data" / "edupaie.db")
            ) as connexion:
                compte = connexion.execute(
                    "SELECT (SELECT COUNT(*) FROM classes), "
                    "(SELECT COUNT(*) FROM eleves), "
                    "(SELECT COUNT(*) FROM paiements)"
                ).fetchone()
            self.assertEqual(compte, (16, 15, 12))


if __name__ == "__main__":
    unittest.main()
