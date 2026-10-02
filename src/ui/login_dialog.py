"""Écran de création du compte initial et de connexion."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from src.auth import AuthService
from src.backup import BackupService


class LoginDialog(QDialog):
    """Demande la création du premier compte ou l'authentification."""

    def __init__(
        self,
        auth_service: AuthService,
        backup_service: BackupService,
        parent=None,
    ):
        super().__init__(parent)
        self.auth_service = auth_service
        self.backup_service = backup_service
        self.creation_initiale = not auth_service.compte_configure()
        self.configuration_sauvegarde = not backup_service.mot_de_passe_configure()
        self.mot_de_passe_sauvegarde = None

        if self.creation_initiale:
            self.setWindowTitle("Configurer EduPaie")
        else:
            self.setWindowTitle("Connexion — EduPaie")
        self.setMinimumWidth(430)

        self._construire_interface()

    def _construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 30, 34, 28)
        layout.setSpacing(16)

        titre = QLabel("EduPaie")
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titre.setObjectName("titre_principal")
        layout.addWidget(titre)

        if self.creation_initiale:
            description = QLabel(
                "Créez le compte administrateur et un mot de passe dédié "
                "aux sauvegardes chiffrées."
            )
        else:
            description = QLabel(
                "Connectez-vous et saisissez le mot de passe dédié aux "
                "sauvegardes chiffrées."
            )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setObjectName("sous_titre")
        layout.addWidget(description)

        formulaire = QFormLayout()
        formulaire.setVerticalSpacing(12)
        formulaire.setHorizontalSpacing(12)
        self.champ_identifiant = QLineEdit()
        self.champ_identifiant.setMaxLength(AuthService.LONGUEUR_MAX_IDENTIFIANT)
        self.champ_identifiant.setPlaceholderText("Au moins 3 caractères")
        formulaire.addRow("Identifiant :", self.champ_identifiant)

        self.champ_mot_de_passe = QLineEdit()
        self.champ_mot_de_passe.setEchoMode(QLineEdit.EchoMode.Password)
        self.champ_mot_de_passe.setPlaceholderText("Au moins 10 caractères")
        self.champ_mot_de_passe.returnPressed.connect(self._soumettre)
        formulaire.addRow("Mot de passe :", self.champ_mot_de_passe)

        self.champ_confirmation = None
        if self.creation_initiale:
            self.champ_confirmation = QLineEdit()
            self.champ_confirmation.setEchoMode(QLineEdit.EchoMode.Password)
            self.champ_confirmation.returnPressed.connect(self._soumettre)
            formulaire.addRow("Confirmer le mot de passe :", self.champ_confirmation)

        self.champ_mot_de_passe_sauvegarde = QLineEdit()
        self.champ_mot_de_passe_sauvegarde.setEchoMode(QLineEdit.EchoMode.Password)
        self.champ_mot_de_passe_sauvegarde.setPlaceholderText("Au moins 12 caractères")
        self.champ_mot_de_passe_sauvegarde.returnPressed.connect(self._soumettre)
        formulaire.addRow(
            "Mot de passe de sauvegarde :",
            self.champ_mot_de_passe_sauvegarde,
        )

        self.champ_confirmation_sauvegarde = None
        if self.configuration_sauvegarde:
            self.champ_confirmation_sauvegarde = QLineEdit()
            self.champ_confirmation_sauvegarde.setEchoMode(
                QLineEdit.EchoMode.Password
            )
            self.champ_confirmation_sauvegarde.returnPressed.connect(
                self._soumettre
            )
            formulaire.addRow(
                "Confirmer le mot de passe de sauvegarde :",
                self.champ_confirmation_sauvegarde,
            )

        layout.addLayout(formulaire)

        self.message = QLabel()
        self.message.setWordWrap(True)
        self.message.setObjectName("message_erreur")
        layout.addWidget(self.message)

        self.bouton_valider = QPushButton(
            "Créer le compte" if self.creation_initiale else "Se connecter"
        )
        self.bouton_valider.setObjectName("btn_primaire")
        self.bouton_valider.clicked.connect(self._soumettre)
        layout.addWidget(self.bouton_valider)

        self.champ_identifiant.setFocus()

    def _soumettre(self):
        identifiant = self.champ_identifiant.text()
        mot_de_passe = self.champ_mot_de_passe.text()
        mot_de_passe_sauvegarde = self.champ_mot_de_passe_sauvegarde.text()

        if self.creation_initiale:
            if self.champ_confirmation.text() != mot_de_passe:
                self.message.setText("Les mots de passe ne correspondent pas.")
                self.champ_confirmation.clear()
                self.champ_confirmation.setFocus()
                return
            try:
                self.auth_service.creer_compte(identifiant, mot_de_passe)
            except ValueError as exc:
                self.message.setText(str(exc))
                return
        elif not self.auth_service.verifier(identifiant, mot_de_passe):
            self.message.setText("Identifiant ou mot de passe incorrect.")
            self.champ_mot_de_passe.clear()
            self.champ_mot_de_passe.setFocus()
            return

        if mot_de_passe_sauvegarde == mot_de_passe:
            self.message.setText(
                "Le mot de passe de sauvegarde doit être différent "
                "du mot de passe de connexion."
            )
            self.champ_mot_de_passe_sauvegarde.clear()
            self.champ_mot_de_passe_sauvegarde.setFocus()
            return

        if self.configuration_sauvegarde:
            if (
                self.champ_confirmation_sauvegarde.text()
                != mot_de_passe_sauvegarde
            ):
                self.message.setText(
                    "Les mots de passe de sauvegarde ne correspondent pas."
                )
                self.champ_confirmation_sauvegarde.clear()
                self.champ_confirmation_sauvegarde.setFocus()
                return
            try:
                self.backup_service.configurer_mot_de_passe(
                    mot_de_passe_sauvegarde
                )
            except ValueError as exc:
                self.message.setText(str(exc))
                return
        elif not self.backup_service.verifier_mot_de_passe(
            mot_de_passe_sauvegarde
        ):
            self.message.setText("Le mot de passe de sauvegarde est incorrect.")
            self.champ_mot_de_passe_sauvegarde.clear()
            self.champ_mot_de_passe_sauvegarde.setFocus()
            return

        self.mot_de_passe_sauvegarde = mot_de_passe_sauvegarde
        self.accept()
