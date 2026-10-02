"""Réinitialise le mot de passe administrateur sans toucher aux données scolaires."""
from getpass import getpass
from pathlib import Path

from src.auth import AuthService
from src.repository import Database


RACINE = Path(__file__).parent
DB_PATH = RACINE / "data" / "edupaie.db"


def main():
    if not DB_PATH.is_file():
        raise SystemExit(f"Base de données introuvable : {DB_PATH}")

    db = Database(DB_PATH)
    db.connecter()
    try:
        auth = AuthService(db)
        if not auth.compte_configure():
            raise SystemExit("Aucun compte administrateur configuré à réinitialiser.")

        print(
            "Cette opération remplacera le mot de passe de connexion "
            "administrateur.\n"
            "Elle ne modifie ni l'identifiant, ni les données scolaires, "
            "ni les reçus PDF."
        )
        if getpass("Pour confirmer, saisissez REINITIALISER : ") != "REINITIALISER":
            raise SystemExit("Réinitialisation annulée.")

        nouveau = getpass("Nouveau mot de passe administrateur (10 caractères minimum) : ")
        confirmation = getpass("Confirmez le nouveau mot de passe : ")
        if nouveau != confirmation:
            raise SystemExit("Les mots de passe ne correspondent pas.")

        auth.reinitialiser_mot_de_passe(nouveau)
        print(
            "Mot de passe remplacé. Connectez-vous avec le même identifiant "
            "et le nouveau mot de passe."
        )
        print(
            "Le mot de passe dédié aux sauvegardes n'a pas été modifié. "
            "S'il n'est pas configuré, EduPaie vous le demandera à la prochaine "
            "connexion."
        )
    finally:
        db.deconnecter()


if __name__ == "__main__":
    main()
