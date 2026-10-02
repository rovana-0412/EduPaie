"""Palette et style global de l'interface EduPaie."""

COULEURS = {
    "primaire": "#2563eb",
    "primaire_dark": "#1d4ed8",
    "succes": "#15803d",
    "attention": "#b45309",
    "danger": "#b91c1c",
    "gris_fonce": "#172033",
    "gris": "#64748b",
    "gris_clair": "#dbe3ee",
    "gris_tres_clair": "#f3f6fb",
    "blanc": "#ffffff",
}

STYLE_GLOBAL = f"""
QWidget {{
    font-family: Arial;
    font-size: 13px;
    color: {COULEURS["gris_fonce"]};
    background-color: transparent;
}}

QMainWindow, QDialog {{
    background-color: {COULEURS["gris_tres_clair"]};
}}

QLabel#titre_principal {{
    font-size: 24px;
    font-weight: 700;
    color: {COULEURS["gris_fonce"]};
}}

QLabel#sous_titre {{
    color: {COULEURS["gris"]};
    font-size: 13px;
}}

QLabel#titre_section {{
    font-size: 15px;
    font-weight: 650;
    color: {COULEURS["gris_fonce"]};
}}

QLabel#carte_titre {{
    color: {COULEURS["gris"]};
    font-size: 12px;
    font-weight: 600;
}}

QLabel#carte_valeur {{
    font-size: 25px;
    font-weight: 700;
    color: {COULEURS["gris_fonce"]};
}}

QLabel#statut_succes, QLabel#statut_attention, QLabel#statut_danger {{
    padding: 7px 12px;
    border-radius: 7px;
    font-weight: 700;
}}

QLabel#statut_succes {{
    color: #166534;
    background-color: #dcfce7;
}}

QLabel#statut_attention {{
    color: #9a3412;
    background-color: #ffedd5;
}}

QLabel#statut_danger {{
    color: #991b1b;
    background-color: #fee2e2;
}}

QLabel#message_erreur {{
    color: {COULEURS["danger"]};
    font-weight: 600;
}}

QFrame#surface, QFrame#carte_stat {{
    background-color: {COULEURS["blanc"]};
    border: 1px solid {COULEURS["gris_clair"]};
    border-radius: 10px;
}}

QFrame#carte_stat {{
    border-top: 3px solid {COULEURS["primaire"]};
}}

QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit {{
    min-height: 20px;
    padding: 8px 11px;
    color: {COULEURS["gris_fonce"]};
    background-color: {COULEURS["blanc"]};
    border: 1px solid {COULEURS["gris_clair"]};
    border-radius: 6px;
    selection-background-color: {COULEURS["primaire"]};
}}

QLineEdit:hover, QComboBox:hover, QDoubleSpinBox:hover, QDateEdit:hover {{
    border-color: #aab8ca;
}}

QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
    border: 1px solid {COULEURS["primaire"]};
}}

QLineEdit:read-only {{
    color: {COULEURS["gris"]};
    background-color: #f8fafc;
}}

QComboBox::drop-down {{
    width: 26px;
    border: none;
}}

QPushButton {{
    min-height: 20px;
    padding: 8px 14px;
    color: {COULEURS["gris_fonce"]};
    background-color: {COULEURS["blanc"]};
    border: 1px solid {COULEURS["gris_clair"]};
    border-radius: 6px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: #f8fafc;
    border-color: #aab8ca;
}}

QPushButton:pressed {{
    background-color: #e8eef6;
}}

QPushButton:disabled {{
    color: #94a3b8;
    background-color: #edf1f6;
    border-color: #e2e8f0;
}}

QPushButton#btn_primaire {{
    color: white;
    background-color: {COULEURS["primaire"]};
    border: 1px solid {COULEURS["primaire"]};
}}

QPushButton#btn_primaire:hover {{
    background-color: {COULEURS["primaire_dark"]};
    border-color: {COULEURS["primaire_dark"]};
}}

QPushButton#btn_succes {{
    color: white;
    background-color: {COULEURS["succes"]};
    border: 1px solid {COULEURS["succes"]};
}}

QPushButton#btn_succes:hover {{
    background-color: #166534;
}}

QPushButton#btn_danger {{
    color: {COULEURS["danger"]};
    background-color: #fffafa;
    border-color: #fecaca;
}}

QPushButton#btn_danger:hover {{
    background-color: #fef2f2;
}}

QTableWidget {{
    color: {COULEURS["gris_fonce"]};
    background-color: {COULEURS["blanc"]};
    alternate-background-color: #f8fafc;
    border: 1px solid {COULEURS["gris_clair"]};
    border-radius: 8px;
    gridline-color: #edf1f6;
    selection-background-color: #eaf1ff;
    selection-color: {COULEURS["gris_fonce"]};
    outline: none;
}}

QTableWidget::item {{
    padding: 7px 9px;
    border: none;
}}

QHeaderView::section {{
    min-height: 22px;
    padding: 9px 8px;
    color: #475569;
    background-color: #f8fafc;
    border: none;
    border-bottom: 1px solid {COULEURS["gris_clair"]};
    font-size: 11px;
    font-weight: 700;
}}

QTableCornerButton::section {{
    background-color: #f8fafc;
    border: none;
    border-bottom: 1px solid {COULEURS["gris_clair"]};
}}

QScrollBar:vertical {{
    width: 10px;
    margin: 2px;
    background: transparent;
}}

QScrollBar::handle:vertical {{
    min-height: 24px;
    background: #cbd5e1;
    border-radius: 5px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
    border: none;
}}

QToolTip {{
    padding: 5px 8px;
    color: white;
    background-color: {COULEURS["gris_fonce"]};
    border: none;
    border-radius: 4px;
}}
"""
