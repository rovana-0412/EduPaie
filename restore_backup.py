"""Restaure une sauvegarde EduPaie chiffrée sans écraser sans filet."""
import argparse
from getpass import getpass
from pathlib import Path

from src.backup import BackupError, BackupService
from src.repository import Database


RACINE = Path(__file__).parent
BASE_PAR_DEFAUT = RACINE / "data" / "edupaie.db"


def main():
    parser = argparse.ArgumentParser(
        description="Restaurer une sauvegarde EduPaie chiffrée."
    )
    parser.add_argument("sauvegarde", type=Path, help="Fichier .enc à restaurer")
    parser.add_argument(
        "--base",
        type=Path,
        default=BASE_PAR_DEFAUT,
        help=f"Base à remplacer (défaut : {BASE_PAR_DEFAUT})",
    )
    args = parser.parse_args()

    if not args.base.is_file():
        parser.error(f"Base à restaurer introuvable : {args.base}")

    mot_de_passe = getpass("Mot de passe dédié des sauvegardes : ")
    db = Database(args.base)
    db.connecter()
    try:
        service = BackupService(db)
        sauvegarde_securite = service.restaurer_sauvegarde_chiffree(
            args.sauvegarde, args.base, mot_de_passe
        )
    except BackupError as exc:
        parser.error(str(exc))
    finally:
        db.deconnecter()

    if sauvegarde_securite:
        print(f"Base restaurée. Sauvegarde de sécurité : {sauvegarde_securite}")
    else:
        print("Base restaurée.")


if __name__ == "__main__":
    main()
