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
        self.tableau.setColumnCount(8)
        self.tableau.setHorizontalHeaderLabels([
            "ID", "Nom", "Prénom", "Date naissance",
            "Classe", "Montant dû (F)", "Solde restant (F)", "Statut"
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

        bouton_fiche = QPushButton("📋 Voir la fiche")
        bouton_fiche.clicked.connect(self._voir_fiche)

        bouton_payer = QPushButton("💰 Enregistrer un paiement")
        bouton_payer.setStyleSheet(
            "background-color: #10b981; color: white; font-weight: bold; padding: 6px;"
        )
        bouton_payer.clicked.connect(self._enregistrer_paiement)

        bouton_actualiser = QPushButton("🔄 Actualiser")
        bouton_actualiser.clicked.connect(self._charger_eleves)

        layout_boutons.addWidget(bouton_ajouter)
        layout_boutons.addWidget(bouton_modifier)
        layout_boutons.addWidget(bouton_supprimer)
        layout_boutons.addWidget(bouton_fiche)
        layout_boutons.addStretch()
        layout_boutons.addWidget(bouton_payer)
        layout_boutons.addWidget(bouton_actualiser)

        layout_principal.addLayout(layout_boutons)

    def _charger_eleves(self):
        """Charge la liste des élèves dans le tableau avec solde et statut."""
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
            # Calculer le solde
            solde_info = self.paiement_service.calculer_solde(eleve.id_eleve)

            self.tableau.setItem(i, 0, QTableWidgetItem(str(eleve.id_eleve)))
            self.tableau.setItem(i, 1, QTableWidgetItem(eleve.nom))
            self.tableau.setItem(i, 2, QTableWidgetItem(eleve.prenom))
            self.tableau.setItem(i, 3, QTableWidgetItem(eleve.date_naissance))
            self.tableau.setItem(i, 4, QTableWidgetItem(str(eleve.id_classe)))
            self.tableau.setItem(i, 5, QTableWidgetItem(f"{eleve.montant_total_du:,.0f}"))
            self.tableau.setItem(i, 6, QTableWidgetItem(f"{solde_info.solde:,.0f}"))

            # Colonne Statut (avec couleur)
            item_statut = QTableWidgetItem(solde_info.statut)
            item_statut.setTextAlignment(Qt.AlignCenter)

            if solde_info.statut == "Soldé":
                item_statut.setBackground(Qt.green)
                item_statut.setForeground(Qt.white)
            elif solde_info.statut == "Partiellement payé":
                item_statut.setBackground(Qt.yellow)
                item_statut.setForeground(Qt.black)
            else:  # Non payé
                item_statut.setBackground(Qt.red)
                item_statut.setForeground(Qt.white)

            self.tableau.setItem(i, 7, item_statut)

        self.tableau.resizeColumnsToContents()

    def _ajouter_eleve(self):
        """Ouvre le formulaire d'ajout."""
        from src.ui.eleve_form import EleveForm

        classes = self.classe_repo.lister_toutes()
        form = EleveForm(classes, eleve=None, parent=self)
        if form.exec() == EleveForm.Accepted:
            try:
                eleve = form.get_eleve()
                self.eleve_service.ajouter(eleve)
                self._charger_eleves()
                QMessageBox.information(self, "Succès", "Élève ajouté avec succès.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter l'élève :\n{e}")

    def _modifier_eleve(self):
        """Ouvre le formulaire de modification pour l'élève sélectionné."""
        from src.ui.eleve_form import EleveForm

        ligne = self.tableau.currentRow()
        if ligne < 0:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner un élève.")
            return

        id_eleve = int(self.tableau.item(ligne, 0).text())
        eleve = self.eleve_service.eleve_repo.trouver_par_id(id_eleve)
        if not eleve:
            QMessageBox.warning(self, "Erreur", "Élève introuvable.")
            return

        classes = self.classe_repo.lister_toutes()
        form = EleveForm(classes, eleve=eleve, parent=self)
        if form.exec() == EleveForm.Accepted:
            try:
                eleve_modifie = form.get_eleve()
                self.eleve_service.modifier(eleve_modifie)
                self._charger_eleves()
                QMessageBox.information(self, "Succès", "Élève modifié avec succès.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de modifier l'élève :\n{e}")

    def _supprimer_eleve(self):
        """Supprime l'élève sélectionné après confirmation."""
        ligne = self.tableau.currentRow()
        if ligne < 0:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner un élève.")
            return

        id_eleve = int(self.tableau.item(ligne, 0).text())
        nom = self.tableau.item(ligne, 1).text()
        prenom = self.tableau.item(ligne, 2).text()

        reponse = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous vraiment supprimer {nom} {prenom} ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reponse == QMessageBox.Yes:
            try:
                self.eleve_service.supprimer(id_eleve)
                self._charger_eleves()
                QMessageBox.information(self, "Succès", "Élève supprimé.")
            except Exception as e:
                QMessageBox.critical(
                    self, "Erreur",
                    f"Impossible de supprimer l'élève :\n{e}\n\n"
                    "Vérifiez qu'il n'a pas de paiements associés."
                )
    def _enregistrer_paiement(self):
        """Ouvre le dialogue d'enregistrement d'un paiement."""
        from src.ui.paiement_dialog import PaiementDialog

        # Vérifier qu'un élève est sélectionné
        ligne = self.tableau.currentRow()
        if ligne < 0:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner un élève.")
            return

        # Récupérer l'élève
        id_eleve = int(self.tableau.item(ligne, 0).text())
        eleve = self.eleve_service.eleve_repo.trouver_par_id(id_eleve)
        if not eleve:
            QMessageBox.warning(self, "Erreur", "Élève introuvable.")
            return

        # Calculer le solde actuel
        solde_info = self.paiement_service.calculer_solde(id_eleve)

        # Vérifier que l'élève n'a pas déjà soldé
        if solde_info.solde <= 0:
            QMessageBox.information(
                self, "Déjà soldé",
                f"{eleve.nom_complet} a déjà soldé ses frais de scolarité."
            )
            return

        # Ouvrir le dialogue
        dialogue = PaiementDialog(eleve, solde_info.solde, parent=self)
        if dialogue.exec() == PaiementDialog.Accepted:
            try:
                donnees = dialogue.get_donnees_paiement()
                self.paiement_service.enregistrer_paiement(
                    id_eleve=id_eleve,
                    montant=donnees["montant"],
                    mode_paiement=donnees["mode_paiement"],
                    date_paiement=donnees["date_paiement"],
                )

                               # Récupérer le paiement qui vient d'être créé
                donnees = dialogue.get_donnees_paiement()
                paiement_cree = self.paiement_service.enregistrer_paiement(
                    id_eleve=id_eleve,
                    montant=donnees["montant"],
                    mode_paiement=donnees["mode_paiement"],
                    date_paiement=donnees["date_paiement"],
                )

                nouveau_solde = self.paiement_service.calculer_solde(id_eleve)

                QMessageBox.information(
                    self, "Paiement enregistré",
                    f"Paiement enregistré avec succès.\n\n"
                    f"Numéro de reçu : {paiement_cree.numero_recu}\n"
                    f"Nouveau solde : {nouveau_solde.solde:,.0f} F CFA"
                )
                self._charger_eleves()
            except Exception as e:
                QMessageBox.critical(
                    self, "Erreur",
                    f"Impossible d'enregistrer le paiement :\n{e}"
                )

    def _voir_fiche(self):
        """Ouvre la fiche de l'élève sélectionné."""
        from src.ui.fiche_eleve import FicheEleveDialog

        ligne = self.tableau.currentRow()
        if ligne < 0:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner un élève.")
            return

        id_eleve = int(self.tableau.item(ligne, 0).text())
        eleve = self.eleve_service.eleve_repo.trouver_par_id(id_eleve)
        if not eleve:
            QMessageBox.warning(self, "Erreur", "Élève introuvable.")
            return

        solde_info = self.paiement_service.calculer_solde(id_eleve)
        paiements = self.paiement_service.lister_paiements(id_eleve)

        dialogue = FicheEleveDialog(eleve, solde_info, paiements, parent=self)
        dialogue.exec()