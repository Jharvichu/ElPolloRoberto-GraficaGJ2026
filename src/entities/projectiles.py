from src.core.entity import Entity
from src.components.transform import TransformComponent
from src.components.velocity import VelocityComponent
from src.components.collider import ColliderComponent
from src.components.sprite import SpriteComponent
from src.components.animation import AnimationComponent
from src.components.projectile import ProjectileComponent
from src.config.projectile_config import BOOMERANG_CONFIG, ProjectileConfig
from src.utils.vector2 import Vector2


def create_boomerang(x: float, y: float, direction: Vector2, owner) -> Entity:

    projectile = Entity(x, y)

    transformComponent = TransformComponent(scale=0.5)
    projectile.add_component("TransformComponent", transformComponent)

    velocityComponent = VelocityComponent(max_speed=BOOMERANG_CONFIG.speed)
    projectile.add_component("VelocityComponent", velocityComponent)
    projectile.add_component("ColliderComponent", ColliderComponent(16, 16, is_trigger=True))

    sprite = SpriteComponent(width=BOOMERANG_CONFIG.sprite_width, height=BOOMERANG_CONFIG.sprite_height)
    projectile.add_component("SpriteComponent", sprite)

    # Agregar animación del sombrero usando el componente de animación
    if BOOMERANG_CONFIG.animation_state:
        animation = AnimationComponent(
            base_path=BOOMERANG_CONFIG.asset_path,
            frame_duration=BOOMERANG_CONFIG.frame_duration,
            default_state=BOOMERANG_CONFIG.animation_state,
            directions=None,
        )
        animation.load_animation_set(BOOMERANG_CONFIG.animation_state)
        projectile.add_component("AnimationComponent", animation)

    projectile_comp = ProjectileComponent(projectile, BOOMERANG_CONFIG, direction, owner)
    projectile.add_component("ProjectileComponent", projectile_comp)

    # Establecer velocidad inicial en la dirección del disparo
    velocity = projectile.get_component("VelocityComponent")
    velocity.set_velocity(
        direction.x * BOOMERANG_CONFIG.speed,
        direction.y * BOOMERANG_CONFIG.speed
    )

    # Marcar como boomerang para lógica de colisión
    projectile.is_boomerang = True

    return projectile


def create_enemy_projectile(x: float, y: float, direction: Vector2, owner, enemy_config) -> Entity:

    # Velocidad de proyectil: más rápida que el enemigo
    projectile_speed = 300.0
    projectile_config = ProjectileConfig(
        name=f"{enemy_config.name}_projectile",
        speed=projectile_speed,
        damage=enemy_config.damage_to_player,
        max_lifetime=5.0,
        is_boomerang=False,
        max_bounces=0,
    )

    projectile = Entity(x, y)
    projectile.add_component("TransformComponent", TransformComponent(x, y))
    projectile.add_component("VelocityComponent", VelocityComponent(max_speed=projectile_config.speed))
    projectile.add_component("ColliderComponent", ColliderComponent(12, 12, is_trigger=True))

    sprite = SpriteComponent(width=12, height=12)
    projectile.add_component("SpriteComponent", sprite)

    projectile_comp = ProjectileComponent(projectile, projectile_config, direction, owner)
    projectile.add_component("ProjectileComponent", projectile_comp)

    # Establecer velocidad inicial en la dirección del disparo
    velocity = projectile.get_component("VelocityComponent")
    velocity.set_velocity(
        direction.x * projectile_config.speed,
        direction.y * projectile_config.speed
    )

    return projectile
