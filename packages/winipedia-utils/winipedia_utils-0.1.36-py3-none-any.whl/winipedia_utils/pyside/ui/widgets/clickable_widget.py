from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QWidget


class ClickableWidget(QWidget):
    """Widget that can be clicked."""

    clicked = Signal()

    def mousePressEvent(self, event: Any) -> None:  # noqa: N802
        """Handle mouse press event."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class ClickableVideoWidget(QVideoWidget):
    """Video widget that can be clicked."""

    clicked = Signal()

    def mousePressEvent(self, event: Any) -> None:  # noqa: N802
        """Handle mouse press event."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
