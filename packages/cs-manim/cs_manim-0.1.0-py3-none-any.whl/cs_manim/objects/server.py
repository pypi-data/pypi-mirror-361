from manim import (
    VGroup,
    Rectangle,
    Circle,
    Text,
    UP,
    LEFT,
    DOWN,
    RED,
    GREEN,
    YELLOW,
)
from ..style import FONT_NAME, SERVER_COLOR


class Server(VGroup):

    def __init__(
        self,
        name="Server",
        color=SERVER_COLOR,
    ):
        """
        Crée un serveur

        Args:
            name: Nom du serveur (par défaut "Serveur")
            color: Couleur du serveur (par défaut GREEN)

        Returns:
            VGroup: Le groupe d'objets représentant le serveur
        """
        return super().__init__(
            # Boîtier principal
            Rectangle(width=1.0, height=1.4, color=color, fill_opacity=0.3),
            # Rack supérieur
            Rectangle(width=0.8, height=0.3, color=color, fill_opacity=0.1).shift(
                UP * 0.4
            ),
            Circle(radius=0.02, color=RED, fill_opacity=1).shift(UP * 0.4 + LEFT * 0.3),
            Circle(radius=0.02, color=GREEN, fill_opacity=1).shift(
                UP * 0.4 + LEFT * 0.2
            ),
            # Rack milieu
            Rectangle(width=0.8, height=0.3, color=color, fill_opacity=0.1),
            Circle(radius=0.02, color=GREEN, fill_opacity=1).shift(LEFT * 0.3),
            Circle(radius=0.02, color=GREEN, fill_opacity=1).shift(LEFT * 0.2),
            # Rack inférieur
            Rectangle(width=0.8, height=0.3, color=color, fill_opacity=0.1).shift(
                DOWN * 0.4
            ),
            Circle(radius=0.02, color=YELLOW, fill_opacity=1).shift(
                DOWN * 0.4 + LEFT * 0.3
            ),
            Circle(radius=0.02, color=GREEN, fill_opacity=1).shift(
                DOWN * 0.4 + LEFT * 0.2
            ),
            # Nom du serveur
            Text(name, font_size=14, color=color, font=FONT_NAME).shift(DOWN * 0.9),
        )
