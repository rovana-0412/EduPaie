"""
EduPaie — Point d'entrée de l'application.
Lance la fenêtre principale après avoir initialisé la base de données.
"""
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

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
from src.service import EleveService, PaiementService
from src.ui.main_window import MainWindow


def main():
    """Point d'entrée principal."""
    # 1. Créer l'application Qt
    app = QApplication(sys.argv)
    app.setApplicationName("EduPaie")
    app.setOrganizationName("EduPaie")

    # 2. Connecter à la base de données
    db = Database(DB_PATH)
    db.connecter()

    # 3. Créer les repositories
    classe_repo = ClasseRepository(db)
    eleve_repo = EleveRepository(db)
    paiement_repo = PaiementRepository(db)

    # 4. Créer les services
    eleve_service = EleveService(eleve_repo)
    paiement_service = PaiementService(eleve_repo, paiement_repo)

    # 5. Créer et afficher la fenêtre principale
    window = MainWindow(classe_repo, eleve_service, paiement_service)
    window.show()

    # 6. Lancer la boucle d'événements
    code_retour = app.exec()

    # 7. Fermer proprement la connexion
    db.deconnecter()
    sys.exit(code_retour)


if __name__ == "__main__":
    main()