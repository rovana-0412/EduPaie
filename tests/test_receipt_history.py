"""Tests de consultation des reçus générés depuis l'historique."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication

from src.models import Eleve, Paiement, SoldeEleve
from src.ui.fiche_eleve import (
    FicheEleveDialog,
    _total_paye_jusquau_paiement,
)


class ReceiptHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.receipts_dir = Path(self.temp_dir.name)
        self.receipts_patch = patch("src.pdf_generator.RECUS_DIR", self.receipts_dir)
        self.receipts_patch.start()

        self.eleve = Eleve(
            id_eleve=1,
            nom="KOUASSI",
            prenom="Ami",
            date_naissance="2014-03-15",
            annee_scolaire="2026-2027",
            montant_total_du=150000,
            id_classe=1,
        )
        self.paiement = Paiement(
            id_paiement=1,
            date_paiement="2026-10-02",
            montant=50000,
            mode_paiement="Espèces",
            numero_recu="REC-2026-000001",
            id_eleve=1,
        )
        solde = SoldeEleve(self.eleve, 150000, 50000, 100000)
        self.dialog = FicheEleveDialog(self.eleve, solde, [self.paiement])

    def tearDown(self):
        self.dialog.close()
        self.receipts_patch.stop()
        self.temp_dir.cleanup()

    def test_open_receipt_button_is_enabled_when_pdf_exists(self):
        chemin = self.receipts_dir / f"{self.paiement.numero_recu}.pdf"
        chemin.write_bytes(b"%PDF-1.4")

        self.dialog.tableau.selectRow(0)
        self.app.processEvents()

        self.assertTrue(self.dialog.bouton_ouvrir_recu.isEnabled())

    def test_open_receipt_button_opens_existing_pdf(self):
        chemin = self.receipts_dir / f"{self.paiement.numero_recu}.pdf"
        chemin.write_bytes(b"%PDF-1.4")
        self.dialog.tableau.selectRow(0)
        self.app.processEvents()

        with patch(
            "src.ui.fiche_eleve.QDesktopServices.openUrl",
            return_value=True,
        ) as ouvrir:
            self.dialog._ouvrir_recu_genere()

        ouvrir.assert_called_once_with(QUrl.fromLocalFile(str(chemin)))

    def test_open_receipt_button_stays_disabled_when_pdf_is_missing(self):
        self.dialog.tableau.selectRow(0)
        self.app.processEvents()

        self.assertFalse(self.dialog.bouton_ouvrir_recu.isEnabled())

    def test_historical_total_orders_payments_on_the_same_day_by_id(self):
        paiement_ancien = Paiement(
            id_paiement=3,
            date_paiement="2026-10-02",
            montant=20000,
            mode_paiement="Espèces",
            numero_recu="REC-2026-000002",
            id_eleve=1,
        )
        paiement_courant = Paiement(
            id_paiement=4,
            date_paiement="2026-10-02",
            montant=30000,
            mode_paiement="Espèces",
            numero_recu="REC-2026-000003",
            id_eleve=1,
        )
        paiement_posterieur = Paiement(
            id_paiement=5,
            date_paiement="2026-10-02",
            montant=40000,
            mode_paiement="Espèces",
            numero_recu="REC-2026-000004",
            id_eleve=1,
        )

        total = _total_paye_jusquau_paiement(
            [paiement_posterieur, paiement_courant, paiement_ancien],
            paiement_courant,
        )

        self.assertEqual(total, 50000)


if __name__ == "__main__":
    unittest.main()
