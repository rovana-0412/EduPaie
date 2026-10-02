"""
EduPaie — Service métier.
Contient les règles de gestion : calcul du solde, validation des paiements,
génération du numéro de reçu.
"""
from datetime import date
from typing import List

from src.date_utils import valider_date_iso
from src.models import Eleve, Paiement, SoldeEleve
from src.repository import (
    ClasseRepository,
    EleveRepository,
    PaiementRepository,
)


class EleveService:
    """Règles métier pour les élèves."""

    def __init__(self, eleve_repo: EleveRepository):
        self.eleve_repo = eleve_repo

    def lister_tous(self) -> List[Eleve]:
        return self.eleve_repo.lister_tous()

    def rechercher(self, terme: str) -> List[Eleve]:
        return self.eleve_repo.rechercher_par_nom(terme)

    def ajouter(self, eleve: Eleve) -> int:
        self._valider_eleve(eleve)
        return self.eleve_repo.ajouter(eleve)

    def modifier(self, eleve: Eleve):
        self._valider_eleve(eleve)
        self.eleve_repo.modifier(eleve)

    def supprimer(self, id_eleve: int):
        self.eleve_repo.supprimer(id_eleve)

    def _valider_eleve(self, eleve: Eleve):
        """Valide les données d'un élève avant insertion."""
        if not eleve.nom or not eleve.nom.strip():
            raise ValueError("Le nom est obligatoire.")
        if not eleve.prenom or not eleve.prenom.strip():
            raise ValueError("Le prénom est obligatoire.")
        if not eleve.date_naissance:
            raise ValueError("La date de naissance est obligatoire.")
        valider_date_iso(eleve.date_naissance, "La date de naissance")
        if eleve.montant_total_du <= 0:
            raise ValueError("Le montant total dû doit être supérieur à 0.")
        if not eleve.id_classe:
            raise ValueError("L'élève doit être rattaché à une classe.")


class PaiementService:
    """Règles métier pour les paiements et les soldes."""

    def __init__(
        self,
        eleve_repo: EleveRepository,
        paiement_repo: PaiementRepository,
    ):
        self.eleve_repo = eleve_repo
        self.paiement_repo = paiement_repo

    def calculer_solde(self, id_eleve: int) -> SoldeEleve:
        """Calcule le solde restant d'un élève."""
        eleve = self.eleve_repo.trouver_par_id(id_eleve)
        if not eleve:
            raise ValueError(f"Élève introuvable : id={id_eleve}")

        total_paye = self.paiement_repo.somme_par_eleve(id_eleve)
        solde = eleve.montant_total_du - total_paye

        return SoldeEleve(
            eleve=eleve,
            total_du=eleve.montant_total_du,
            total_paye=total_paye,
            solde=solde,
        )

    def enregistrer_paiement(
        self,
        id_eleve: int,
        montant: float,
        mode_paiement: str,
        date_paiement: str = None,
    ) -> Paiement:
        """Enregistre un paiement après validation."""
        if montant <= 0:
            raise ValueError("Le montant doit être supérieur à 0.")

        # Vérifier le solde
        solde_actuel = self.calculer_solde(id_eleve)
        if solde_actuel.solde <= 0:
            raise ValueError("Cet élève a déjà soldé ses frais.")
        if montant > solde_actuel.solde:
            raise ValueError(
                f"Le montant ({montant:,.0f} F) dépasse le solde restant "
                f"({solde_actuel.solde:,.0f} F)."
            )

        modes_valides = ["Espèces", "Chèque", "Virement", "Mobile Money"]
        if mode_paiement not in modes_valides:
            raise ValueError(f"Mode de paiement invalide : {mode_paiement}")

        if date_paiement is None:
            date_paiement = date.today().isoformat()
        date_validee = valider_date_iso(date_paiement, "La date du paiement")

        # Enregistrer
        paiement = Paiement(
            id_paiement=None,
            date_paiement=date_validee.isoformat(),
            montant=montant,
            mode_paiement=mode_paiement,
            numero_recu="",
            id_eleve=id_eleve,
        )
        id_paiement, paiement.numero_recu = (
            self.paiement_repo.ajouter_avec_numero_recu(paiement, date_validee.year)
        )
        paiement.id_paiement = id_paiement
        return paiement

    def lister_paiements(self, id_eleve: int) -> List[Paiement]:
        """Liste les paiements d'un élève, du plus récent au plus ancien."""
        return self.paiement_repo.lister_par_eleve(id_eleve)

    def _generer_numero_recu(self, annee: int) -> str:
        """Génère un numéro de reçu unique au format REC-AAAA-NNNNNN."""
        return self.paiement_repo.prochain_numero_recu(annee)