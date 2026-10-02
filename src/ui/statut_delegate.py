"""Délégué d'affichage des statuts sous forme de badges."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QStyledItemDelegate


class StatutDelegate(QStyledItemDelegate):
    """Affiche les statuts dans des badges lisibles et discrets."""

    COULEURS_STATUT = {
        "Soldé": (QColor("#dcfce7"), QColor("#166534")),
        "Partiellement payé": (QColor("#ffedd5"), QColor("#9a3412")),
        "Non payé": (QColor("#fee2e2"), QColor("#991b1b")),
    }

    def paint(self, painter: QPainter, option, index):
        """Peint une pastille de statut centrée dans la cellule."""
        statut = index.data(Qt.ItemDataRole.DisplayRole)
        if statut not in self.COULEURS_STATUT:
            super().paint(painter, option, index)
            return

        painter.save()
        fond, couleur_texte = self.COULEURS_STATUT[statut]
        largeur_badge = min(option.rect.width() - 16, 148)
        badge = option.rect
        badge.setWidth(largeur_badge)
        badge.moveCenter(option.rect.center())
        badge.adjust(0, 7, 0, -7)
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.setBrush(fond)
        painter.drawRoundedRect(badge, 8, 8)
        painter.setPen(couleur_texte)
        font = painter.font()
        font.setWeight(font.Weight.DemiBold)
        painter.setFont(font)
        painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, statut)
        painter.restore()
