"""Écran de création du compte initial et de connexion."""
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
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

        (
            self.champ_mot_de_passe,
            champ_mot_de_passe_widget,
            self.bouton_voir_mot_de_passe,
        ) = self._creer_champ_mot_de_passe("Au moins 10 caractères")
        self.champ_mot_de_passe.returnPressed.connect(self._soumettre)
        formulaire.addRow("Mot de passe :", champ_mot_de_passe_widget)

        self.champ_confirmation = None
        self.bouton_voir_confirmation = None
        if self.creation_initiale:
            (
                self.champ_confirmation,
                confirmation_widget,
                self.bouton_voir_confirmation,
            ) = self._creer_champ_mot_de_passe("Confirmez le mot de passe")
            self.champ_confirmation.returnPressed.connect(self._soumettre)
            formulaire.addRow("Confirmer le mot de passe :", confirmation_widget)

        (
            self.champ_mot_de_passe_sauvegarde,
            mot_de_passe_sauvegarde_widget,
            self.bouton_voir_mot_de_passe_sauvegarde,
        ) = self._creer_champ_mot_de_passe("Au moins 12 caractères")
        self.champ_mot_de_passe_sauvegarde.returnPressed.connect(self._soumettre)
        formulaire.addRow(
            "Mot de passe de sauvegarde :",
            mot_de_passe_sauvegarde_widget,
        )

        self.champ_confirmation_sauvegarde = None
        self.bouton_voir_confirmation_sauvegarde = None
        if self.configuration_sauvegarde:
            (
                self.champ_confirmation_sauvegarde,
                confirmation_sauvegarde_widget,
                self.bouton_voir_confirmation_sauvegarde,
            ) = self._creer_champ_mot_de_passe(
                "Confirmez le mot de passe de sauvegarde"
            )
            self.champ_confirmation_sauvegarde.returnPressed.connect(
                self._soumettre
            )
            formulaire.addRow(
                "Confirmer le mot de passe de sauvegarde :",
                confirmation_sauvegarde_widget,
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

    def _creer_champ_mot_de_passe(self, placeholder):
        champ = QLineEdit()
        champ.setEchoMode(QLineEdit.EchoMode.Password)
        champ.setPlaceholderText(placeholder)

        bouton = QToolButton()
        bouton.setCheckable(True)
        bouton.setAutoRaise(True)
        bouton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        bouton.setFixedSize(34, 34)
        bouton.setIconSize(QSize(20, 20))
        bouton.setStyleSheet(
            """
            QToolButton#btn_voir_mot_de_passe {
                border: none;
                border-radius: 5px;
                padding: 4px;
            }
            QToolButton#btn_voir_mot_de_passe:hover {
                background-color: #f1f5f9;
            }
            """
        )
        icone_visible = self._creer_icone_visibilite(masquer=False)
        icone_masquee = self._creer_icone_visibilite(masquer=True)
        bouton.setIcon(icone_masquee)
        bouton.setToolTip("Afficher le mot de passe")
        bouton.setAccessibleName("Afficher le mot de passe")
        bouton.setObjectName("btn_voir_mot_de_passe")

        def definir_visibilite(visible):
            champ.setEchoMode(
                QLineEdit.EchoMode.Normal
                if visible
                else QLineEdit.EchoMode.Password
            )
            bouton.setIcon(icone_visible if visible else icone_masquee)
            libelle = "Masquer le mot de passe" if visible else "Afficher le mot de passe"
            bouton.setToolTip(libelle)
            bouton.setAccessibleName(libelle)

        bouton.toggled.connect(definir_visibilite)

        conteneur = QWidget()
        ligne = QHBoxLayout(conteneur)
        ligne.setContentsMargins(0, 0, 0, 0)
        ligne.setSpacing(4)
        ligne.addWidget(champ, 1)
        ligne.addWidget(bouton)
        return champ, conteneur, bouton

    @staticmethod
    def _creer_icone_visibilite(masquer):
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#64748b"), 1.7))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        oeil = QPainterPath()
        oeil.moveTo(2.5, 12)
        oeil.cubicTo(7, 5.5, 17, 5.5, 21.5, 12)
        oeil.cubicTo(17, 18.5, 7, 18.5, 2.5, 12)
        painter.drawPath(oeil)

        painter.drawEllipse(9.2, 9.2, 5.6, 5.6)
        painter.setBrush(QColor("#64748b"))
        painter.drawEllipse(11, 11, 2, 2)

        if masquer:
            painter.setPen(QPen(QColor("#64748b"), 1.8, Qt.PenStyle.SolidLine,
                                Qt.PenCapStyle.RoundCap))
            painter.drawLine(4, 20, 20, 4)

        painter.end()
        return QIcon(pixmap)

    def _soumettre(self):
        identifiant = self.champ_identifiant.text()
        mot_de_passe = self.champ_mot_de_passe.text()
        mot_de_passe_sauvegarde = self.champ_mot_de_passe_sauvegarde.text()

        if not identifiant.strip():
            self.message.setText("Saisissez votre identifiant.")
            self.champ_identifiant.setFocus()
            return

        if not mot_de_passe:
            self.message.setText("Saisissez votre mot de passe de connexion.")
            self.champ_mot_de_passe.setFocus()
            return

        if self.creation_initiale:
            if self.champ_confirmation.text() != mot_de_passe:
                self.message.setText("Les mots de passe ne correspondent pas.")
                self.champ_confirmation.clear()
                self.champ_confirmation.setFocus()
                return
        elif not self.auth_service.verifier(identifiant, mot_de_passe):
            self.message.setText(
                "Identifiant ou mot de passe incorrect. Vérifiez votre saisie "
                "et la disposition du clavier."
            )
            self.champ_mot_de_passe.setFocus()
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
            if len(mot_de_passe_sauvegarde) < (
                self.backup_service.LONGUEUR_MIN_MOT_DE_PASSE
            ):
                self.message.setText(
                    "Le mot de passe de sauvegarde doit contenir au moins "
                    f"{self.backup_service.LONGUEUR_MIN_MOT_DE_PASSE} caractères."
                )
                self.champ_mot_de_passe_sauvegarde.setFocus()
                return

        if mot_de_passe_sauvegarde == mot_de_passe:
            self.message.setText(
                "Le mot de passe de sauvegarde doit être différent "
                "du mot de passe de connexion."
            )
            self.champ_mot_de_passe_sauvegarde.clear()
            self.champ_mot_de_passe_sauvegarde.setFocus()
            return

        if self.creation_initiale:
            try:
                self.auth_service.creer_compte(identifiant, mot_de_passe)
            except ValueError as exc:
                self.message.setText(str(exc))
                return

        if self.configuration_sauvegarde:
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
