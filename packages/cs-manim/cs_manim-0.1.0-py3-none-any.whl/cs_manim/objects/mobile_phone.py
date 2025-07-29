from manim import VGroup, RoundedRectangle, Rectangle, Text, DOWN, PURPLE
from ..style import FONT_NAME


class MobilePhone(VGroup):

    def __init__(self, name="Mobile", color=PURPLE):
        """
        Crée un téléphone mobile

        Args:
            name: Nom du téléphone (par défaut "Mobile")
            color: Couleur du téléphone (par défaut PURPLE)

        Returns:
            VGroup: Le groupe d'objets représentant le téléphone mobile
        """
        return super().__init__(
            RoundedRectangle(
                width=0.8,
                height=1.4,
                color=color,
                fill_opacity=0.3,
                corner_radius=0.1,
            ),
            Rectangle(width=0.6, height=1.2, color=color, fill_opacity=0.1),
            Text(name, font_size=16, color=color, font=FONT_NAME).shift(DOWN * 0.9),
        )
