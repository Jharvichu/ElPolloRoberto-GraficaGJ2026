from src.components.animation_state_machine import AnimationStateMachineComponent
from src.core.entity import Entity
from src.components.transform import TransformComponent
from src.components.velocity import VelocityComponent
from src.components.sprite import SpriteComponent
from src.components.collider import ColliderComponent
from src.components.animation import AnimationComponent
from src.components.health import HealthComponent
from src.components.ai import AIComponent
from src.config.enemy_config import GALARRETA_CONFIG, BARBARAN_CONFIG, KEIKO_CONFIG
from src.utils.vector2 import Vector2
import math


class KeikoAIComponent(AIComponent):
    """IA especial para Keiko: dispara 5 proyectiles en abanico."""

    def __init__(self, entity, config, player):
        super().__init__(entity, config, player)
        self.pending_projectiles = []  # Lista de múltiples proyectiles

    def _handle_attack(self, player, dt):
        """Keiko dispara 5 proyectiles en patrón abanico."""
        self.attack_timer -= dt

        velocity = self.entity.get_component("VelocityComponent")
        if velocity:
            velocity.set_velocity(0, 0)

        if self.attack_timer <= 0:
            self.attack_timer = self.config.attack_cooldown
            direction = (player.position - self.entity.position).normalize()

            # Crear 5 proyectiles en abanico
            angles = [-30, -15, 0, 15, 30]  # grados
            from src.entities.projectiles import create_enemy_projectile

            for angle_deg in angles:
                # Convertir ángulo a radianes y rotar la dirección
                angle_rad = math.radians(angle_deg)
                cos_a = math.cos(angle_rad)
                sin_a = math.sin(angle_rad)

                # Rotar vector de dirección
                rotated_dir = Vector2(
                    direction.x * cos_a - direction.y * sin_a,
                    direction.x * sin_a + direction.y * cos_a
                )

                projectile = create_enemy_projectile(
                    self.entity.position.x,
                    self.entity.position.y,
                    rotated_dir.normalize(),
                    self.entity,
                    self.config
                )
                self.pending_projectiles.append(projectile)


def _build_enemy_animation_fsm(enemy: Entity) -> AnimationStateMachineComponent:

    fsm = AnimationStateMachineComponent(enemy, initial_state="idle")

    # Definir estados
    fsm.add_state("idle", duration=float('inf'), face_velocity=True)
    fsm.add_state("run", duration=float('inf'), face_velocity=True)

    # Transiciones: idle <-> run por velocidad
    fsm.add_transition("idle", "run",
        lambda entity: entity.get_component("VelocityComponent").velocity.magnitude() > 0.1)
    fsm.add_transition("run", "idle",
        lambda entity: entity.get_component("VelocityComponent").velocity.magnitude() <= 0.1)
    return fsm


def create_enemy_galarreta(x: float, y: float, player: Entity) -> Entity:
    """Galarreta: 3 vidas, ataque cuerpo a cuerpo."""
    enemy = Entity(x, y)

    transform = TransformComponent(scale=GALARRETA_CONFIG.scale)
    enemy.add_component("TransformComponent", transform)

    velocity = VelocityComponent(max_speed=GALARRETA_CONFIG.max_speed)
    enemy.add_component("VelocityComponent", velocity)

    animation = AnimationComponent(
        base_path=GALARRETA_CONFIG.asset_path,
        frame_duration=GALARRETA_CONFIG.frame_duration,
        default_state="idle",
        directions=GALARRETA_CONFIG.directions,
        flip_map=GALARRETA_CONFIG.flip_map,
    )
    animation.load_animation_set("idle")
    animation.load_animation_set("run")
    animation.enabled = False
    enemy.add_component("AnimationComponent", animation)

    sprite = SpriteComponent(GALARRETA_CONFIG.sprite_width, GALARRETA_CONFIG.sprite_height)
    enemy.add_component("SpriteComponent", sprite)

    # Collider físico (choca con paredes)
    collider = ColliderComponent(
        width=8,
        height=8,
        offset_y = 16,
        is_trigger=False
    )
    enemy.add_component("ColliderComponent", collider)

    # Trigger (recibe daño de balas)
    trigger = ColliderComponent(
        width=GALARRETA_CONFIG.sprite_width,
        height=GALARRETA_CONFIG.sprite_height,
        is_trigger=True
    )
    enemy.add_component("TriggerComponent", trigger)

    health = HealthComponent(max_hp=GALARRETA_CONFIG.max_hp)
    enemy.add_component("HealthComponent", health)

    ai = AIComponent(enemy, GALARRETA_CONFIG, player)
    enemy.add_component("AIComponent", ai)

    animation_fsm = _build_enemy_animation_fsm(enemy)
    enemy.add_component("AnimationStateMachineComponent", animation_fsm)

    return enemy


def create_enemy_barbaran(x: float, y: float, player: Entity) -> Entity:
    """Barbaran: 1 vida, dispara proyectiles."""
    enemy = Entity(x, y)

    transform = TransformComponent(scale=BARBARAN_CONFIG.scale)
    enemy.add_component("TransformComponent", transform)

    velocity = VelocityComponent(max_speed=BARBARAN_CONFIG.max_speed)
    enemy.add_component("VelocityComponent", velocity)

    animation = AnimationComponent(
        base_path=BARBARAN_CONFIG.asset_path,
        frame_duration=BARBARAN_CONFIG.frame_duration,
        default_state="idle",
        directions=BARBARAN_CONFIG.directions,
        flip_map=BARBARAN_CONFIG.flip_map,
    )
    animation.load_animation_set("idle")
    animation.load_animation_set("run")
    animation.enabled = False
    enemy.add_component("AnimationComponent", animation)

    sprite = SpriteComponent(BARBARAN_CONFIG.sprite_width, BARBARAN_CONFIG.sprite_height)
    enemy.add_component("SpriteComponent", sprite)

    # Collider físico (choca con paredes)
    collider = ColliderComponent(
        width=8,
        height=8,
        offset_y = 16,
        is_trigger=False
    )
    enemy.add_component("ColliderComponent", collider)

    # Trigger (recibe daño de balas)
    trigger = ColliderComponent(
        width=BARBARAN_CONFIG.sprite_width,
        height=BARBARAN_CONFIG.sprite_height,
        is_trigger=True
    )
    enemy.add_component("TriggerComponent", trigger)

    health = HealthComponent(max_hp=BARBARAN_CONFIG.max_hp)
    enemy.add_component("HealthComponent", health)

    ai = AIComponent(enemy, BARBARAN_CONFIG, player)
    enemy.add_component("AIComponent", ai)

    animation_fsm = _build_enemy_animation_fsm(enemy)
    enemy.add_component("AnimationStateMachineComponent", animation_fsm)

    return enemy

def create_enemy_keiko(x: float, y: float, player: Entity) -> Entity:
    """Keiko (BOSS): 10 vidas, dispara 5 proyectiles en abanico."""
    enemy = Entity(x, y)

    transform = TransformComponent(scale=KEIKO_CONFIG.scale)
    enemy.add_component("TransformComponent", transform)

    velocity = VelocityComponent(max_speed=KEIKO_CONFIG.max_speed)
    enemy.add_component("VelocityComponent", velocity)

    animation = AnimationComponent(
        base_path=KEIKO_CONFIG.asset_path,
        frame_duration=KEIKO_CONFIG.frame_duration,
        default_state="idle",
        directions=KEIKO_CONFIG.directions,
        flip_map=KEIKO_CONFIG.flip_map,
    )
    animation.load_animation_set("idle")
    animation.load_animation_set("run")
    animation.enabled = False
    enemy.add_component("AnimationComponent", animation)

    sprite = SpriteComponent(KEIKO_CONFIG.sprite_width, KEIKO_CONFIG.sprite_height)
    enemy.add_component("SpriteComponent", sprite)

    # Collider físico (choca con paredes)
    collider = ColliderComponent(
        width=KEIKO_CONFIG.sprite_width,
        height=KEIKO_CONFIG.sprite_height,
        is_trigger=False
    )
    enemy.add_component("ColliderComponent", collider)

    # Trigger (recibe daño de balas)
    trigger = ColliderComponent(
        width=KEIKO_CONFIG.sprite_width,
        height=KEIKO_CONFIG.sprite_height,
        is_trigger=True
    )
    enemy.add_component("TriggerComponent", trigger)

    health = HealthComponent(max_hp=KEIKO_CONFIG.max_hp)
    enemy.add_component("HealthComponent", health)

    # Usar AI especial que dispara múltiples proyectiles
    ai = KeikoAIComponent(enemy, KEIKO_CONFIG, player)
    enemy.add_component("AIComponent", ai)

    animation_fsm = _build_enemy_animation_fsm(enemy)
    enemy.add_component("AnimationStateMachineComponent", animation_fsm)

    return enemy
