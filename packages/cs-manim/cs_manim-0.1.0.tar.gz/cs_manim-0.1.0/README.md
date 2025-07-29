# CS-Manim

Animations vidéo avec Manim pour expliquer les concepts techniques liés à l'informatique.

## Description

CS-Manim est une librairie Python qui fournit des objets et des styles réutilisables pour créer des animations éducatives avec Manim, spécialement conçue pour expliquer des concepts d'informatique et de programmation.

## Installation

```bash
pip install cs-manim
```

## Utilisation

```python
from manim import *
from cs_manim import Computer, Server, MobilePhone
from cs_manim import CLIENT_COLOR, SERVER_COLOR, FONT_NAME

class MyScene(Scene):
    def construct(self):
        # Créer des objets pour vos animations
        computer = Computer("PC Client")
        server = Server("API Server")
        mobile = MobilePhone("Smartphone")

        # Positionner et animer
        computer.shift(LEFT * 3)
        server.shift(RIGHT * 3)

        self.play(Create(computer))
        self.play(Create(server))
```

## Fonctionnalités

- **Objets réutilisables** : Ordinateurs, serveurs, téléphones portables
- **Styles cohérents** : Couleurs et polices prédéfinies
- **Compatible Manim** : Utilise Manim 0.19.0+
- **Facile à utiliser** : Import simple et API intuitive

## Objets disponibles

### Computer

```python
computer = Computer(name="Mon PC", color=CLIENT_COLOR)
```

### Server

```python
server = Server(name="Mon Serveur", color=SERVER_COLOR)
```

### MobilePhone

```python
mobile = MobilePhone(name="Mon Téléphone", color=PURPLE)
```

## Styles disponibles

- `CLIENT_COLOR` : Couleur par défaut pour les clients (BLUE)
- `SERVER_COLOR` : Couleur par défaut pour les serveurs (GREEN)
- `REQUEST_COLOR` : Couleur pour les requêtes (YELLOW)
- `RESPONSE_COLOR` : Couleur pour les réponses (ORANGE)
- `FONT_NAME` : Police par défaut ("Inconsolata")

## Développement

### Configuration de l'environnement

```bash
# Cloner le dépôt
git clone https://github.com/PierreOlivierBrillant/cs-manim.git
cd cs-manim

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# Installer en mode développement
pip install -e .[dev]
```

### Tests

```bash
# Exécuter les tests
pytest

# Avec couverture
pytest --cov=cs_manim
```

### Formatage et linting

```bash
# Formater le code
black cs_manim tests examples

# Vérifier le style
flake8 cs_manim tests examples

# Vérifier les types
mypy cs_manim
```

### Construction du package

```bash
# Construire le package
python -m build

# Vérifier le package
twine check dist/*
```

## Publication

### Prérequis pour la publication

1. Compte PyPI (https://pypi.org/)
2. Token d'API PyPI configuré
3. Toutes les vérifications passées

### Étapes de publication

1. **Mettre à jour la version** dans `pyproject.toml`
2. **Mettre à jour le CHANGELOG.md**
3. **Créer un tag git** : `git tag v0.1.0`
4. **Pousser le tag** : `git push origin v0.1.0`
5. **Créer une release sur GitHub**

La publication sur PyPI se fait automatiquement via GitHub Actions lors de la création d'une release.

### Publication manuelle

```bash
# Construire le package
python -m build

# Publier sur PyPI
twine upload dist/*
```

## Exemples

Voir le dossier `examples/` pour des exemples d'utilisation.

## Contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les instructions de contribution.

## Dépendances

- Python >= 3.10
- Manim >= 0.19.0
- Pillow >= 11.0.0
- NumPy >= 1.24.0
- SciPy >= 1.10.0

## Licence

MIT License - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Auteur

Pierre-Olivier Brillant - pierreolivierbrillant@gmail.com

## Liens

- [GitHub](https://github.com/PierreOlivierBrillant/cs-manim)
- [PyPI](https://pypi.org/project/cs-manim/)
- [Documentation Manim](https://docs.manim.community/)
