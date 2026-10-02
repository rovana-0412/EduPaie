"""
EduPaie — Génération des reçus PDF au format reçu scolaire.
"""
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A6
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


RACINE = Path(__file__).parent.parent
RECUS_DIR = RACINE / "data" / "recus"
RECUS_DIR.mkdir(parents=True, exist_ok=True)

BLEU = colors.HexColor("#1e40af")
BLEU_CLAIR = colors.HexColor("#eff6ff")
GRIS = colors.HexColor("#475569")
GRIS_CLAIR = colors.HexColor("#cbd5e1")
VERT = colors.HexColor("#047857")


class GenerateurRecu:
    """Génère un reçu scolaire compact sur une page A6."""

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
        """Crée le reçu et retourne le chemin du PDF."""
        chemin = RECUS_DIR / f"{numero_recu}.pdf"
        marge = 0.4 * cm
        largeur = A6[0] - 2 * marge

        doc = SimpleDocTemplate(
            str(chemin),
            pagesize=A6,
            rightMargin=marge,
            leftMargin=marge,
            topMargin=marge,
            bottomMargin=marge,
            title=f"Reçu scolaire {numero_recu}",
            author=self.nom_ecole,
        )

        styles = getSampleStyleSheet()
        style_ecole = ParagraphStyle(
            "RecuEcole",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=17,
            textColor=colors.white,
            alignment=TA_CENTER,
        )
        style_entete = ParagraphStyle(
            "RecuEntete",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=colors.white,
            alignment=TA_CENTER,
        )
        style_cellule = ParagraphStyle(
            "RecuCellule",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=GRIS,
        )
        style_libelle = ParagraphStyle(
            "RecuLibelle",
            parent=style_cellule,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#1f2937"),
        )
        style_montant = ParagraphStyle(
            "RecuMontant",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=17,
            textColor=VERT,
            alignment=TA_CENTER,
        )
        style_pied = ParagraphStyle(
            "RecuPied",
            parent=style_cellule,
            fontSize=7,
            leading=9,
            alignment=TA_CENTER,
        )
        style_signature = ParagraphStyle(
            "RecuSignature",
            parent=style_cellule,
            fontSize=7,
            leading=10,
            alignment=TA_CENTER,
        )

        def texte(valeur: object, style: ParagraphStyle = style_cellule) -> Paragraph:
            return Paragraph(escape(str(valeur)), style)

        elements = []
        entete = Table(
            [
                [texte(self.nom_ecole, style_ecole)],
                [texte("REÇU DE PAIEMENT SCOLAIRE", style_entete)],
            ],
            colWidths=[largeur],
        )
        entete.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BLEU),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (0, 0), 8),
            ("BOTTOMPADDING", (0, 0), (0, 0), 2),
            ("TOPPADDING", (0, 1), (0, 1), 2),
            ("BOTTOMPADDING", (0, 1), (0, 1), 8),
        ]))
        elements.extend([entete, Spacer(1, 2)])

        largeur_libelle = 2.65 * cm
        largeur_valeur = largeur - largeur_libelle
        informations = Table(
            [
                [texte("N° reçu", style_libelle), texte(numero_recu)],
                [texte("Date", style_libelle), texte(date_paiement)],
                [texte("Élève", style_libelle), texte(nom_eleve)],
                [
                    texte("Classe / année", style_libelle),
                    texte(f"{classe} — {annee_scolaire}"),
                ],
                [texte("Motif", style_libelle), texte("Frais de scolarité")],
                [texte("Mode de paiement", style_libelle), texte(mode_paiement)],
            ],
            colWidths=[largeur_libelle, largeur_valeur],
        )
        informations.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LINEBELOW", (0, 0), (-1, -1), 0.35, GRIS_CLAIR),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        elements.extend([informations, Spacer(1, 2)])

        montant = Table(
            [[texte("MONTANT REÇU", style_libelle)], [
                texte(f"{montant_paye:,.0f} F CFA", style_montant)
            ]],
            colWidths=[largeur],
        )
        montant.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BLEU_CLAIR),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#bfdbfe")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (0, 0), 5),
            ("BOTTOMPADDING", (0, 0), (0, 0), 1),
            ("TOPPADDING", (0, 1), (0, 1), 1),
            ("BOTTOMPADDING", (0, 1), (0, 1), 5),
        ]))
        elements.extend([montant, Spacer(1, 2)])

        situation = Table(
            [
                [texte("Montant total dû", style_libelle), texte(f"{montant_total_du:,.0f} F")],
                [texte("Total payé à ce jour", style_libelle), texte(f"{total_paye:,.0f} F")],
                [texte("Solde restant", style_libelle), texte(f"{solde_apres:,.0f} F")],
                [texte("Statut", style_libelle), texte(statut, style_libelle)],
            ],
            colWidths=[largeur_libelle, largeur_valeur],
        )
        situation.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("LINEBELOW", (0, 0), (-1, -2), 0.35, GRIS_CLAIR),
            ("BACKGROUND", (0, 2), (-1, 2), BLEU_CLAIR),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        elements.extend([situation, Spacer(1, 4)])

        signatures = Table(
            [[
                Paragraph("____________________<br/>Signature du caissier", style_signature),
                Paragraph("____________________<br/>Signature du parent", style_signature),
            ]],
            colWidths=[largeur / 2, largeur / 2],
        )
        signatures.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
            ("LINEABOVE", (0, 0), (-1, -1), 0.5, GRIS_CLAIR),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ]))
        elements.extend([
            signatures,
            Spacer(1, 2),
            texte("Merci de conserver ce reçu comme preuve de paiement.", style_pied),
            texte(f"Édité le {date.today().isoformat()}", style_pied),
        ])

        doc.build(elements)
        return chemin
