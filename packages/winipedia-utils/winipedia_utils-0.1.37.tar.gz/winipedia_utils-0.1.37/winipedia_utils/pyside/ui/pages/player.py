"""Player page module.

This module contains the player page class for the VideoVault application.
"""

from pathlib import Path
from typing import final

from winipedia_utils.pyside.ui.pages.base.base import Base as BasePage
from winipedia_utils.pyside.ui.widgets.media_player import MediaPlayer


class Player(BasePage):
    """Player page for the VideoVault application."""

    @final
    def setup(self) -> None:
        """Setup the UI."""
        self.media_player = MediaPlayer(self.v_layout)

    @final
    def play_file(self, path: Path) -> None:
        """Play the video."""
        # set current page to player
        self.set_current_page(self.__class__)
        # Stop current playback and clean up resources
        self.media_player.play_file(path)
