"""Validation stricte des dates ISO utilisées par les services métier."""
from datetime import date


def valider_date_iso(valeur: str, libelle: str = "Date") -> date:
    """Retourne la date si elle respecte exactement le format AAAA-MM-JJ."""
    try:
        date_validee = date.fromisoformat(valeur)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{libelle} doit être une date valide au format AAAA-MM-JJ."
        ) from exc

    if date_validee.isoformat() != valeur:
        raise ValueError(f"{libelle} doit être au format AAAA-MM-JJ.")
    return date_validee
