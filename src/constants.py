"""Constantes de configuration scolaire de l'application."""

ANNEE_SCOLAIRE_DEFAUT = "2026-2027"

CLASSES_ETABLISSEMENT = (
    "6ème A",
    "6ème B",
    "5ème A",
    "5ème B",
    "4ème A",
    "4ème B",
    "3ème A",
    "3ème B",
    "2nd A4",
    "2nd S",
    "1ère A4",
    "1ère D",
    "1ère C",
    "Tle A4",
    "Tle D",
    "Tle C",
)


def niveau_de_classe(nom_classe: str) -> str:
    """Extrait le niveau scolaire du nom complet de classe."""
    return nom_classe.rsplit(" ", 1)[0]


def ordre_classe(nom_classe: str) -> tuple:
    """Trie selon l'ordre scolaire défini, puis les classes personnalisées."""
    try:
        return (0, CLASSES_ETABLISSEMENT.index(nom_classe))
    except ValueError:
        return (1, nom_classe.casefold())
