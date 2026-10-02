"""
EduPaie — Point d'entrée de l'application.
Lance la fenêtre principale après avoir initialisé la base de données.
"""
import sys
import sqlite3
from pathlib import Path

from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

# Chemins
RACINE = Path(__file__).parent
DB_PATH = RACINE / "data" / "edupaie.db"

# Vérification de la base
if not DB_PATH.exists():
    print(f"❌ Base de données introuvable : {DB_PATH}")
    print("   Lancez d'abord : python init_db.py && python seed_db.py")
    sys.exit(1)

# Imports du projet
from src.repository import (
    Database,
    ClasseRepository,
    EleveRepository,
    PaiementRepository,
)
from src.auth import AuthService
from src.backup import BackupError, BackupService
from src.service import EleveService, PaiementService
from src.ui.login_dialog import LoginDialog
from src.ui.main_window import MainWindow


def main():
    """Point d'entrée principal."""
    app = QApplication(sys.argv)
    app.setApplicationName("EduPaie")
    app.setOrganizationName("EduPaie")

    # Appliquer le style global
    from src.ui.style import STYLE_GLOBAL
    app.setStyleSheet(STYLE_GLOBAL)
    db = Database(DB_PATH)
    db.connecter()
    try:
        auth_service = AuthService(db)
        auth_service.initialiser()
        backup_service = BackupService(db)
        backup_service.initialiser()
        dialogue_connexion = LoginDialog(auth_service, backup_service)
        if dialogue_connexion.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            chemin_sauvegarde = backup_service.creer_sauvegarde_chiffree(
                DB_PATH, dialogue_connexion.mot_de_passe_sauvegarde
            )
        except (BackupError, OSError, sqlite3.Error) as exc:
            QMessageBox.critical(
                None,
                "Sauvegarde impossible",
                "Aucune sauvegarde chiffrée n'a pu être créée. "
                "L'application ne sera pas ouverte.\n\n"
                f"Détail : {exc}",
            )
            return 1

        classe_repo = ClasseRepository(db)
        eleve_repo = EleveRepository(db)
        paiement_repo = PaiementRepository(db)

        eleve_service = EleveService(eleve_repo)
        paiement_service = PaiementService(eleve_repo, paiement_repo)

        window = MainWindow(classe_repo, eleve_service, paiement_service)
        window.show()
        print(f"Sauvegarde chiffrée créée : {chemin_sauvegarde}")
        return app.exec()
    finally:
        db.deconnecter()


if __name__ == "__main__":
    raise SystemExit(main() or 0)