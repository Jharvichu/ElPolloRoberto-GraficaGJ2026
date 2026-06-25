import pygame
from enum import Enum, auto

from src.core.component import Component
from src.utils.vector2 import Vector2


class InputAction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    ATTACK = auto()
    PARRY = auto()
    TOGGLE_COLLIDERS = auto()
    CYCLE_CAMERA = auto()


class InputComponent(Component):
    """Captura entrada del jugador"""

    def __init__(self):
        super().__init__()

        self.input_direction = Vector2(0, 0)

        self.keys_pressed = {
            InputAction.UP: False,
            InputAction.DOWN: False,
            InputAction.LEFT: False,
            InputAction.RIGHT: False,
            InputAction.ATTACK: False,
            InputAction.PARRY: False,
            InputAction.TOGGLE_COLLIDERS: False,
            InputAction.CYCLE_CAMERA: False,
        }

        self.previous_keys_pressed = self.keys_pressed.copy()

    def update(self, dt):
        """Captura teclas presionadas"""
        self.previous_keys_pressed = self.keys_pressed.copy()

        try:
            keys = pygame.key.get_pressed()
        except pygame.error:
            return

        self.keys_pressed = {
            InputAction.UP: keys[pygame.K_w] or keys[pygame.K_UP],
            InputAction.DOWN: keys[pygame.K_s] or keys[pygame.K_DOWN],
            InputAction.LEFT: keys[pygame.K_a] or keys[pygame.K_LEFT],
            InputAction.RIGHT: keys[pygame.K_d] or keys[pygame.K_RIGHT],
            InputAction.ATTACK: keys[pygame.K_SPACE],
            InputAction.PARRY: keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT],
            InputAction.TOGGLE_COLLIDERS: keys[pygame.K_k],
            InputAction.CYCLE_CAMERA: keys[pygame.K_c],
        }

        self.input_direction = Vector2(0, 0)

        if self.keys_pressed[InputAction.UP]:
            self.input_direction.y = -1
        if self.keys_pressed[InputAction.DOWN]:
            self.input_direction.y = 1
        if self.keys_pressed[InputAction.LEFT]:
            self.input_direction.x = -1
        if self.keys_pressed[InputAction.RIGHT]:
            self.input_direction.x = 1

        # Normaliza diagonal
        if self.input_direction.magnitude() > 0:
            self.input_direction = self.input_direction.normalize()

    def is_action_pressed(self, action: InputAction) -> bool:
        return self.keys_pressed[action]

    def get_movement_vector(self):
        return self.input_direction

    def is_moving(self):
        return self.input_direction.magnitude() > 0

    def is_attacking_pressed(self):
        return self.is_action_pressed(InputAction.ATTACK)

    def is_attacking_just_pressed(self) -> bool:
        """Detecta rising edge: tecla presionada en este frame pero no en el anterior"""
        return self.keys_pressed[InputAction.ATTACK] and not self.previous_keys_pressed[InputAction.ATTACK]

    def is_parrying_pressed(self):
        return self.is_action_pressed(InputAction.PARRY)

    def is_parrying_just_pressed(self) -> bool:
        """Detecta rising edge: tecla presionada en este frame pero no en el anterior"""
        return self.keys_pressed[InputAction.PARRY] and not self.previous_keys_pressed[InputAction.PARRY]

    def get_facing_direction(self):
        if self.input_direction.magnitude() > 0:
            return self.input_direction
        return Vector2(1, 0)

    def get_direction(self):
        return self.input_direction

    def is_toggle_colliders_just_pressed(self) -> bool:
        return self.keys_pressed[InputAction.TOGGLE_COLLIDERS] and not self.previous_keys_pressed[InputAction.TOGGLE_COLLIDERS]

    def is_cycle_camera_just_pressed(self) -> bool:
        return self.keys_pressed[InputAction.CYCLE_CAMERA] and not self.previous_keys_pressed[InputAction.CYCLE_CAMERA]