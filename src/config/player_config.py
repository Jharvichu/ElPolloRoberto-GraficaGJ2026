from dataclasses import dataclass


@dataclass
class PlayerConfig:
    """Estadísticas y configuración del jugador."""

    # Movimiento
    MAX_SPEED: float = 250.0  # píxeles/segundo
    ACCELERATION: float = 500.0  # píxeles/segundo²
    FRICTION: float = 400.0  # píxeles/segundo² (desaceleración)

    # Físicas
    SPRITE_WIDTH: int = 32
    SPRITE_HEIGHT: int = 16

    # Animación
    ANIMATION_BASE_PATH: str = "assets/gfx/pollo_con_sombrero"
    FRAME_DURATION: float = 0.25  # segundos por frame
    DIRECTIONS: list = None
    FLIP_MAP: dict = None

    # Vida y Daño
    MAX_HP: int = 100
    INVINCIBILITY_DURATION: float = 1.0  # segundos de invencibilidad después de daño
    KNOCKBACK_FORCE: float = 200.0  # píxeles/segundo al recibir daño

    # Ataque
    ATTACK_DAMAGE: int = 10
    ATTACK_COOLDOWN: float = 0.5  # segundos
    ATTACK_DURATION: float = 0.4  # duración de animación de ataque

    # Parry
    PARRY_WINDOW: float = 0.3  # segundos durante los que se puede parry
    PARRY_COOLDOWN: float = 0.8  # segundos

    def __post_init__(self):
        # Establecer valores por defecto para listas/dicts
        if self.DIRECTIONS is None:
            self.DIRECTIONS = ["down", "down_right", "right", "up_right", "up"]

        if self.FLIP_MAP is None:
            self.FLIP_MAP = {
                "down": ("down", False, False),
                "down_right": ("right", False, False),
                "right": ("right", False, False),
                "up_right": ("right", False, False),
                "up": ("up", False, False),
                "up_left": ("right", True, False),
                "left": ("right", True, False),
                "down_left": ("right", True, False),
            }


# Instancia global de configuración del jugador
PLAYER_CONFIG = PlayerConfig()
