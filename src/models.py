"""
EduPaie — Modèles de données (dataclasses).
Représentent les objets métier : Classe, Eleve, Paiement.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Classe:
    """Représente une classe d'élèves."""
    id_classe: Optional[int]
    nom_classe: str
    niveau: str
    annee_scolaire: str


@dataclass
class Eleve:
    """Représente un élève inscrit."""
    id_eleve: Optional[int]
    nom: str
    prenom: str
    date_naissance: str          # Format ISO : YYYY-MM-DD
    annee_scolaire: str          # Ex : "2026-2027"
    montant_total_du: float      # Frais de scolarité personnalisés
    id_classe: int

    @property
    def nom_complet(self) -> str:
        """Retourne le nom complet (pratique pour l'affichage)."""
        return f"{self.nom} {self.prenom}"


@dataclass
class Paiement:
    """Représente un paiement effectué par un élève."""
    id_paiement: Optional[int]
    date_paiement: str           # Format ISO : YYYY-MM-DD
    montant: float
    mode_paiement: str           # Espèces, Chèque, Virement, Mobile Money
    numero_recu: str             # Format : REC-AAAA-NNNNNN
    id_eleve: int


@dataclass
class SoldeEleve:
    """Vue calculée : solde d'un élève (non stocké en base)."""
    eleve: Eleve
    total_du: float
    total_paye: float
    solde: float

    @property
    def statut(self) -> str:
        """Retourne le statut de paiement dérivé."""
        if self.solde <= 0:
            return "Soldé"
        elif self.total_paye > 0:
            return "Partiellement payé"
        else:
            return "Non payé"