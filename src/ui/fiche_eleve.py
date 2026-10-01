"""
EduPaie — Fiche élève avec historique des paiements.
Affiche les informations d'un élève et la liste de ses paiements.
"""
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFrame,
    QMessageBox,
)
from PySide6.QtCore import Qt

from src.models import Eleve, SoldeEleve


class FicheEleveDialog(QDialog):
    """Boîte de dialogue affichant la fiche complète d'un élève."""

    def __init__(self, eleve: Eleve, solde_info: SoldeEleve, paiements: list, parent=None):
        """
        Args:
            eleve       : l'élève concerné
            solde_info  : objet SoldeEleve (total dû, total payé, solde, statut)
            paiements   : liste des paiements de l'élève
            parent      : widget parent
        """
        super().__init__(parent)
        self.eleve = eleve
        self.solde_info = solde_info
        self.paiements = paiements

        self.setWindowTitle(f"Fiche élève — {eleve.nom_complet}")
        self.setMinimumSize(700, 550)

        self._construire_interface()

    def _construire_interface(self):
        """Construit l'interface de la fiche."""
        layout = QVBoxLayout(self)

        # ===== En-tête : nom de l'élève =====
        titre = QLabel(self.eleve.nom_complet)
        titre.setStyleSheet(
            "font-size: 20px; font-weight: bold; padding: 10px; color: #1e40af;"
        )
        layout.addWidget(titre)

        # ===== Bloc infos élève =====
        cadre_infos = QFrame()
        cadre_infos.setFrameShape(QFrame.StyledPanel)
        cadre_infos.setStyleSheet(
            "background-color: #f9fafb; padding: 10px; border: 1px solid #e5e7eb;"
        )
        form_infos = QFormLayout(cadre_infos)

        form_infos.addRow("Date de naissance :", QLabel(self.eleve.date_naissance))
        form_infos.addRow("Année scolaire :", QLabel(self.eleve.annee_scolaire))
        form_infos.addRow("Classe :", QLabel(f"ID {self.eleve.id_classe}"))

        layout.addWidget(cadre_infos)

        # ===== Bloc solde =====
        cadre_solde = QFrame()
        cadre_solde.setFrameShape(QFrame.StyledPanel)
        cadre_solde.setStyleSheet(
            "background-color: #eff6ff; padding: 12px; "
            "border: 1px solid #bfdbfe; border-radius: 6px;"
        )
        layout_solde = QVBoxLayout(cadre_solde)

        label_du = QLabel(f"💰 Montant total dû : {self.solde_info.total_du:,.0f} F CFA")
        label_paye = QLabel(f"✅ Total déjà payé : {self.solde_info.total_paye:,.0f} F CFA")
        label_solde = QLabel(f"🔵 Solde restant : {self.solde_info.solde:,.0f} F CFA")
        label_solde.setStyleSheet("font-size: 15px; font-weight: bold;")

        label_statut = QLabel(f"📊 Statut : {self.solde_info.statut}")
        if self.solde_info.statut == "Soldé":
            label_statut.setStyleSheet(
                "background-color: #10b981; color: white; "
                "padding: 6px; border-radius: 4px; font-weight: bold;"
            )
        elif self.solde_info.statut == "Partiellement payé":
            label_statut.setStyleSheet(
                "background-color: #f59e0b; color: white; "
                "padding: 6px; border-radius: 4px; font-weight: bold;"
            )
        else:
            label_statut.setStyleSheet(
                "background-color: #ef4444; color: white; "
                "padding: 6px; border-radius: 4px; font-weight: bold;"
            )

        layout_solde.addWidget(label_du)
        layout_solde.addWidget(label_paye)
        layout_solde.addWidget(label_solde)
        layout_solde.addWidget(label_statut)

        layout.addWidget(cadre_solde)

        # ===== Titre historique =====
        titre_hist = QLabel(f"📜 Historique des paiements ({len(self.paiements)})")
        titre_hist.setStyleSheet(
            "font-size: 15px; font-weight: bold; padding: 8px 0;"
        )
        layout.addWidget(titre_hist)

        # ===== Tableau des paiements =====
        self.tableau = QTableWidget()
        self.tableau.setColumnCount(5)
        self.tableau.setHorizontalHeaderLabels([
            "ID", "Date", "Montant (F)", "Mode", "N° Reçu"
        ])
        self.tableau.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableau.setSelectionBehavior(QTableWidget.SelectRows)

        self.tableau.setRowCount(len(self.paiements))
        for i, p in enumerate(self.paiements):
            self.tableau.setItem(i, 0, QTableWidgetItem(str(p.id_paiement)))
            self.tableau.setItem(i, 1, QTableWidgetItem(p.date_paiement))
            self.tableau.setItem(i, 2, QTableWidgetItem(f"{p.montant:,.0f}"))
            self.tableau.setItem(i, 3, QTableWidgetItem(p.mode_paiement))
            self.tableau.setItem(i, 4, QTableWidgetItem(p.numero_recu))

        self.tableau.resizeColumnsToContents()
        layout.addWidget(self.tableau)

        # ===== Boutons =====
        layout_boutons = QHBoxLayout()

        bouton_voir_recu = QPushButton("🖨 Voir le reçu")
        bouton_voir_recu.clicked.connect(self._voir_recu)

        bouton_fermer = QPushButton("Fermer")
        bouton_fermer.clicked.connect(self.accept)

        layout_boutons.addWidget(bouton_voir_recu)
        layout_boutons.addStretch()
        layout_boutons.addWidget(bouton_fermer)

        layout.addLayout(layout_boutons)

    def _voir_recu(self):
        """Affiche un message (sera remplacé par la génération PDF)."""
        ligne = self.tableau.currentRow()
        if ligne < 0:
            QMessageBox.warning(
                self, "Aucune sélection",
                "Veuillez sélectionner un paiement dans la liste."
            )
            return

        numero_recu = self.tableau.item(ligne, 4).text()
        QMessageBox.information(
            self, "Reçu sélectionné",
            f"Numéro de reçu : {numero_recu}\n\n"
            "La génération PDF sera implémentée dans la prochaine branche."
        )