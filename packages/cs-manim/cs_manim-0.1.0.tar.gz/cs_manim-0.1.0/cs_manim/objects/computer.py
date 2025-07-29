from manim import VGroup, Rectangle, Text, UP, DOWN
from ..style import FONT_NAME, CLIENT_COLOR


class Computer(VGroup):

    def __init__(self, name="Computer", color=CLIENT_COLOR):
        """
        Crée un Ordinateur

        Args:
            name: Nom de l'ordinateur
            color: Couleur du client (par défaut BLUE)
        """
        super().__init__(
            Rectangle(width=2, height=1.2, color=color, fill_opacity=0.3),
            Rectangle(width=2.2, height=0.2, color=color, fill_opacity=0.8).shift(
                DOWN * 0.7
            ),
            Text(name, font_size=20, color=color, font=FONT_NAME).shift(UP * 0.3),
        )
