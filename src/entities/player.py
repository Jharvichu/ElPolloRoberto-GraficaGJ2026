from src.core.entity import Entity
from src.components.transform import TransformComponent
from src.components.velocity import VelocityComponent
from src.components.input import InputComponent
from src.components.sprite import SpriteComponent
from src.components.collider import ColliderComponent
from src.components.animation import AnimationComponent
from src.components.animation_state_machine import AnimationStateMachineComponent
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT


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
    fsm.add_state("attack", duration=0.4, face_velocity=False)

    # Transiciones: idle <-> run por velocidad
    fsm.add_transition("idle", "run",
        lambda entity: entity.get_component("VelocityComponent").velocity.magnitude() > 0.1)
    fsm.add_transition("run", "idle",
        lambda entity: entity.get_component("VelocityComponent").velocity.magnitude() <= 0.1)

    # Transiciones: a attack por input
    fsm.add_transition("idle", "attack",
        lambda entity: entity.get_component("InputComponent").is_attacking_just_pressed())
    fsm.add_transition("run", "attack",
        lambda entity: entity.get_component("InputComponent").is_attacking_just_pressed())

    # Transición: attack -> idle por duración
    fsm.add_transition("attack", "idle",
        lambda entity: fsm.state_elapsed() > 0.4)

    return fsm


def create_player(x: float = 640, y: float = 360) -> Entity:
    player = Entity(x, y)

    transform = TransformComponent()
    player.add_component("TransformComponent", transform)

    velocity = VelocityComponent(max_speed=250)
    player.add_component("VelocityComponent", velocity)

    input_component = InputComponent()
    player.add_component("InputComponent", input_component)

    # Animación (sin auto-transiciones; las maneja la FSM)
    animation = AnimationComponent(
        base_path="assets/gfx/player_test",
        frame_duration=0.25,
        default_state="idle",
        directions=["down", "down_right", "right", "up_right", "up"],
        flip_map={
            "down": ("down", False, False),
            "down_right": ("right", False, False),
            "right": ("right", False, False),
            "up_right": ("right", False, False),
            "up": ("up", False, False),
            "up_left": ("right", True, False),
            "left": ("right", True, False),
            "down_left": ("right", True, False),
        },
    )
    animation.load_animation_set("idle")
    animation.load_animation_set("run")
    animation.load_animation_set("attack")
    animation.enabled = False  # La FSM lo actualiza, no el Entity.update() genérico
    player.add_component("AnimationComponent", animation)

    sprite = SpriteComponent(width=32, height=32)
    player.add_component("SpriteComponent", sprite)

    collider = ColliderComponent(width=32, height=32, offset_x=0, offset_y=0, is_trigger=False, debug=True)
    player.add_component("ColliderComponent", collider)

    # Configurar FSM de animación
    animation_fsm = _build_player_animation_fsm(player)
    player.add_component("AnimationStateMachineComponent", animation_fsm)

    return player


def clamp_player_position(entity: Entity):
    collider = entity.get_component("ColliderComponent")

    if collider:
        min_x = 0
        max_x = SCREEN_WIDTH - collider.width
        min_y = 0
        max_y = SCREEN_HEIGHT - collider.height

        entity.position.x = max(min_x, min(max_x, entity.position.x))
        entity.position.y = max(min_y, min(max_y, entity.position.y))
