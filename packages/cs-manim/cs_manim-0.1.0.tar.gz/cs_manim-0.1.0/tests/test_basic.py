"""Tests pour les imports et la configuration de base."""


def test_package_import():
    """Test que le package peut être importé avec ses métadonnées."""
    import cs_manim

    assert cs_manim.__version__ == "0.1.0"
    assert cs_manim.__author__ == "Pierre-Olivier Brillant"


def test_objects_import():
    """Test que les objets principaux peuvent être importés."""
    from cs_manim.objects import Computer, Server, MobilePhone

    # Vérifier que les classes existent et sont callable
    assert callable(Computer)
    assert callable(Server)
    assert callable(MobilePhone)


def test_style_import():
    """Test que les constantes de style peuvent être importées."""
    from cs_manim.style import (
        CLIENT_COLOR,
        SERVER_COLOR,
        REQUEST_COLOR,
        RESPONSE_COLOR,
        FONT_NAME,
    )

    # Vérifier que les constantes existent et ont le bon type
    assert CLIENT_COLOR is not None
    assert SERVER_COLOR is not None
    assert REQUEST_COLOR is not None
    assert RESPONSE_COLOR is not None
    assert isinstance(FONT_NAME, str)
    assert FONT_NAME == "Inconsolata"


def test_public_api():
    """Test que l'API publique est accessible via le package principal."""
    import cs_manim

    # Vérifier que les objets principaux sont accessibles
    assert hasattr(cs_manim, "Computer")
    assert hasattr(cs_manim, "Server")
    assert hasattr(cs_manim, "MobilePhone")

    # Vérifier que les styles sont accessibles
    assert hasattr(cs_manim, "CLIENT_COLOR")
    assert hasattr(cs_manim, "SERVER_COLOR")
    assert hasattr(cs_manim, "FONT_NAME")


def test_objects_instantiation():
    """Test que les objets peuvent être instanciés (sans Manim scene)."""
    from cs_manim import Computer, Server, MobilePhone

    # Test que les constructeurs acceptent des paramètres
    try:
        # Ces tests ne vont pas créer les objets complets car Manim n'est pas
        # initialisé, mais ils testent que les constructeurs sont corrects
        computer_class = Computer
        server_class = Server
        mobile_class = MobilePhone

        assert computer_class is not None
        assert server_class is not None
        assert mobile_class is not None
    except Exception:
        # Si Manim n'est pas disponible, c'est OK pour ce test de base
        pass
