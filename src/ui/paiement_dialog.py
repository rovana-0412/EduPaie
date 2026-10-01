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
        self.setMinimumWidth(480)

        self._construire_interface()

    def _construire_interface(self):
        """Construit les champs du dialogue."""
        layout = QVBoxLayout(self)

        # ===== En-tête : infos élève =====
        titre = QLabel(f"Paiement pour : {self.eleve.nom_complet}")
        titre.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
        layout.addWidget(titre)

        # Infos solde
        cadre_solde = QFrame()
        cadre_solde.setFrameShape(QFrame.StyledPanel)
        cadre_solde.setStyleSheet(
            "background-color: #f0f4ff; padding: 10px; border-radius: 5px;"
        )
        layout_solde = QVBoxLayout(cadre_solde)

        label_du = QLabel(f"Montant total dû : {self.eleve.montant_total_du:,.0f} F CFA")
        label_solde = QLabel(f"Solde restant : {self.solde_actuel:,.0f} F CFA")
        label_solde.setStyleSheet("font-weight: bold; color: #1e40af;")

        layout_solde.addWidget(label_du)
        layout_solde.addWidget(label_solde)
        layout.addWidget(cadre_solde)

        # ===== Formulaire =====
        form = QFormLayout()
        form.setSpacing(10)

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

        bouton_valider = QPushButton("💰 Enregistrer le paiement")
        bouton_valider.setDefault(True)
        bouton_valider.clicked.connect(self._valider)

        layout_boutons.addStretch()
        layout_boutons.addWidget(bouton_annuler)
        layout_boutons.addWidget(bouton_valider)

        layout.addLayout(layout_boutons)

    def _valider(self):
        """Valide les champs avant de fermer."""
        montant = self.champ_montant.value()
        date_paiement = self.champ_date.text().strip()

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

        if not date_paiement:
            QMessageBox.warning(self, "Champ manquant", "La date est obligatoire.")
            self.champ_date.setFocus()
            return

        # Vérifier le format de la date
        try:
            parties = date_paiement.split("-")
            if len(parties) != 3 or len(parties[0]) != 4:
                raise ValueError
            int(parties[0]); int(parties[1]); int(parties[2])
        except (ValueError, IndexError):
            QMessageBox.warning(
                self, "Format invalide",
                "La date doit être au format AAAA-MM-JJ (ex : 2026-10-01)."
            )
            self.champ_date.setFocus()
            return

        self.accept()

    def get_donnees_paiement(self) -> dict:
        """Retourne les données saisies pour création du Paiement."""
        return {
            "montant": self.champ_montant.value(),
            "date_paiement": self.champ_date.text().strip(),
            "mode_paiement": self.champ_mode.currentText(),
        }