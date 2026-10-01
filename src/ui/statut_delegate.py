"""
EduPaie — Délégué pour afficher les statuts avec fond coloré.
Contourne le QSS qui écrase les couleurs de fond.
"""
from PySide6.QtWidgets import QStyledItemDelegate, QStyle
from PySide6.QtGui import QColor, QPainter, QBrush
from PySide6.QtCore import Qt


class StatutDelegate(QStyledItemDelegate):
    """Délégué qui peint les cellules de statut avec un fond coloré."""

    COULEURS_STATUT = {
        "Soldé":               QColor("#10b981"),  # vert
        "Partiellement payé":  QColor("#f59e0b"),  # orange
        "Non payé":            QColor("#ef4444"),  # rouge
    }

    def paint(self, painter: QPainter, option, index):
        """Peint la cellule."""
        statut = index.data(Qt.DisplayRole)

        if statut in self.COULEURS_STATUT:
            # Sauvegarder l'état
            painter.save()

            # Dessiner le fond coloré
            painter.fillRect(option.rect, QBrush(self.COULEURS_STATUT[statut]))

            # Dessiner le texte en blanc, centré, en gras
            painter.setPen(QColor("white"))
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)

            painter.drawText(
                option.rect,
                Qt.AlignCenter,
                statut
            )

            # Restaurer l'état
            painter.restore()
        else:
            # Comportement par défaut
            super().paint(painter, option, index)