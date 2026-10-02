"""
EduPaie — Dialogue d'enregistrement d'un paiement.
Permet de saisir un paiement pour un élève donné, avec validation du solde.
"""
from datetime import date

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QDoubleSpinBox,
    QPushButton,
    QMessageBox,
    QLabel,
    QFrame,
)

from src.date_utils import valider_date_iso
from src.models import Eleve, Paiement


class PaiementDialog(QDialog):
    """Boîte de dialogue pour enregistrer un paiement."""

    def __init__(self, eleve: Eleve, solde_actuel: float, parent=None):
        """
        Args:
            eleve         : l'élève concerné par le paiement
            solde_actuel  : solde restant dû (calculé par le service)
            parent        : widget parent
        """
        super().__init__(parent)
        self.eleve = eleve
        self.solde_actuel = solde_actuel

        self.setWindowTitle(f"Enregistrer un paiement — {eleve.nom_complet}")
        self.setMinimumWidth(500)

        self._construire_interface()

    def _construire_interface(self):
        """Construit les champs du dialogue."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(16)

        # ===== En-tête : infos élève =====
        titre = QLabel(f"Paiement pour : {self.eleve.nom_complet}")
        titre.setObjectName("titre_principal")
        layout.addWidget(titre)

        # Infos solde
        cadre_solde = QFrame()
        cadre_solde.setObjectName("surface")
        cadre_solde.setFrameShape(QFrame.StyledPanel)
        layout_solde = QVBoxLayout(cadre_solde)
        layout_solde.setContentsMargins(16, 12, 16, 12)
        layout_solde.setSpacing(6)

        label_du = QLabel(f"Montant total dû : {self.eleve.montant_total_du:,.0f} F CFA")
        label_solde = QLabel(f"Solde restant : {self.solde_actuel:,.0f} F CFA")
        label_solde.setObjectName("titre_section")

        layout_solde.addWidget(label_du)
        layout_solde.addWidget(label_solde)
        layout.addWidget(cadre_solde)

        # ===== Formulaire =====
        form = QFormLayout()
        form.setVerticalSpacing(12)
        form.setHorizontalSpacing(16)

        # Montant
        self.champ_montant = QDoubleSpinBox()
        self.champ_montant.setRange(0, self.solde_actuel)
        self.champ_montant.setDecimals(0)
        self.champ_montant.setSingleStep(5000)
        self.champ_montant.setSuffix(" F CFA")
        self.champ_montant.setValue(min(50000, self.solde_actuel))
        form.addRow("Montant à payer * :", self.champ_montant)

        # Date
        self.champ_date = QLineEdit()
        self.champ_date.setText(date.today().isoformat())
        self.champ_date.setReadOnly(True)
        form.addRow("Date du paiement * :", self.champ_date)

        # Mode
        self.champ_mode = QComboBox()
        self.champ_mode.addItems(["Espèces", "Chèque", "Virement", "Mobile Money"])
        form.addRow("Mode de paiement * :", self.champ_mode)

        layout.addLayout(form)

        # ===== Boutons =====
        layout_boutons = QHBoxLayout()

        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(self.reject)

        bouton_valider = QPushButton("Enregistrer le paiement")
        bouton_valider.setObjectName("btn_succes")
        bouton_valider.setDefault(True)
        bouton_valider.clicked.connect(self._valider)

        layout_boutons.addStretch()
        layout_boutons.addWidget(bouton_annuler)
        layout_boutons.addWidget(bouton_valider)

        layout.addLayout(layout_boutons)

    def _valider(self):
        """Valide les champs avant de fermer."""
        montant = self.champ_montant.value()

        # Validations
        if montant <= 0:
            QMessageBox.warning(
                self, "Montant invalide",
                "Le montant doit être supérieur à 0."
            )
            self.champ_montant.setFocus()
            return

        if montant > self.solde_actuel:
            QMessageBox.warning(
                self, "Montant trop élevé",
                f"Le montant ({montant:,.0f} F) dépasse le solde restant "
                f"({self.solde_actuel:,.0f} F)."
            )
            self.champ_montant.setFocus()
            return

        self.champ_date.setText(date.today().isoformat())
        try:
            valider_date_iso(self.champ_date.text(), "La date du paiement")
        except ValueError:
            QMessageBox.warning(
                self,
                "Date invalide",
                "La date du jour ne peut pas être validée.",
            )
            return
        self.accept()

    def get_donnees_paiement(self) -> dict:
        """Retourne les données saisies pour création du Paiement."""
        return {
            "montant": self.champ_montant.value(),
            "date_paiement": self.champ_date.text().strip(),
            "mode_paiement": self.champ_mode.currentText(),
        }