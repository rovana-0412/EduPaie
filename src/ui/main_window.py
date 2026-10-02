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
    QFrame,
    QHeaderView,
)
from PySide6.QtCore import Qt

from src.ui.statut_delegate import StatutDelegate


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application."""

    def __init__(self, classe_repo, eleve_service, paiement_service):
        super().__init__()

        # Références aux services
        self.classe_repo = classe_repo
        self.eleve_service = eleve_service
        self.paiement_service = paiement_service
        self.classes = {
            classe.id_classe: classe.nom_classe
            for classe in self.classe_repo.lister_toutes()
        }

        # Configuration de la fenêtre
        self.setWindowTitle("EduPaie — Gestion des paiements scolaires")
        self.resize(1200, 760)
        self.setMinimumSize(940, 620)

        # Construire l'interface
        self._construire_interface()

        # Charger les données
        self._charger_eleves()

    def _construire_interface(self):
        """Construit les widgets de la fenêtre."""
        central = QWidget()
        self.setCentralWidget(central)

        layout_principal = QVBoxLayout(central)
        layout_principal.setContentsMargins(28, 24, 28, 22)
        layout_principal.setSpacing(16)

        # ===== En-tête =====
        entete = QHBoxLayout()
        bloc_titre = QVBoxLayout()
        titre = QLabel("Suivi des élèves")
        titre.setObjectName("titre_principal")
        sous_titre = QLabel("Gérez les inscriptions et suivez les paiements de scolarité.")
        sous_titre.setObjectName("sous_titre")
        bloc_titre.addWidget(titre)
        bloc_titre.addWidget(sous_titre)
        entete.addLayout(bloc_titre)
        entete.addStretch()

        bouton_ajouter_classe = QPushButton("Ajouter une classe")
        bouton_ajouter_classe.clicked.connect(self._ajouter_classe)
        entete.addWidget(bouton_ajouter_classe)

        bouton_tableau_bord = QPushButton("Tableau de bord")
        bouton_tableau_bord.setObjectName("btn_primaire")
        bouton_tableau_bord.clicked.connect(self._ouvrir_tableau_bord)
        entete.addWidget(bouton_tableau_bord)
        layout_principal.addLayout(entete)

        # ===== Barre de recherche + filtre =====
        cadre_recherche = QFrame()
        cadre_recherche.setObjectName("surface")
        layout_recherche = QHBoxLayout(cadre_recherche)
        layout_recherche.setContentsMargins(14, 12, 14, 12)
        layout_recherche.setSpacing(12)

        self.champ_recherche = QLineEdit()
        self.champ_recherche.setPlaceholderText("Rechercher par nom ou prénom")
        self.champ_recherche.textChanged.connect(self._charger_eleves)

        self.filtre_classe = QComboBox()
        self.filtre_classe.addItem("Toutes les classes", None)
        for classe in self.classe_repo.lister_toutes():
            self.filtre_classe.addItem(classe.nom_classe, classe.id_classe)
        self.filtre_classe.currentIndexChanged.connect(self._charger_eleves)

        layout_recherche.addWidget(self.champ_recherche, 3)
        layout_recherche.addWidget(self.filtre_classe, 1)
        layout_principal.addWidget(cadre_recherche)

        self.label_resume = QLabel("Liste des élèves")
        self.label_resume.setObjectName("titre_section")
        layout_principal.addWidget(self.label_resume)

        # ===== Tableau des élèves =====
        self.tableau = QTableWidget()
        self.tableau.setColumnCount(8)
        self.tableau.setHorizontalHeaderLabels([
            "ID", "Nom", "Prénom", "Date de naissance",
            "Classe", "Montant dû", "Solde restant", "Statut"
        ])
        self.tableau.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableau.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tableau.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tableau.setAlternatingRowColors(True)
        self.tableau.verticalHeader().setVisible(False)
        self.tableau.verticalHeader().setDefaultSectionSize(42)
        entete_tableau = self.tableau.horizontalHeader()
        entete_tableau.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        entete_tableau.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        entete_tableau.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        self.tableau.setColumnHidden(0, True)
        self.tableau.setItemDelegateForColumn(7, StatutDelegate(self.tableau))
        layout_principal.addWidget(self.tableau)

        # ===== Boutons d'action =====
        layout_boutons = QHBoxLayout()
        layout_boutons.setSpacing(8)

        bouton_ajouter = QPushButton("Ajouter un élève")
        bouton_ajouter.setObjectName("btn_primaire")
        bouton_ajouter.clicked.connect(self._ajouter_eleve)

        bouton_modifier = QPushButton("Modifier")
        bouton_modifier.clicked.connect(self._modifier_eleve)

        bouton_supprimer = QPushButton("Supprimer")
        bouton_supprimer.setObjectName("btn_danger")
        bouton_supprimer.clicked.connect(self._supprimer_eleve)

        bouton_fiche = QPushButton("Fiche élève")
        bouton_fiche.clicked.connect(self._voir_fiche)

        bouton_payer = QPushButton("Enregistrer un paiement")
        bouton_payer.setObjectName("btn_succes")
        bouton_payer.clicked.connect(self._enregistrer_paiement)

        bouton_actualiser = QPushButton("Actualiser")
        bouton_actualiser.clicked.connect(self._charger_eleves)
        layout_boutons.addWidget(bouton_ajouter)
        layout_boutons.addWidget(bouton_ajouter)
        layout_boutons.addWidget(bouton_modifier)
        layout_boutons.addWidget(bouton_supprimer)
        layout_boutons.addWidget(bouton_fiche)
        layout_boutons.addStretch()
        layout_boutons.addWidget(bouton_payer)
        layout_boutons.addWidget(bouton_actualiser)

        layout_principal.addLayout(layout_boutons)

    def _actualiser_classes(self, id_classe_selectionnee=None):
        classes = self.classe_repo.lister_toutes()
        self.classes = {
            classe.id_classe: classe.nom_classe for classe in classes
        }
        self.filtre_classe.blockSignals(True)
        self.filtre_classe.clear()
        self.filtre_classe.addItem("Toutes les classes", None)
        for classe in classes:
            self.filtre_classe.addItem(
                classe.nom_classe, classe.id_classe
            )
        if id_classe_selectionnee is not None:
            index = self.filtre_classe.findData(id_classe_selectionnee)
            if index >= 0:
                self.filtre_classe.setCurrentIndex(index)
        self.filtre_classe.blockSignals(False)

    def _ajouter_classe(self):
        from src.ui.classe_dialog import ClasseDialog

        dialogue = ClasseDialog(self)
        if dialogue.exec() != ClasseDialog.DialogCode.Accepted:
            return

        donnees = dialogue.get_donnees_classe()
        try:
            id_classe = self.classe_repo.ajouter(**donnees)
        except ValueError as exc:
            QMessageBox.warning(self, "Classe déjà existante", str(exc))
            return
        except Exception as exc:
            QMessageBox.critical(
                self, "Erreur", f"Impossible d'ajouter la classe :\n{exc}"
            )
            return

        self._actualiser_classes(id_classe)
        self._charger_eleves()
        QMessageBox.information(
            self,
            "Classe ajoutée",
            f"La classe « {donnees['nom_classe']} » a été ajoutée.\n"
            "Elle est maintenant disponible pour inscrire des élèves.",
        )

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
            solde_info = self.paiement_service.calculer_solde(eleve.id_eleve)

            self.tableau.setItem(i, 0, QTableWidgetItem(str(eleve.id_eleve)))
            self.tableau.setItem(i, 1, QTableWidgetItem(eleve.nom))
            self.tableau.setItem(i, 2, QTableWidgetItem(eleve.prenom))
            self.tableau.setItem(i, 3, QTableWidgetItem(eleve.date_naissance))
            self.tableau.setItem(
                i, 4, QTableWidgetItem(self.classes.get(eleve.id_classe, str(eleve.id_classe)))
            )
            self.tableau.setItem(i, 5, QTableWidgetItem(f"{eleve.montant_total_du:,.0f} F"))
            self.tableau.setItem(i, 6, QTableWidgetItem(f"{solde_info.solde:,.0f} F"))

            # Colonne Statut (avec couleur)
            item_statut = QTableWidgetItem(solde_info.statut)
            item_statut.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tableau.setItem(i, 7, item_statut)

        self.tableau.resizeColumnToContents(3)
        self.tableau.resizeColumnToContents(4)
        self.tableau.resizeColumnToContents(5)
        self.tableau.resizeColumnToContents(6)
        self.label_resume.setText(f"Élèves inscrits  ·  {len(eleves)} résultat(s)")

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

    def _ouvrir_tableau_bord(self):
        """Ouvre le tableau de bord."""
        from src.ui.tableau_bord import TableauBordDialog

        dialogue = TableauBordDialog(
            self.eleve_service,
            self.paiement_service,
            parent=self,
            classe_repo=self.classe_repo,
        )
        dialogue.exec()