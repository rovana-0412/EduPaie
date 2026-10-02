"""Dialogue de création d'une classe personnalisée."""
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from src.constants import ANNEE_SCOLAIRE_DEFAUT


class ClasseDialog(QDialog):
    """Saisit le libellé, le niveau et l'année d'une nouvelle classe."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter une classe")
        self.setMinimumWidth(460)
        self._construire_interface()

    def _construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(14)

        titre = QLabel("Nouvelle classe")
        titre.setObjectName("titre_principal")
        layout.addWidget(titre)

        description = QLabel(
            "Ajoutez une classe personnalisée qui n'est pas dans la liste."
        )
        description.setObjectName("sous_titre")
        description.setWordWrap(True)
        layout.addWidget(description)

        form = QFormLayout()
        form.setVerticalSpacing(12)
        form.setHorizontalSpacing(14)

        self.champ_nom = QLineEdit()
        self.champ_nom.setPlaceholderText("Ex. : 1ère E")
        form.addRow("Nom de la classe * :", self.champ_nom)

        self.champ_niveau = QLineEdit()
        self.champ_niveau.setPlaceholderText("Ex. : 1ère")
        form.addRow("Niveau * :", self.champ_niveau)

        self.champ_annee = QLineEdit()
        self.champ_annee.setText(ANNEE_SCOLAIRE_DEFAUT)
        self.champ_annee.setPlaceholderText("Ex. : 2026-2027")
        form.addRow("Année scolaire * :", self.champ_annee)
        layout.addLayout(form)

        boutons = QHBoxLayout()
        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(self.reject)
        bouton_ajouter = QPushButton("Ajouter la classe")
        bouton_ajouter.setObjectName("btn_primaire")
        bouton_ajouter.setDefault(True)
        bouton_ajouter.clicked.connect(self._valider)
        boutons.addStretch()
        boutons.addWidget(bouton_annuler)
        boutons.addWidget(bouton_ajouter)
        layout.addLayout(boutons)

    def _valider(self):
        if not self.champ_nom.text().strip():
            QMessageBox.warning(
                self, "Nom manquant", "Le nom de la classe est obligatoire."
            )
            self.champ_nom.setFocus()
            return
        if not self.champ_niveau.text().strip():
            QMessageBox.warning(
                self, "Niveau manquant", "Le niveau scolaire est obligatoire."
            )
            self.champ_niveau.setFocus()
            return
        if not self.champ_annee.text().strip():
            QMessageBox.warning(
                self, "Année manquante", "L'année scolaire est obligatoire."
            )
            self.champ_annee.setFocus()
            return
        self.accept()

    def get_donnees_classe(self):
        return {
            "nom_classe": self.champ_nom.text().strip(),
            "niveau": self.champ_niveau.text().strip(),
            "annee_scolaire": self.champ_annee.text().strip(),
        }
