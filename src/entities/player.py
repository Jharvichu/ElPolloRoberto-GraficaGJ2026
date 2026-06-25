from src.core.entity import Entity
from src.components.transform import TransformComponent
from src.components.velocity import VelocityComponent
from src.components.input import InputComponent
from src.components.sprite import SpriteComponent
from src.components.collider import ColliderComponent
from src.components.animation import AnimationComponent
from src.components.animation_state_machine import AnimationStateMachineComponent
from src.components.health import HealthComponent
from src.config.game_config import GAME_CONFIG
from src.config.player_config import PLAYER_CONFIG


def _build_player_animation_fsm(player: Entity) -> AnimationStateMachineComponent:
    """
    Configura la máquina de estados de animación del jugador.

    Transiciones:
    - idle <-> run: según magnitud de velocidad
    - idle/run -> attack: al hacer click de ataque
    - attack -> idle: después de duración fija
    """
    fsm = AnimationStateMachineComponent(player, initial_state="idle")

    # Definir estados
    fsm.add_state("idle", duration=float('inf'), face_velocity=True)
    fsm.add_state("run", duration=float('inf'), face_velocity=True)

    # Transiciones: idle <-> run por velocidad
    fsm.add_transition("idle", "run",
        lambda entity: entity.get_component("VelocityComponent").velocity.magnitude() > 0.1)
    fsm.add_transition("run", "idle",
        lambda entity: entity.get_component("VelocityComponent").velocity.magnitude() <= 0.1)

    return fsm


def create_player(x: float = None, y: float = None) -> Entity:
    """
    Factory para crear el jugador completamente configurado.

    Args:
        x: Posición X inicial (por defecto, centro pantalla)
        y: Posición Y inicial (por defecto, centro pantalla)

    Returns:
        Entity con todos los componentes del jugador
    """
    if x is None:
        x = GAME_CONFIG.SCREEN_WIDTH / 2
    if y is None:
        y = GAME_CONFIG.SCREEN_HEIGHT / 2

    player = Entity(x, y)

    # Componente de Transformación
    transform = TransformComponent(scale=0.15)
    player.add_component("TransformComponent", transform)

    # Componente de Movimiento
    velocity = VelocityComponent(max_speed=PLAYER_CONFIG.MAX_SPEED)
    player.add_component("VelocityComponent", velocity)

    # Componente de Entrada
    input_component = InputComponent()
    player.add_component("InputComponent", input_component)

    # Componente de Animación
    # La FSM controla las transiciones de estado, no el componente automáticamente
    animation = AnimationComponent(
        base_path=PLAYER_CONFIG.ANIMATION_BASE_PATH,
        frame_duration=PLAYER_CONFIG.FRAME_DURATION,
        default_state="idle",
        directions=PLAYER_CONFIG.DIRECTIONS,
        flip_map=PLAYER_CONFIG.FLIP_MAP,
    )
    animation.load_animation_set("idle")
    animation.load_animation_set("run")
    animation.load_animation_set("attack")
    animation.enabled = False  # La FSM lo actualiza, no el Entity.update()
    player.add_component("AnimationComponent", animation)

    # Componente de Sprite
    sprite = SpriteComponent(PLAYER_CONFIG.SPRITE_WIDTH, PLAYER_CONFIG.SPRITE_HEIGHT)
    player.add_component("SpriteComponent", sprite)

    # Componente de Colisión
    collider = ColliderComponent(
        width = PLAYER_CONFIG.SPRITE_WIDTH - 10,
        height = PLAYER_CONFIG.SPRITE_HEIGHT,
        offset_y = 16
    )
    player.add_component("ColliderComponent", collider)

    # Máquina de Estados de Animación
    animation_fsm = _build_player_animation_fsm(player)
    player.add_component("AnimationStateMachineComponent", animation_fsm)

    return player


def clamp_player_position(entity: Entity):
    """Mantiene al jugador dentro de los límites de pantalla"""
    collider = entity.get_component("ColliderComponent")

    if collider:
        min_x = -collider.offset_x
        max_x = GAME_CONFIG.SCREEN_WIDTH - collider.width - collider.offset_x
        min_y = -collider.offset_y
        max_y = GAME_CONFIG.SCREEN_HEIGHT - collider.height - collider.offset_y

        entity.position.x = max(min_x, min(max_x, entity.position.x))
        entity.position.y = max(min_y, min(max_y, entity.position.y))


def create_static_collider(x: float, y: float, width: float, height: float) -> Entity:
    """Factory para crear un collider estático (obstáculo del mapa)"""
    collider_entity = Entity(x, y)

    transform = TransformComponent()
    collider_entity.add_component("TransformComponent", transform)

    # Offset 0,0 porque los colliders del mapa TMX usan esquina superior-izquierda
    collider = ColliderComponent(width=width, height=height, offset_x=0, offset_y=0)
    collider_entity.add_component("ColliderComponent", collider)

    return collider_entity
