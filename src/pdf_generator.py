"""
EduPaie — Génération des reçus PDF avec ReportLab.
"""
from pathlib import Path
from datetime import date

from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


# Dossier de sortie
RACINE = Path(__file__).parent.parent
RECUS_DIR = RACINE / "data" / "recus"
RECUS_DIR.mkdir(parents=True, exist_ok=True)


class GenerateurRecu:
    """Génère un reçu PDF pour un paiement donné."""

    def __init__(self, nom_ecole: str = "École EduPaie"):
        self.nom_ecole = nom_ecole

    def generer(
        self,
        numero_recu: str,
        nom_eleve: str,
        classe: str,
        annee_scolaire: str,
        date_paiement: str,
        montant_paye: float,
        mode_paiement: str,
        montant_total_du: float,
        total_paye: float,
        solde_apres: float,
        statut: str,
    ) -> Path:
        """
        Génère un reçu PDF et retourne son chemin.
        """
        # Nom du fichier
        nom_fichier = f"{numero_recu}.pdf"
        chemin = RECUS_DIR / nom_fichier

        # Créer le document (format A5, portrait)
        doc = SimpleDocTemplate(
            str(chemin),
            pagesize=A5,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )

        # Styles
        styles = getSampleStyleSheet()
        style_titre = ParagraphStyle(
            "Titre",
            parent=styles["Heading1"],
            fontSize=16,
            textColor=HexColor("#1e40af"),
            alignment=TA_CENTER,
            spaceAfter=6,
        )
        style_sous_titre = ParagraphStyle(
            "SousTitre",
            parent=styles["Heading2"],
            fontSize=11,
            textColor=HexColor("#374151"),
            alignment=TA_CENTER,
            spaceAfter=12,
        )
        style_section = ParagraphStyle(
            "Section",
            parent=styles["Heading3"],
            fontSize=10,
            textColor=HexColor("#1e40af"),
            spaceBefore=8,
            spaceAfter=6,
        )
        style_normal = ParagraphStyle(
            "Normal",
            parent=styles["Normal"],
            fontSize=10,
            alignment=TA_LEFT,
        )

        # Contenu
        elements = []

        # En-tête
        elements.append(Paragraph(self.nom_ecole, style_titre))
        elements.append(Paragraph(f"REÇU DE PAIEMENT N° {numero_recu}", style_sous_titre))
        elements.append(Spacer(1, 0.3 * cm))

        # Infos élève
        elements.append(Paragraph("Informations de l'élève", style_section))
        data_eleve = [
            ["Élève", nom_eleve],
            ["Classe", classe],
            ["Année scolaire", annee_scolaire],
            ["Date du paiement", date_paiement],
        ]
        table_eleve = Table(data_eleve, colWidths=[4 * cm, 8 * cm])
        table_eleve.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(table_eleve)
        elements.append(Spacer(1, 0.3 * cm))

        # Détails du paiement
        elements.append(Paragraph("Détails du paiement", style_section))
        data_paiement = [
            ["Montant payé", f"{montant_paye:,.0f} F CFA"],
            ["Mode de paiement", mode_paiement],
            ["Numéro de reçu", numero_recu],
        ]
        table_paiement = Table(data_paiement, colWidths=[4 * cm, 8 * cm])
        table_paiement.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#f0f9ff")),
            ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#bfdbfe")),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(table_paiement)
        elements.append(Spacer(1, 0.3 * cm))

        # Situation après paiement
        elements.append(Paragraph("Situation après paiement", style_section))
        data_situation = [
            ["Montant total dû", f"{montant_total_du:,.0f} F CFA"],
            ["Total déjà payé", f"{total_paye:,.0f} F CFA"],
            ["Solde restant", f"{solde_apres:,.0f} F CFA"],
            ["Statut", statut],
        ]
        table_situation = Table(data_situation, colWidths=[4 * cm, 8 * cm])
        table_situation.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),  # solde en gras
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#d1d5db")),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(table_situation)

        # Pied de page
        elements.append(Spacer(1, 0.5 * cm))
        elements.append(Paragraph(
            "Merci de conserver ce reçu. Il constitue une preuve de paiement.",
            style_normal,
        ))
        elements.append(Spacer(1, 0.2 * cm))
        elements.append(Paragraph(
            f"Document généré le {date.today().isoformat()} par EduPaie.",
            style_normal,
        ))

        # Générer le PDF
        doc.build(elements)

        return chemin