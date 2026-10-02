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
    QHeaderView,
)
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QDesktopServices

from src.models import Eleve, SoldeEleve


def _total_paye_jusquau_paiement(paiements, paiement_selectionne) -> float:
    """Total chronologique inclusif, les identifiants départageant les dates égales."""
    return sum(
        paiement.montant
        for paiement in paiements
        if (paiement.date_paiement, paiement.id_paiement)
        <= (
            paiement_selectionne.date_paiement,
            paiement_selectionne.id_paiement,
        )
    )


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
        self.setMinimumSize(760, 620)

        self._construire_interface()

    def _construire_interface(self):
        """Construit l'interface de la fiche."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 22)
        layout.setSpacing(14)

        # ===== En-tête : nom de l'élève =====
        titre = QLabel(self.eleve.nom_complet)
        titre.setObjectName("titre_principal")
        layout.addWidget(titre)
        sous_titre = QLabel("Fiche de suivi scolaire et historique des règlements.")
        sous_titre.setObjectName("sous_titre")
        layout.addWidget(sous_titre)

        # ===== Bloc infos élève =====
        cadre_infos = QFrame()
        cadre_infos.setObjectName("surface")
        cadre_infos.setFrameShape(QFrame.StyledPanel)
        form_infos = QFormLayout(cadre_infos)
        form_infos.setContentsMargins(16, 12, 16, 12)
        form_infos.setHorizontalSpacing(20)
        form_infos.setVerticalSpacing(8)

        form_infos.addRow("Date de naissance", QLabel(self.eleve.date_naissance))
        form_infos.addRow("Année scolaire", QLabel(self.eleve.annee_scolaire))
        form_infos.addRow("Classe", QLabel(f"Classe {self.eleve.id_classe}"))

        layout.addWidget(cadre_infos)

        # ===== Bloc solde =====
        cadre_solde = QFrame()
        cadre_solde.setObjectName("surface")
        layout_solde = QVBoxLayout(cadre_solde)
        layout_solde.setContentsMargins(16, 14, 16, 14)
        layout_solde.setSpacing(7)

        titre_solde = QLabel("Situation financière")
        titre_solde.setObjectName("titre_section")
        layout_solde.addWidget(titre_solde)
        label_du = QLabel(f"Montant total dû  ·  {self.solde_info.total_du:,.0f} F CFA")
        label_paye = QLabel(f"Total déjà payé  ·  {self.solde_info.total_paye:,.0f} F CFA")
        label_solde = QLabel(f"Solde restant  ·  {self.solde_info.solde:,.0f} F CFA")
        label_solde.setObjectName("titre_section")

        couleur_statut = {
            "Soldé": "statut_succes",
            "Partiellement payé": "statut_attention",
            "Non payé": "statut_danger",
        }.get(self.solde_info.statut, "statut_danger")
        label_statut = QLabel(self.solde_info.statut)
        label_statut.setObjectName(couleur_statut)
        label_statut.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_statut.setMaximumWidth(210)

        layout_solde.addWidget(label_du)
        layout_solde.addWidget(label_paye)
        layout_solde.addWidget(label_solde)
        layout_solde.addWidget(label_statut)

        layout.addWidget(cadre_solde)

        # ===== Titre historique =====
        titre_hist = QLabel(f"Historique des paiements  ·  {len(self.paiements)}")
        titre_hist.setObjectName("titre_section")
        layout.addWidget(titre_hist)

        # ===== Tableau des paiements =====
        self.tableau = QTableWidget()
        self.tableau.setColumnCount(5)
        self.tableau.setHorizontalHeaderLabels([
            "ID", "Date", "Montant (F)", "Mode", "N° Reçu"
        ])
        self.tableau.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableau.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tableau.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tableau.setAlternatingRowColors(True)
        self.tableau.verticalHeader().setVisible(False)
        self.tableau.verticalHeader().setDefaultSectionSize(40)
        self.tableau.setColumnHidden(0, True)
        self.tableau.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.Stretch
        )

        self.tableau.setRowCount(len(self.paiements))
        for i, p in enumerate(self.paiements):
            self.tableau.setItem(i, 0, QTableWidgetItem(str(p.id_paiement)))
            self.tableau.setItem(i, 1, QTableWidgetItem(p.date_paiement))
            self.tableau.setItem(i, 2, QTableWidgetItem(f"{p.montant:,.0f} F"))
            self.tableau.setItem(i, 3, QTableWidgetItem(p.mode_paiement))
            self.tableau.setItem(i, 4, QTableWidgetItem(p.numero_recu))

        self.tableau.resizeColumnsToContents()
        layout.addWidget(self.tableau)

        # ===== Boutons =====
        layout_boutons = QHBoxLayout()

        bouton_voir_recu = QPushButton("Générer le reçu")
        bouton_voir_recu.setObjectName("btn_primaire")
        bouton_voir_recu.clicked.connect(self._voir_recu)

        self.bouton_ouvrir_recu = QPushButton("Ouvrir le reçu généré")
        self.bouton_ouvrir_recu.setEnabled(False)
        self.bouton_ouvrir_recu.setToolTip(
            "Sélectionnez un paiement dont le reçu PDF a déjà été généré."
        )
        self.bouton_ouvrir_recu.clicked.connect(self._ouvrir_recu_genere)
        self.tableau.itemSelectionChanged.connect(self._maj_bouton_ouvrir_recu)

        bouton_fermer = QPushButton("Fermer")
        bouton_fermer.clicked.connect(self.accept)

        layout_boutons.addWidget(bouton_voir_recu)
        layout_boutons.addWidget(self.bouton_ouvrir_recu)
        layout_boutons.addStretch()
        layout_boutons.addWidget(bouton_fermer)

        layout.addLayout(layout_boutons)

    def _paiement_selectionne(self):
        ligne = self.tableau.currentRow()
        if ligne < 0:
            return None

        id_paiement = int(self.tableau.item(ligne, 0).text())
        return next(
            (paiement for paiement in self.paiements if paiement.id_paiement == id_paiement),
            None,
        )

    def _chemin_recu_genere(self, paiement):
        from src.pdf_generator import RECUS_DIR

        return RECUS_DIR / f"{paiement.numero_recu}.pdf"

    def _maj_bouton_ouvrir_recu(self):
        paiement = self._paiement_selectionne()
        disponible = paiement is not None and self._chemin_recu_genere(paiement).is_file()
        self.bouton_ouvrir_recu.setEnabled(disponible)
        if paiement is None:
            self.bouton_ouvrir_recu.setToolTip(
                "Sélectionnez un paiement dont le reçu PDF a déjà été généré."
            )
        elif disponible:
            self.bouton_ouvrir_recu.setToolTip("Ouvrir le reçu PDF déjà généré.")
        else:
            self.bouton_ouvrir_recu.setToolTip(
                "Aucun reçu généré pour ce paiement. Utilisez « Générer le reçu »."
            )

    def _ouvrir_fichier_recu(self, chemin):
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(chemin))):
            QMessageBox.critical(
                self,
                "Ouverture impossible",
                f"Impossible d'ouvrir le reçu :\n{chemin}",
            )
            return False
        return True

    def _ouvrir_recu_genere(self):
        paiement = self._paiement_selectionne()
        if paiement is None:
            QMessageBox.warning(
                self, "Aucune sélection", "Veuillez sélectionner un paiement."
            )
            return

        chemin = self._chemin_recu_genere(paiement)
        if not chemin.is_file():
            self._maj_bouton_ouvrir_recu()
            QMessageBox.information(
                self,
                "Reçu indisponible",
                "Aucun reçu PDF n'a encore été généré pour ce paiement.",
            )
            return

        self._ouvrir_fichier_recu(chemin)

    def _voir_recu(self):
        """Génère le PDF du reçu sélectionné et l'ouvre."""
        from src.pdf_generator import GenerateurRecu

        paiement = self._paiement_selectionne()
        if paiement is None and self.tableau.currentRow() < 0:
            QMessageBox.warning(
                self, "Aucune sélection",
                "Veuillez sélectionner un paiement dans la liste."
            )
            return

        if not paiement:
            QMessageBox.warning(self, "Erreur", "Paiement introuvable.")
            return

        try:
            # Calculer le solde APRÈS ce paiement
            # = montant total dû - somme de tous les paiements jusqu'à celui-ci
            total_paye_apres = _total_paye_jusquau_paiement(
                self.paiements, paiement
            )
            solde_apres = self.solde_info.total_du - total_paye_apres

            # Statut après ce paiement
            if solde_apres <= 0:
                statut_apres = "Soldé"
            elif total_paye_apres > 0:
                statut_apres = "Partiellement payé"
            else:
                statut_apres = "Non payé"

            generateur = GenerateurRecu(nom_ecole="École EduPaie")
            chemin = generateur.generer(
                numero_recu=paiement.numero_recu,
                nom_eleve=self.eleve.nom_complet,
                classe=f"Classe {self.eleve.id_classe}",
                annee_scolaire=self.eleve.annee_scolaire,
                date_paiement=paiement.date_paiement,
                montant_paye=paiement.montant,
                mode_paiement=paiement.mode_paiement,
                montant_total_du=self.solde_info.total_du,
                total_paye=total_paye_apres,
                solde_apres=solde_apres,
                statut=statut_apres,
            )

            self._ouvrir_fichier_recu(chemin)

            QMessageBox.information(
                self, "Reçu généré",
                f"Le reçu a été généré :\n{chemin}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Erreur",
                f"Impossible de générer le reçu :\n{e}"
            )