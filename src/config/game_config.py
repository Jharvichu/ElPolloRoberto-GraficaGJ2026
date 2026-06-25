from dataclasses import dataclass
from typing import Optional


@dataclass
class GameConfig:
    """Configuración global del juego."""
    SCREEN_WIDTH: int = 960
    SCREEN_HEIGHT: int = 540
    FPS: int = 60
    TITLE: str = "El Pollo Roberto: La Vida Da Vueltas"
    BG_COLOR: tuple = (30, 30, 30)

    # Debug
    DEBUG_ENABLED: bool = False
    DEBUG_COLOR_SOLID: tuple = (255, 0, 0)
    DEBUG_COLOR_TRIGGER: tuple = (0, 255, 0)
    DEBUG_THICKNESS: int = 2

    # Cámara
    CAMERA_WIDTH: int = 960
    CAMERA_HEIGHT: int = 540
    CAMERA_SMOOTHING: float = 0.15


# Instancia global
GAME_CONFIG = GameConfig()
