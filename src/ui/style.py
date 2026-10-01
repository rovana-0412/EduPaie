"""
EduPaie — Feuille de style globale (QSS).
Palette cohérente et moderne pour toute l'application.
"""

# Palette de couleurs
COULEURS = {
    "primaire":      "#2563eb",  # bleu
    "primaire_dark": "#1e40af",
    "succes":        "#10b981",  # vert
    "succes_dark":   "#059669",
    "attention":     "#f59e0b",  # orange
    "danger":        "#ef4444",  # rouge
    "gris_fonce":    "#1f2937",
    "gris":          "#6b7280",
    "gris_clair":    "#e5e7eb",
    "gris_tres_clair":"#f9fafb",
    "blanc":         "#ffffff",
}

# Feuille de style globale
STYLE_GLOBAL = f"""
QWidget {{
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
    color: {COULEURS['gris_fonce']};
    background-color: {COULEURS['blanc']};
}}

QMainWindow, QDialog {{
    background-color: {COULEURS['gris_tres_clair']};
}}

/* ===== Titres ===== */
QLabel#titre_principal {{
    font-size: 22px;
    font-weight: bold;
    color: {COULEURS['primaire_dark']};
    padding: 12px;
}}

QLabel#titre_section {{
    font-size: 15px;
    font-weight: bold;
    color: {COULEURS['gris_fonce']};
    padding: 6px 0;
}}

/* ===== Champs de saisie ===== */
QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit {{
    padding: 8px 12px;
    border: 1px solid {COULEURS['gris_clair']};
    border-radius: 6px;
    background-color: {COULEURS['blanc']};
    min-height: 20px;
}}

QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
    border: 2px solid {COULEURS['primaire']};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

/* ===== Boutons ===== */
QPushButton {{
    padding: 8px 16px;
    border: 1px solid {COULEURS['gris_clair']};
    border-radius: 6px;
    background-color: {COULEURS['blanc']};
    color: {COULEURS['gris_fonce']};
    font-weight: 500;
    min-height: 20px;
}}

QPushButton:hover {{
    background-color: {COULEURS['gris_tres_clair']};
    border-color: {COULEURS['gris']};
}}

QPushButton:pressed {{
    background-color: {COULEURS['gris_clair']};
}}

/* Bouton primaire (bleu) */
QPushButton#btn_primaire {{
    background-color: {COULEURS['primaire']};
    color: white;
    border: none;
    font-weight: bold;
}}

QPushButton#btn_primaire:hover {{
    background-color: {COULEURS['primaire_dark']};
}}

/* Bouton succès (vert) */
QPushButton#btn_succes {{
    background-color: {COULEURS['succes']};
    color: white;
    border: none;
    font-weight: bold;
}}

QPushButton#btn_succes:hover {{
    background-color: {COULEURS['succes_dark']};
}}

/* ===== Tableaux ===== */
QTableWidget {{
    background-color: {COULEURS['blanc']};
    border: 1px solid {COULEURS['gris_clair']};
    border-radius: 6px;
    gridline-color: {COULEURS['gris_clair']};
    alternate-background-color: {COULEURS['gris_tres_clair']};
}}

QTableWidget::item {{
    padding: 8px;
    border: none;
}}

/* Pas de règle pour item:selected → les couleurs personnalisées sont préservées */

QHeaderView::section {{
    background-color: {COULEURS['gris_fonce']};
    color: white;
    padding: 10px;
    border: none;
    font-weight: bold;
    font-size: 12px;
}}

/* ===== Cartes de statistiques ===== */
QFrame#carte_stat {{
    background-color: {COULEURS['blanc']};
    border-radius: 10px;
    border-left: 5px solid {COULEURS['primaire']};
    padding: 4px;
}}

QFrame#carte_stat QLabel#titre_stat {{
    font-size: 12px;
    color: {COULEURS['gris']};
    font-weight: normal;
}}

QFrame#carte_stat QLabel#valeur_stat {{
    font-size: 26px;
    font-weight: bold;
    color: {COULEURS['gris_fonce']};
}}
"""