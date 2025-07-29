"""
CS-Manim: Animations vidéo avec Manim pour expliquer les concepts techniques
liés à l'informatique.

Cette librairie fournit des objets et des styles réutilisables pour créer
des animations éducatives avec Manim, spécialement conçue pour expliquer
des concepts d'informatique.
"""

from .objects import Computer, Server, MobilePhone
from .style import (
    CLIENT_COLOR,
    SERVER_COLOR,
    REQUEST_COLOR,
    RESPONSE_COLOR,
    FONT_NAME,
)

__version__ = "0.1.0"
__author__ = "Pierre-Olivier Brillant"
__email__ = "pierreolivierbrillant@gmail.com"

__all__ = [
    "Computer",
    "Server",
    "MobilePhone",
    "CLIENT_COLOR",
    "SERVER_COLOR",
    "REQUEST_COLOR",
    "RESPONSE_COLOR",
    "FONT_NAME",
]
