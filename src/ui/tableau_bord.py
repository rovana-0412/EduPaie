"""Tableau de bord avec filtres, indicateurs interactifs et rapport imprimable."""
from datetime import datetime
from html import escape
from pathlib import Path

from PySide6.QtCore import QMarginsF, QSizeF, Qt
from PySide6.QtGui import QPageLayout, QPageSize, QTextDocument
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from src.constants import ordre_classe
from src.ui.statut_delegate import StatutDelegate
from src.ui.style import COULEURS


class TableauBordDialog(QDialog):
    """Vue synthétique des paiements et élèves inscrits."""

    def __init__(
        self,
        eleve_service,
        paiement_service,
        parent=None,
        classe_repo=None,
    ):
        super().__init__(parent)
        self.eleve_service = eleve_service
        self.paiement_service = paiement_service
        self.classe_repo = classe_repo
        self.classes = {}
        self.donnees = []

        self.setWindowTitle("Tableau de bord — EduPaie")
        self.resize(1140, 700)
        self.setMinimumSize(1000, 660)

        self._construire_interface()
        self._actualiser()

    def _construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(26, 22, 26, 22)

        titre = QLabel("Tableau de bord")
        titre.setObjectName("titre_principal")
        layout.addWidget(titre)

        sous_titre = QLabel(
            "Vue d'ensemble des frais de scolarité et des paiements."
        )
        sous_titre.setObjectName("sous_titre")
        layout.addWidget(sous_titre)

        layout_stats = QHBoxLayout()
        layout_stats.setSpacing(12)
        self.carte_eleves = self._creer_carte(
            "Élèves inscrits", "0", COULEURS["primaire"],
            "Afficher tous les élèves du périmètre sélectionné.",
        )
        self.carte_encaisse = self._creer_carte(
            "Montant encaissé", "0 F", COULEURS["succes"],
            "Afficher les élèves ayant effectué au moins un paiement.",
        )
        self.carte_restant = self._creer_carte(
            "Reste à recouvrer", "0 F", COULEURS["attention"],
            "Afficher les élèves ayant encore un solde à payer.",
        )
        self.carte_non_soldes = self._creer_carte(
            "Élèves non soldés", "0", COULEURS["danger"],
            "Afficher les élèves dont les frais ne sont pas soldés.",
        )
        self.carte_eleves.clicked.connect(
            lambda: self._selectionner_situation("tous")
        )
        self.carte_encaisse.clicked.connect(
            lambda: self._selectionner_situation("avec_paiement")
        )
        self.carte_restant.clicked.connect(
            lambda: self._selectionner_situation("reste_du")
        )
        self.carte_non_soldes.clicked.connect(
            lambda: self._selectionner_situation("reste_du")
        )
        for carte in (
            self.carte_eleves,
            self.carte_encaisse,
            self.carte_restant,
            self.carte_non_soldes,
        ):
            layout_stats.addWidget(carte)
        layout.addLayout(layout_stats)

        cadre_filtres = QFrame()
        cadre_filtres.setObjectName("surface")
        layout_filtres = QHBoxLayout(cadre_filtres)
        layout_filtres.setContentsMargins(14, 10, 14, 10)
        layout_filtres.setSpacing(10)

        label_classe = QLabel("Classe")
        self.filtre_classe = QComboBox()
        self.filtre_classe.setMinimumWidth(155)
        self.filtre_classe.addItem("Toutes les classes", None)

        label_annee = QLabel("Année scolaire")
        self.filtre_annee = QComboBox()
        self.filtre_annee.setMinimumWidth(145)
        self.filtre_annee.addItem("Toutes les années", None)

        label_situation = QLabel("Situation")
        self.filtre_situation = QComboBox()
        self.filtre_situation.setMinimumWidth(180)
        self.filtre_situation.addItem("Toutes les situations", "tous")
        self.filtre_situation.addItem("Soldé", "Soldé")
        self.filtre_situation.addItem(
            "Partiellement payé", "Partiellement payé"
        )
        self.filtre_situation.addItem("Non payé", "Non payé")
        self.filtre_situation.addItem("Avec paiement", "avec_paiement")
        self.filtre_situation.addItem("Solde à payer", "reste_du")

        self.bouton_actualiser = QPushButton("Actualiser")
        self.bouton_actualiser.clicked.connect(self._actualiser)
        self.filtre_classe.currentIndexChanged.connect(
            self._actualiser_affichage
        )
        self.filtre_annee.currentIndexChanged.connect(
            self._actualiser_affichage
        )
        self.filtre_situation.currentIndexChanged.connect(
            self._actualiser_affichage
        )

        layout_filtres.addWidget(label_classe)
        layout_filtres.addWidget(self.filtre_classe)
        layout_filtres.addWidget(label_annee)
        layout_filtres.addWidget(self.filtre_annee)
        layout_filtres.addWidget(label_situation)
        layout_filtres.addWidget(self.filtre_situation)
        layout_filtres.addStretch()
        layout_filtres.addWidget(self.bouton_actualiser)
        layout.addWidget(cadre_filtres)

        self.label_resultats = QLabel("Situation des élèves")
        self.label_resultats.setObjectName("titre_section")
        layout.addWidget(self.label_resultats)

        self.tableau = QTableWidget()
        self.tableau.setColumnCount(8)
        self.tableau.setHorizontalHeaderLabels(
            [
                "Nom",
                "Prénom",
                "Classe",
                "Année scolaire",
                "Montant dû",
                "Payé",
                "Solde",
                "Statut",
            ]
        )
        self.tableau.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tableau.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.tableau.setAlternatingRowColors(True)
        self.tableau.verticalHeader().setVisible(False)
        self.tableau.verticalHeader().setDefaultSectionSize(40)
        header = self.tableau.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for column in range(2, 8):
            header.setSectionResizeMode(
                column, QHeaderView.ResizeMode.ResizeToContents
            )
        self.tableau.setItemDelegateForColumn(7, StatutDelegate(self.tableau))
        layout.addWidget(self.tableau)

        actions = QHBoxLayout()
        self.bouton_exporter = QPushButton("Exporter le rapport PDF")
        self.bouton_exporter.setObjectName("btn_primaire")
        self.bouton_exporter.clicked.connect(self._choisir_export_pdf)
        self.bouton_imprimer = QPushButton("Imprimer le rapport")
        self.bouton_imprimer.clicked.connect(self._imprimer)
        bouton_fermer = QPushButton("Fermer")
        bouton_fermer.clicked.connect(self.accept)

        actions.addWidget(self.bouton_exporter)
        actions.addWidget(self.bouton_imprimer)
        actions.addStretch()
        actions.addWidget(bouton_fermer)
        layout.addLayout(actions)

    def _creer_carte(self, titre, valeur, couleur, infobulle):
        carte = QPushButton()
        carte.setObjectName("carte_stat")
        carte.setToolTip(infobulle)
        carte.setAccessibleName(f"{titre}. {infobulle}")
        carte.setFixedHeight(130)
        carte.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        carte.setCursor(Qt.CursorShape.PointingHandCursor)
        carte.setStyleSheet(
            f"""
            QPushButton#carte_stat {{
                text-align: left;
                background-color: {COULEURS['blanc']};
                border: 2px solid {couleur};
                border-radius: 10px;
                min-height: 130px;
                max-height: 130px;
                padding: 10px;
            }}
            QPushButton#carte_stat:hover {{
                background-color: #f8fafc;
            }}
            QPushButton#carte_stat:pressed {{
                background-color: #edf3fb;
            }}
            """
        )
        contenu = QVBoxLayout(carte)
        contenu.setContentsMargins(8, 8, 8, 8)
        contenu.setSpacing(9)

        label_titre = QLabel(titre)
        label_titre.setObjectName("carte_titre")
        label_titre.setStyleSheet("font-size: 14px;")
        label_titre.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        label_valeur = QLabel(valeur)
        label_valeur.setObjectName("carte_valeur")
        label_valeur.setStyleSheet(
            f"color: {couleur}; font-size: 30px; font-weight: 700;"
        )
        label_valeur.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        contenu.addWidget(label_titre)
        contenu.addWidget(label_valeur)
        contenu.addStretch()
        return carte

    @staticmethod
    def _maj_carte(carte, valeur):
        label = carte.findChild(QLabel, "carte_valeur")
        if label:
            label.setText(valeur)

    def _actualiser(self):
        """Recharge les données, les classes et les années depuis la base."""
        classe_selectionnee = self.filtre_classe.currentData()
        annee_selectionnee = self.filtre_annee.currentData()

        eleves = self.eleve_service.lister_tous()
        if self.classe_repo is not None:
            classes = self.classe_repo.lister_toutes()
            self.classes = {
                classe.id_classe: classe.nom_classe for classe in classes
            }
        else:
            self.classes = {
                eleve.id_classe: f"Classe {eleve.id_classe}" for eleve in eleves
            }

        self.donnees = [
            (eleve, self.paiement_service.calculer_solde(eleve.id_eleve))
            for eleve in eleves
        ]
        self._reconstruire_filtres(classe_selectionnee, annee_selectionnee)
        self._actualiser_affichage()

    def _reconstruire_filtres(self, classe_selectionnee, annee_selectionnee):
        self.filtre_classe.blockSignals(True)
        self.filtre_classe.clear()
        self.filtre_classe.addItem("Toutes les classes", None)
        for id_classe, nom_classe in sorted(
            self.classes.items(), key=lambda element: ordre_classe(element[1])
        ):
            self.filtre_classe.addItem(nom_classe, id_classe)
        index_classe = self.filtre_classe.findData(classe_selectionnee)
        self.filtre_classe.setCurrentIndex(max(index_classe, 0))
        self.filtre_classe.blockSignals(False)

        annees = sorted(
            {eleve.annee_scolaire for eleve, _ in self.donnees},
            reverse=True,
        )
        self.filtre_annee.blockSignals(True)
        self.filtre_annee.clear()
        self.filtre_annee.addItem("Toutes les années", None)
        for annee in annees:
            self.filtre_annee.addItem(annee, annee)
        index_annee = self.filtre_annee.findData(annee_selectionnee)
        self.filtre_annee.setCurrentIndex(max(index_annee, 0))
        self.filtre_annee.blockSignals(False)

    def _selectionner_situation(self, situation):
        index = self.filtre_situation.findData(situation)
        if index >= 0:
            self.filtre_situation.setCurrentIndex(index)

    def _donnees_perimetre(self):
        id_classe = self.filtre_classe.currentData()
        annee = self.filtre_annee.currentData()
        return [
            (eleve, solde)
            for eleve, solde in self.donnees
            if (id_classe is None or eleve.id_classe == id_classe)
            and (annee is None or eleve.annee_scolaire == annee)
        ]

    def _actualiser_affichage(self):
        """Recalcule les indicateurs et filtre la liste affichée."""
        perimetre = self._donnees_perimetre()
        total_encaisse = sum(solde.total_paye for _, solde in perimetre)
        total_restant = sum(max(0, solde.solde) for _, solde in perimetre)
        nb_non_soldes = sum(
            solde.statut != "Soldé" for _, solde in perimetre
        )

        self._maj_carte(self.carte_eleves, str(len(perimetre)))
        self._maj_carte(
            self.carte_encaisse, f"{total_encaisse:,.0f} F CFA"
        )
        self._maj_carte(
            self.carte_restant, f"{total_restant:,.0f} F CFA"
        )
        self._maj_carte(self.carte_non_soldes, str(nb_non_soldes))

        situation = self.filtre_situation.currentData()
        lignes = [
            (eleve, solde)
            for eleve, solde in perimetre
            if self._correspond_situation(situation, solde)
        ]
        self.tableau.setRowCount(len(lignes))
        for index, (eleve, solde) in enumerate(lignes):
            valeurs = (
                eleve.nom,
                eleve.prenom,
                self.classes.get(eleve.id_classe, f"Classe {eleve.id_classe}"),
                eleve.annee_scolaire,
                f"{solde.total_du:,.0f} F",
                f"{solde.total_paye:,.0f} F",
                f"{solde.solde:,.0f} F",
            )
            for colonne, valeur in enumerate(valeurs):
                self.tableau.setItem(
                    index, colonne, QTableWidgetItem(str(valeur))
                )
            item_statut = QTableWidgetItem(solde.statut)
            item_statut.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tableau.setItem(index, 7, item_statut)

        self.label_resultats.setText(
            f"Situation des élèves  ·  {len(lignes)} résultat(s)"
        )
        self.lignes_visibles = lignes

    @staticmethod
    def _correspond_situation(situation, solde):
        if situation in (None, "tous"):
            return True
        if situation == "avec_paiement":
            return solde.total_paye > 0
        if situation == "reste_du":
            return solde.solde > 0
        return solde.statut == situation

    def _construire_rapport_html(self):
        """Produit le HTML commun à l'export PDF et à l'impression."""
        filtres = [
            f"Classe : {self.filtre_classe.currentText()}",
            f"Année scolaire : {self.filtre_annee.currentText()}",
            f"Situation : {self.filtre_situation.currentText()}",
        ]
        entetes = (
            "Nom",
            "Prénom",
            "Classe",
            "Année scolaire",
            "Montant dû",
            "Payé",
            "Solde",
            "Statut",
        )
        lignes_html = []
        for eleve, solde in self.lignes_visibles:
            valeurs = (
                eleve.nom,
                eleve.prenom,
                self.classes.get(eleve.id_classe, f"Classe {eleve.id_classe}"),
                eleve.annee_scolaire,
                f"{solde.total_du:,.0f} F CFA",
                f"{solde.total_paye:,.0f} F CFA",
                f"{solde.solde:,.0f} F CFA",
                solde.statut,
            )
            cellules = "".join(
                f"<td>{escape(str(valeur))}</td>" for valeur in valeurs
            )
            lignes_html.append(f"<tr>{cellules}</tr>")

        if not lignes_html:
            lignes_html.append(
                f'<tr><td colspan="{len(entetes)}">Aucun élève pour ces filtres.</td></tr>'
            )

        titres = "".join(f"<th>{escape(entete)}</th>" for entete in entetes)
        liste_filtres = " &nbsp; | &nbsp; ".join(
            escape(valeur) for valeur in filtres
        )
        perimetre = self._donnees_perimetre()
        total_encaisse = sum(solde.total_paye for _, solde in perimetre)
        total_restant = sum(max(0, solde.solde) for _, solde in perimetre)
        non_soldes = sum(solde.statut != "Soldé" for _, solde in perimetre)
        return f"""
        <html><head><meta charset="utf-8"/>
        <style>
            body {{ font-family: Arial, sans-serif; color: #172033; font-size: 9pt; }}
            h1 {{ color: #1e40af; font-size: 20pt; margin-bottom: 4px; }}
            .meta {{ color: #64748b; font-size: 8pt; margin-bottom: 14px; }}
            .stats {{ margin: 10px 0 14px; padding: 8px; background: #f8fafc; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ background: #eff6ff; color: #1e3a8a; text-align: left; }}
            th, td {{ border: 1px solid #dbe3ee; padding: 6px 5px; }}
            tr:nth-child(even) {{ background: #f8fafc; }}
        </style></head><body>
        <h1>EduPaie — Rapport du tableau de bord</h1>
        <div class="meta">Généré le {datetime.now().strftime("%d/%m/%Y à %H:%M")}
        <br/>{liste_filtres}
        <br/>{len(self.lignes_visibles)} élève(s) dans le rapport</div>
        <div class="stats">
        Élèves inscrits : {len(perimetre)} &nbsp; | &nbsp;
        Encaissé : {total_encaisse:,.0f} F CFA &nbsp; | &nbsp;
        Reste à recouvrer : {total_restant:,.0f} F CFA &nbsp; | &nbsp;
        Non soldés : {non_soldes}
        </div>
        <table><thead><tr>{titres}</tr></thead>
        <tbody>{"".join(lignes_html)}</tbody></table>
        </body></html>
        """

    def _preparer_imprimante(self, imprimante):
        imprimante.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        imprimante.setPageOrientation(QPageLayout.Orientation.Landscape)
        imprimante.setPageMargins(
            QMarginsF(10, 10, 10, 10), QPageLayout.Unit.Millimeter
        )
        document = QTextDocument(self)
        document.setHtml(self._construire_rapport_html())
        largeur = imprimante.pageLayout().paintRect(
            QPageLayout.Unit.Point
        ).width()
        document.setPageSize(
            QSizeF(
                largeur,
                imprimante.pageLayout().paintRect(
                    QPageLayout.Unit.Point
                ).height(),
            )
        )
        document.setTextWidth(largeur)
        return document

    def _choisir_export_pdf(self):
        nom = f"rapport_edupaie_{datetime.now():%Y%m%d_%H%M%S}.pdf"
        chemin, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter le rapport PDF",
            str(Path.home() / nom),
            "Fichier PDF (*.pdf)",
        )
        if not chemin:
            return
        if not chemin.lower().endswith(".pdf"):
            chemin += ".pdf"
        try:
            self._ecrire_pdf(chemin)
        except (OSError, RuntimeError) as exc:
            QMessageBox.critical(
                self, "Export impossible", f"Impossible de créer le PDF :\n{exc}"
            )
            return
        QMessageBox.information(
            self, "Rapport exporté", f"Le rapport PDF a été enregistré :\n{chemin}"
        )

    def _ecrire_pdf(self, chemin):
        imprimante = QPrinter(QPrinter.PrinterMode.HighResolution)
        imprimante.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        imprimante.setOutputFileName(str(chemin))
        document = self._preparer_imprimante(imprimante)
        document.print_(imprimante)
        if not Path(chemin).is_file() or Path(chemin).stat().st_size == 0:
            raise OSError("Le fichier PDF n'a pas été créé.")

    def _imprimer(self):
        imprimante = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialogue = QPrintDialog(imprimante, self)
        if dialogue.exec() != QPrintDialog.DialogCode.Accepted:
            return
        try:
            document = self._preparer_imprimante(imprimante)
            document.print_(imprimante)
        except RuntimeError as exc:
            QMessageBox.critical(
                self, "Impression impossible", f"Impossible d'imprimer :\n{exc}"
            )
