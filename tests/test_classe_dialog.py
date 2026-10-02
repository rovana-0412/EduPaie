"""Tests du dialogue d'ajout de classes personnalisées."""
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialog

from src.ui.classe_dialog import ClasseDialog


class ClasseDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_valid_class_values_are_returned_without_extra_whitespace(self):
        dialog = ClasseDialog()
        dialog.champ_nom.setText("  1ère E  ")
        dialog.champ_niveau.setText("  1ère ")
        dialog.champ_annee.setText("  2026-2027 ")

        dialog._valider()

        self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)
        self.assertEqual(
            dialog.get_donnees_classe(),
            {
                "nom_classe": "1ère E",
                "niveau": "1ère",
                "annee_scolaire": "2026-2027",
            },
        )


if __name__ == "__main__":
    unittest.main()
