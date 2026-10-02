"""Tests du tableau de bord, de ses filtres et de ses rapports."""
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QApplication, QLabel, QStyleOptionViewItem

from src.models import Classe, Eleve, SoldeEleve
from src.ui.statut_delegate import StatutDelegate
from src.ui.style import STYLE_GLOBAL
from src.ui.tableau_bord import TableauBordDialog


class FauxClasseRepository:
    def lister_toutes(self):
        return [
            Classe(1, "6ème A", "6ème", "2026-2027"),
            Classe(2, "5ème B", "5ème", "2026-2027"),
        ]


class FauxEleveService:
    def __init__(self, eleves):
        self.eleves = eleves

    def lister_tous(self):
        return list(self.eleves)


class FauxPaiementService:
    def __init__(self, soldes):
        self.soldes = soldes

    def calculer_solde(self, id_eleve):
        return self.soldes[id_eleve]


class TableauBordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.eleves = [
            Eleve(1, "KOUASSI", "Ami", "2014-03-15", "2026-2027", 100000, 1),
            Eleve(2, "MENSAH", "Kofi", "2014-07-22", "2026-2027", 80000, 2),
            Eleve(3, "AGBEKO", "Sena", "2014-11-08", "2027-2028", 120000, 1),
        ]
        self.soldes = {
            1: SoldeEleve(self.eleves[0], 100000, 40000, 60000),
            2: SoldeEleve(self.eleves[1], 80000, 80000, 0),
            3: SoldeEleve(self.eleves[2], 120000, 0, 120000),
        }
        self.eleve_service = FauxEleveService(self.eleves)
        self.paiement_service = FauxPaiementService(self.soldes)
        self.dialog = TableauBordDialog(
            self.eleve_service,
            self.paiement_service,
            classe_repo=FauxClasseRepository(),
        )

    def tearDown(self):
        self.dialog.close()

    @staticmethod
    def _valeur_carte(carte):
        return carte.findChild(QLabel, "carte_valeur").text()

    def test_class_and_school_year_filters_update_table_and_summary(self):
        self.dialog.filtre_classe.setCurrentIndex(
            self.dialog.filtre_classe.findData(1)
        )
        self.dialog.filtre_annee.setCurrentIndex(
            self.dialog.filtre_annee.findData("2026-2027")
        )

        self.assertEqual(self.dialog.tableau.rowCount(), 1)
        self.assertEqual(self.dialog.tableau.item(0, 0).text(), "KOUASSI")
        self.assertEqual(self._valeur_carte(self.dialog.carte_eleves), "1")
        self.assertEqual(self._valeur_carte(self.dialog.carte_encaisse), "40,000 F CFA")
        self.assertEqual(self.dialog.tableau.item(0, 2).text(), "6ème A")

    def test_cards_filter_students_by_relevant_payment_situation(self):
        self.dialog.carte_encaisse.click()
        self.assertEqual(self.dialog.filtre_situation.currentData(), "avec_paiement")
        self.assertEqual(self.dialog.tableau.rowCount(), 2)

        self.dialog.carte_non_soldes.click()
        self.assertEqual(self.dialog.filtre_situation.currentData(), "reste_du")
        self.assertEqual(self.dialog.tableau.rowCount(), 2)

        self.dialog.carte_eleves.click()
        self.assertEqual(self.dialog.filtre_situation.currentData(), "tous")
        self.assertEqual(self.dialog.tableau.rowCount(), 3)

    def test_stat_cards_keep_a_large_fixed_height_and_expand_horizontally(self):
        ancienne_feuille_style = self.app.styleSheet()
        self.app.setStyleSheet(STYLE_GLOBAL)
        self.dialog.show()
        self.app.processEvents()
        for carte in (
            self.dialog.carte_eleves,
            self.dialog.carte_encaisse,
            self.dialog.carte_restant,
            self.dialog.carte_non_soldes,
        ):
            with self.subTest(carte=carte.accessibleName()):
                self.assertGreaterEqual(carte.height(), 130)
                self.assertGreaterEqual(
                    carte.findChild(QLabel, "carte_valeur").height(), 28
                )
        self.app.setStyleSheet(ancienne_feuille_style)

    def test_status_column_allocates_enough_width_for_long_badge(self):
        self.dialog._actualiser_affichage()
        ligne_partiellement_payee = next(
            ligne
            for ligne in range(self.dialog.tableau.rowCount())
            if self.dialog.tableau.item(ligne, 7).text()
            == "Partiellement payé"
        )
        index = self.dialog.tableau.model().index(
            ligne_partiellement_payee, 7
        )
        option = QStyleOptionViewItem()
        option.font = self.dialog.tableau.font()
        option.fontMetrics = QFontMetrics(option.font)
        delegate = StatutDelegate(self.dialog.tableau)

        self.assertGreaterEqual(
            delegate.sizeHint(option, index).width(),
            option.fontMetrics.horizontalAdvance("Partiellement payé") + 36,
        )

    def test_refresh_reloads_source_records_and_recomputes_statistics(self):
        nouvel_eleve = Eleve(
            4, "DOSSEH", "Abla", "2014-09-12", "2027-2028", 90000, 2
        )
        self.eleve_service.eleves.append(nouvel_eleve)
        self.soldes[4] = SoldeEleve(nouvel_eleve, 90000, 0, 90000)

        self.dialog.bouton_actualiser.click()

        self.assertEqual(self.dialog.tableau.rowCount(), 4)
        self.assertEqual(self._valeur_carte(self.dialog.carte_eleves), "4")
        self.assertEqual(
            self._valeur_carte(self.dialog.carte_restant),
            "270,000 F CFA",
        )

    def test_report_includes_filters_and_only_visible_students(self):
        self.dialog.carte_encaisse.click()
        html = self.dialog._construire_rapport_html()

        self.assertIn("Rapport du tableau de bord", html)
        self.assertIn("Situation : Avec paiement", html)
        self.assertIn("Reste à recouvrer : 180,000 F CFA", html)
        self.assertIn("KOUASSI", html)
        self.assertIn("MENSAH", html)
        self.assertNotIn("AGBEKO", html)

    def test_pdf_export_writes_a_pdf_to_the_requested_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            chemin = Path(temp_dir) / "rapport.pdf"

            self.dialog._ecrire_pdf(chemin)

            self.assertTrue(chemin.is_file())
            self.assertGreater(chemin.stat().st_size, 100)
            self.assertTrue(chemin.read_bytes().startswith(b"%PDF-"))


if __name__ == "__main__":
    unittest.main()
