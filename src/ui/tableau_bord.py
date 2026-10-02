"""
EduPaie — Tableau de bord.
Vue d'ensemble des statistiques et liste filtrée par statut.
"""
from src.ui.statut_delegate import StatutDelegate
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QFrame,
    QHeaderView,
)
from PySide6.QtCore import Qt

from src.ui.style import COULEURS


class TableauBordDialog(QDialog):
    """Boîte de dialogue du tableau de bord."""

    def __init__(self, eleve_service, paiement_service, parent=None):
        super().__init__(parent)
        self.eleve_service = eleve_service
        self.paiement_service = paiement_service

        self.setWindowTitle("Tableau de bord — EduPaie")
        self.setMinimumSize(960, 650)

        self._construire_interface()
        self._charger_statistiques()
        self._charger_eleves()

    def _construire_interface(self):
        """Construit l'interface du tableau de bord."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(26, 22, 26, 22)

        # ===== En-tête =====
        titre = QLabel("Tableau de bord")
        titre.setObjectName("titre_principal")
        layout.addWidget(titre)
        sous_titre = QLabel("Vue d'ensemble des frais de scolarité et des paiements.")
        sous_titre.setObjectName("sous_titre")
        layout.addWidget(sous_titre)

        # ===== Cartes de statistiques =====
        layout_stats = QHBoxLayout()
        layout_stats.setSpacing(12)

        self.carte_eleves = self._creer_carte("Élèves inscrits", "0", COULEURS["primaire"])
        self.carte_encaisse = self._creer_carte("Montant encaissé", "0 F", COULEURS["succes"])
        self.carte_restant = self._creer_carte("Reste à recouvrer", "0 F", COULEURS["attention"])
        self.carte_non_soldes = self._creer_carte("Élèves non soldés", "0", COULEURS["danger"])

        layout_stats.addWidget(self.carte_eleves)
        layout_stats.addWidget(self.carte_encaisse)
        layout_stats.addWidget(self.carte_restant)
        layout_stats.addWidget(self.carte_non_soldes)

        layout.addLayout(layout_stats)

        # ===== Filtre =====
        layout_filtre = QHBoxLayout()

        label_filtre = QLabel("Statut")
        label_filtre.setObjectName("titre_section")

        self.filtre_statut = QComboBox()
        self.filtre_statut.addItem("Tous", None)
        self.filtre_statut.addItem("Soldé", "Soldé")
        self.filtre_statut.addItem("Partiellement payé", "Partiellement payé")
        self.filtre_statut.addItem("Non payé", "Non payé")
        self.filtre_statut.setMinimumWidth(200)
        self.filtre_statut.currentIndexChanged.connect(self._charger_eleves)

        layout_filtre.addWidget(label_filtre)
        layout_filtre.addWidget(self.filtre_statut)
        layout_filtre.addStretch()

        cadre_filtre = QFrame()
        cadre_filtre.setObjectName("surface")
        cadre_filtre.setLayout(layout_filtre)
        layout_filtre.setContentsMargins(14, 10, 14, 10)
        layout.addWidget(cadre_filtre)

        # ===== Tableau =====
        self.label_resultats = QLabel("Situation des élèves")
        self.label_resultats.setObjectName("titre_section")
        layout.addWidget(self.label_resultats)

        self.tableau = QTableWidget()
        self.tableau.setColumnCount(7)
        self.tableau.setHorizontalHeaderLabels([
            "Nom", "Prénom", "Classe",
            "Montant dû", "Payé", "Solde", "Statut"
        ])
        self.tableau.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableau.setSelectionMode(QTableWidget.NoSelection)
        self.tableau.setAlternatingRowColors(True)
        self.tableau.verticalHeader().setVisible(False)
        self.tableau.verticalHeader().setDefaultSectionSize(40)
        header = self.tableau.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for column in range(2, 7):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        self.tableau.setItemDelegateForColumn(6, StatutDelegate(self.tableau))

        layout.addWidget(self.tableau)

        # ===== Bouton fermer =====
        layout_boutons = QHBoxLayout()
        bouton_fermer = QPushButton("Fermer")
        bouton_fermer.setObjectName("btn_primaire")
        bouton_fermer.setMinimumWidth(120)
        bouton_fermer.clicked.connect(self.accept)
        layout_boutons.addStretch()
        layout_boutons.addWidget(bouton_fermer)
        layout.addLayout(layout_boutons)

    def _creer_carte(self, titre: str, valeur: str, couleur: str) -> QFrame:
        """Crée une carte de statistique moderne."""
        carte = QFrame()
        carte.setObjectName("carte_stat")
        carte.setMinimumHeight(110)
        carte.setMaximumHeight(125)

        layout = QVBoxLayout(carte)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(8)

        label_titre = QLabel(titre)
        label_titre.setObjectName("carte_titre")

        label_valeur = QLabel(valeur)
        label_valeur.setObjectName("carte_valeur")
        label_valeur.setStyleSheet(
            f"color: {couleur};"
        )

        layout.addWidget(label_titre)
        layout.addWidget(label_valeur)
        layout.addStretch()

        return carte

    def _maj_carte(self, carte: QFrame, valeur: str):
        """Met à jour la valeur d'une carte."""
        label = carte.findChild(QLabel, "carte_valeur")
        if label:
            label.setText(valeur)

    def _charger_statistiques(self):
        """Calcule et affiche les statistiques globales."""
        eleves = self.eleve_service.lister_tous()
        nb_eleves = len(eleves)

        total_encaisse = 0
        total_du = 0
        nb_non_soldes = 0

        for eleve in eleves:
            solde_info = self.paiement_service.calculer_solde(eleve.id_eleve)
            total_encaisse += solde_info.total_paye
            total_du += solde_info.total_du
            if solde_info.statut != "Soldé":
                nb_non_soldes += 1

        total_restant = total_du - total_encaisse

        self._maj_carte(self.carte_eleves, str(nb_eleves))
        self._maj_carte(self.carte_encaisse, f"{total_encaisse:,.0f} F")
        self._maj_carte(self.carte_restant, f"{total_restant:,.0f} F")
        self._maj_carte(self.carte_non_soldes, str(nb_non_soldes))

    def _charger_eleves(self):
        """Charge la liste des élèves filtrée par statut."""
        statut_filtre = self.filtre_statut.currentData()

        eleves = self.eleve_service.lister_tous()

        donnees = []
        for eleve in eleves:
            solde_info = self.paiement_service.calculer_solde(eleve.id_eleve)
            if statut_filtre and solde_info.statut != statut_filtre:
                continue
            donnees.append((eleve, solde_info))

        self.tableau.setRowCount(len(donnees))
        self.label_resultats.setText(f"Situation des élèves  ·  {len(donnees)} résultat(s)")
        for i, (eleve, solde_info) in enumerate(donnees):
            self.tableau.setItem(i, 0, QTableWidgetItem(eleve.nom))
            self.tableau.setItem(i, 1, QTableWidgetItem(eleve.prenom))
            self.tableau.setItem(i, 2, QTableWidgetItem(f"Classe {eleve.id_classe}"))
            self.tableau.setItem(i, 3, QTableWidgetItem(f"{solde_info.total_du:,.0f} F"))
            self.tableau.setItem(i, 4, QTableWidgetItem(f"{solde_info.total_paye:,.0f} F"))
            self.tableau.setItem(i, 5, QTableWidgetItem(f"{solde_info.solde:,.0f} F"))

            item_statut = QTableWidgetItem(solde_info.statut)
            item_statut.setTextAlignment(Qt.AlignCenter)

            self.tableau.setItem(i, 6, item_statut)

        for column in range(2, 6):
            self.tableau.resizeColumnToContents(column)