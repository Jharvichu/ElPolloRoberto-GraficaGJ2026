from dataclasses import dataclass


@dataclass
class EnemyConfig:
    """Configuración específica de un enemigo."""

    name: str = ""

    # Movimiento
    max_speed: float = 250.0

    # Físicas
    sprite_width: int = 32
    sprite_height: int = 32
    scale: float = 0.15

    # Animación
    asset_path: str = ""
    frame_duration: float = 0.1
    directions: list = None
    flip_map: dict = None

    # Vida y Daño
    max_hp: int = 100
    damage_to_player: int = 10

    # IA
    chase_range: float = 300.0
    attack_range: float = 50.0
    attack_cooldown: float = 1.0

    def __post_init__(self):
        if self.directions is None:
            self.directions = ["down", "down_right", "right", "up_right", "up"]

        if self.flip_map is None:
            self.flip_map = {
                "down": ("down", False, False),
                "down_right": ("right", False, False),
                "right": ("right", False, False),
                "up_right": ("right", False, False),
                "up": ("up", False, False),
                "up_left": ("right", True, False),
                "left": ("right", True, False),
                "down_left": ("right", True, False),
            }

# Configuración específica: GALARRETA
GALARRETA_CONFIG = EnemyConfig(
    name="Galarreta",
    asset_path="assets/gfx/bosses/galarreta",
    max_speed=50.0,
    sprite_width=32,
    sprite_height=32,
    scale=0.15,
    frame_duration=0.1,
    max_hp=40,
    damage_to_player=0.5,
    chase_range=100.0,
    attack_range=30.0,
    attack_cooldown=1.2,
)

# Configuración específica: BARBARAN
BARBARAN_CONFIG = EnemyConfig(
    name="Barbaran",
    asset_path="assets/gfx/bosses/barbaran",
    max_speed=50.0,
    sprite_width=32,
    sprite_height=32,
    scale=0.15,
    frame_duration=0.1,
    max_hp=20,
    damage_to_player=8,
    chase_range=200.0,
    attack_range=100.0,
    attack_cooldown=1.5,
)

# Configuración específica: KEIKO
KEIKO_CONFIG = EnemyConfig(
    name="Keiko",
    asset_path="assets/gfx/bosses/keiko",
    max_speed=40.0,
    sprite_width=32,
    sprite_height=32,
    scale=0.2,
    frame_duration=0.1,
    max_hp=100,
    damage_to_player=12,
    chase_range=350.0,
    attack_range=150.0,
    attack_cooldown=1.0,
)