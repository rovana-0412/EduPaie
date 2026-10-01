"""
EduPaie — Fenêtre principale.
Affiche la liste des élèves et permet de les gérer.
"""
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application."""

    def __init__(self, classe_repo, eleve_service, paiement_service):
        super().__init__()

        # Références aux services
        self.classe_repo = classe_repo
        self.eleve_service = eleve_service
        self.paiement_service = paiement_service

        # Configuration de la fenêtre
        self.setWindowTitle("EduPaie — Gestion des paiements scolaires")
        self.resize(1000, 600)

        # Construire l'interface
        self._construire_interface()

        # Charger les données
        self._charger_eleves()

    def _construire_interface(self):
        """Construit les widgets de la fenêtre."""
        central = QWidget()
        self.setCentralWidget(central)

        layout_principal = QVBoxLayout(central)

        # ===== Titre =====
        titre = QLabel("Liste des élèves")
        titre.setStyleSheet("font-size: 18px; font-weight: bold; padding: 8px;")
        layout_principal.addWidget(titre)

        # ===== Barre de recherche + filtre =====
        layout_recherche = QHBoxLayout()

        self.champ_recherche = QLineEdit()
        self.champ_recherche.setPlaceholderText("Rechercher un élève (nom ou prénom)...")
        self.champ_recherche.textChanged.connect(self._charger_eleves)

        self.filtre_classe = QComboBox()
        self.filtre_classe.addItem("Toutes les classes", None)
        for classe in self.classe_repo.lister_toutes():
            self.filtre_classe.addItem(classe.nom_classe, classe.id_classe)
        self.filtre_classe.currentIndexChanged.connect(self._charger_eleves)

        layout_recherche.addWidget(self.champ_recherche, 3)
        layout_recherche.addWidget(self.filtre_classe, 1)
        layout_principal.addLayout(layout_recherche)

        # ===== Tableau des élèves =====
        self.tableau = QTableWidget()
        self.tableau.setColumnCount(6)
        self.tableau.setHorizontalHeaderLabels([
            "ID", "Nom", "Prénom", "Date naissance",
            "Classe", "Montant dû (F)"
        ])
        self.tableau.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableau.setSelectionBehavior(QTableWidget.SelectRows)
        layout_principal.addWidget(self.tableau)

        # ===== Boutons d'action =====
        layout_boutons = QHBoxLayout()

        bouton_ajouter = QPushButton("➕ Ajouter un élève")
        bouton_ajouter.clicked.connect(self._ajouter_eleve)

        bouton_modifier = QPushButton("✏ Modifier")
        bouton_modifier.clicked.connect(self._modifier_eleve)

        bouton_supprimer = QPushButton("🗑 Supprimer")
        bouton_supprimer.clicked.connect(self._supprimer_eleve)

        bouton_actualiser = QPushButton("🔄 Actualiser")
        bouton_actualiser.clicked.connect(self._charger_eleves)

        layout_boutons.addWidget(bouton_ajouter)
        layout_boutons.addWidget(bouton_modifier)
        layout_boutons.addWidget(bouton_supprimer)
        layout_boutons.addStretch()
        layout_boutons.addWidget(bouton_actualiser)

        layout_principal.addLayout(layout_boutons)

    def _charger_eleves(self):
        """Charge la liste des élèves dans le tableau."""
        terme = self.champ_recherche.text().strip()
        id_classe = self.filtre_classe.currentData()

        # Récupérer les élèves
        if terme:
            eleves = self.eleve_service.rechercher(terme)
        else:
            eleves = self.eleve_service.lister_tous()

        # Filtrer par classe si nécessaire
        if id_classe:
            eleves = [e for e in eleves if e.id_classe == id_classe]

        # Remplir le tableau
        self.tableau.setRowCount(len(eleves))
        for i, eleve in enumerate(eleves):
            self.tableau.setItem(i, 0, QTableWidgetItem(str(eleve.id_eleve)))
            self.tableau.setItem(i, 1, QTableWidgetItem(eleve.nom))
            self.tableau.setItem(i, 2, QTableWidgetItem(eleve.prenom))
            self.tableau.setItem(i, 3, QTableWidgetItem(eleve.date_naissance))
            self.tableau.setItem(i, 4, QTableWidgetItem(str(eleve.id_classe)))
            self.tableau.setItem(i, 5, QTableWidgetItem(f"{eleve.montant_total_du:,.0f}"))

        self.tableau.resizeColumnsToContents()

    def _ajouter_eleve(self):
        QMessageBox.information(self, "Info", "Fonctionnalité à venir (branche suivante).")

    def _modifier_eleve(self):
        QMessageBox.information(self, "Info", "Fonctionnalité à venir (branche suivante).")

    def _supprimer_eleve(self):
        QMessageBox.information(self, "Info", "Fonctionnalité à venir (branche suivante).")