"""
EduPaie — Formulaire d'ajout/modification d'élève.
Boîte de dialogue modale pour saisir les informations d'un élève.
"""
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
)
from PySide6.QtCore import Qt

from src.constants import ANNEE_SCOLAIRE_DEFAUT
from src.date_utils import valider_date_iso
from src.models import Eleve


class EleveForm(QDialog):
    """Boîte de dialogue pour ajouter ou modifier un élève."""

    def __init__(self, classes: list, eleve: Eleve = None, parent=None):
        """
        Args:
            classes : liste des objets Classe disponibles
            eleve   : si fourni, on est en mode "modification"
                      si None, on est en mode "ajout"
            parent  : widget parent (fenêtre principale)
        """
        super().__init__(parent)
        self.classes = classes
        self.eleve = eleve

        # Titre selon le mode
        if eleve is None:
            self.setWindowTitle("Ajouter un élève")
        else:
            self.setWindowTitle(f"Modifier : {eleve.nom_complet}")

        self.setMinimumWidth(500)

        # Construire l'interface
        self._construire_interface()

        # Pré-remplir si modification
        if eleve:
            self._remplir_champs()

    def _construire_interface(self):
        """Construit les champs du formulaire."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(16)

        # ===== Titre =====
        titre = QLabel(
            "Ajouter un élève" if self.eleve is None else "Modifier les informations"
        )
        titre.setObjectName("titre_principal")
        layout.addWidget(titre)
        description = QLabel("Renseignez les informations scolaires et personnelles.")
        description.setObjectName("sous_titre")
        layout.addWidget(description)

        # ===== Formulaire =====
        form = QFormLayout()
        form.setVerticalSpacing(12)
        form.setHorizontalSpacing(16)

        # Nom
        self.champ_nom = QLineEdit()
        self.champ_nom.setPlaceholderText("Ex : KOUASSI")
        form.addRow("Nom * :", self.champ_nom)

        # Prénom
        self.champ_prenom = QLineEdit()
        self.champ_prenom.setPlaceholderText("Ex : Ami")
        form.addRow("Prénom * :", self.champ_prenom)

        # Date de naissance
        self.champ_date = QLineEdit()
        self.champ_date.setPlaceholderText("Ex : 2014-03-15")
        form.addRow("Date de naissance * :", self.champ_date)

        # Année scolaire
        self.champ_annee = QLineEdit()
        self.champ_annee.setPlaceholderText(
            f"Ex : {ANNEE_SCOLAIRE_DEFAUT}"
        )
        self.champ_annee.setText(ANNEE_SCOLAIRE_DEFAUT)
        form.addRow("Année scolaire * :", self.champ_annee)

        # Montant dû
        self.champ_montant = QDoubleSpinBox()
        self.champ_montant.setRange(0, 10_000_000)
        self.champ_montant.setDecimals(0)
        self.champ_montant.setSingleStep(5000)
        self.champ_montant.setSuffix(" F CFA")
        self.champ_montant.setValue(150000)  # valeur par défaut
        form.addRow("Montant total dû * :", self.champ_montant)

        # Classe
        self.champ_classe = QComboBox()
        self.champ_classe.addItem("-- Choisir une classe --", None)
        for classe in self.classes:
            self.champ_classe.addItem(
                f"{classe.nom_classe} ({classe.niveau})",
                classe.id_classe
            )
        form.addRow("Classe * :", self.champ_classe)

        layout.addLayout(form)

        # ===== Boutons =====
        layout_boutons = QHBoxLayout()

        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(self.reject)

        bouton_valider = QPushButton("Valider")
        bouton_valider.setObjectName("btn_primaire")
        bouton_valider.setDefault(True)
        bouton_valider.clicked.connect(self._valider)

        layout_boutons.addStretch()
        layout_boutons.addWidget(bouton_annuler)
        layout_boutons.addWidget(bouton_valider)

        layout.addLayout(layout_boutons)

    def _remplir_champs(self):
        """Pré-remplit les champs en mode modification."""
        self.champ_nom.setText(self.eleve.nom)
        self.champ_prenom.setText(self.eleve.prenom)
        self.champ_date.setText(self.eleve.date_naissance)
        self.champ_annee.setText(self.eleve.annee_scolaire)
        self.champ_montant.setValue(self.eleve.montant_total_du)

        # Sélectionner la bonne classe
        index = self.champ_classe.findData(self.eleve.id_classe)
        if index >= 0:
            self.champ_classe.setCurrentIndex(index)

    def _valider(self):
        """Valide les champs avant de fermer."""
        # Récupérer les valeurs
        nom = self.champ_nom.text().strip()
        prenom = self.champ_prenom.text().strip()
        date_naissance = self.champ_date.text().strip()
        annee_scolaire = self.champ_annee.text().strip()
        montant = self.champ_montant.value()
        id_classe = self.champ_classe.currentData()

        # Validations
        if not nom:
            QMessageBox.warning(self, "Champ manquant", "Le nom est obligatoire.")
            self.champ_nom.setFocus()
            return
        if not prenom:
            QMessageBox.warning(self, "Champ manquant", "Le prénom est obligatoire.")
            self.champ_prenom.setFocus()
            return
        if not date_naissance:
            QMessageBox.warning(self, "Champ manquant", "La date de naissance est obligatoire.")
            self.champ_date.setFocus()
            return
        try:
            valider_date_iso(date_naissance, "La date de naissance")
        except ValueError:
            QMessageBox.warning(
                self, "Format invalide",
                "Saisissez une date réelle au format AAAA-MM-JJ "
                "(ex. : 2014-03-15)."
            )
            self.champ_date.setFocus()
            return

        if not annee_scolaire:
            QMessageBox.warning(self, "Champ manquant", "L'année scolaire est obligatoire.")
            self.champ_annee.setFocus()
            return
        if montant <= 0:
            QMessageBox.warning(self, "Montant invalide", "Le montant doit être supérieur à 0.")
            self.champ_montant.setFocus()
            return
        if id_classe is None:
            QMessageBox.warning(self, "Champ manquant", "Veuillez choisir une classe.")
            self.champ_classe.setFocus()
            return

        # Tout est OK → on ferme avec succès
        self.accept()

    def get_eleve(self) -> Eleve:
        """Retourne un objet Eleve à partir des champs saisis."""
        return Eleve(
            id_eleve=self.eleve.id_eleve if self.eleve else None,
            nom=self.champ_nom.text().strip(),
            prenom=self.champ_prenom.text().strip(),
            date_naissance=self.champ_date.text().strip(),
            annee_scolaire=self.champ_annee.text().strip(),
            montant_total_du=self.champ_montant.value(),
            id_classe=self.champ_classe.currentData(),
        )