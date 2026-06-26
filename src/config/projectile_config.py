from dataclasses import dataclass
from src.config.player_config import PLAYER_CONFIG


@dataclass
class ProjectileConfig:
    """Configuración centralizada para proyectiles."""
    name: str
    asset_path: str = ""
    speed: float = 300.0
    sprite_width: int = 12
    sprite_height: int = 12
    damage: int = 10
    max_lifetime: float = 2.0
    is_boomerang: bool = False
    return_speed: float = 400.0
    return_distance: float = 500.0
    max_bounces: int = 0
    animation_state: str = ""
    frame_duration: float = 0.1


BOOMERANG_CONFIG = ProjectileConfig(
    name="Boomerang",
    asset_path="assets/gfx/sombrero",
    speed=PLAYER_CONFIG.MAX_SPEED,
    sprite_width=16,
    sprite_height=16,
    damage=PLAYER_CONFIG.ATTACK_DAMAGE,
    max_lifetime=5.0,
    is_boomerang=True,
    return_speed=400.0,
    return_distance=400.0,
    max_bounces=3,
    animation_state="spin",
    frame_duration=0.1,
)
