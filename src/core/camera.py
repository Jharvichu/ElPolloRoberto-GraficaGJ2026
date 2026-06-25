import pygame
from typing import Tuple, Optional


class Camera:
    def __init__(self, width: int, height: int, map_width: int, map_height: int):
        """
        Cámara que sigue a un objetivo manteniéndolo centrado.

        Args:
            width: Ancho de la cámara en píxeles (tamaño visible)
            height: Alto de la cámara en píxeles (tamaño visible)
            map_width: Ancho total del mapa en píxeles
            map_height: Alto total del mapa en píxeles
        """
        self.width = width
        self.height = height
        self.map_width = map_width
        self.map_height = map_height

        self.x = 0.0
        self.y = 0.0

        self.target = None
        self.smoothing = 0.15

    def set_target(self, entity):
        self.target = entity

    def update(self, dt: float = 0):
        if self.target is None:
            return

        if hasattr(self.target, "position"):
            target_x = self.target.position.x
            target_y = self.target.position.y
        else:
            target_x = self.target[0]
            target_y = self.target[1]

        sprite_comp = None
        if hasattr(self.target, "get_component"):
            sprite_comp = self.target.get_component("SpriteComponent")

        if sprite_comp:
            center_x = target_x + sprite_comp.width / 2
            center_y = target_y + sprite_comp.height / 2
        else:
            center_x = target_x
            center_y = target_y

        desired_x = center_x - self.width / 2
        desired_y = center_y - self.height / 2

        self.x += (desired_x - self.x) * self.smoothing
        self.y += (desired_y - self.y) * self.smoothing

        self._clamp()

    def _clamp(self):
        self.x = max(0, min(self.x, self.map_width - self.width))
        self.y = max(0, min(self.y, self.map_height - self.height))

    def get_offset(self) -> Tuple[int, int]:
        return (-int(self.x), -int(self.y))

    def is_in_view(self, x: float, y: float, width: float = 0, height: float = 0) -> bool:
        return (
            x + width > self.x and
            x < self.x + self.width and
            y + height > self.y and
            y < self.y + self.height
        )

    def set_size(self, width: int, height: int):
        self.width = width
        self.height = height
        self._clamp()

    def get_viewport_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        screen_x = int(world_x - self.x)
        screen_y = int(world_y - self.y)
        return (screen_x, screen_y)

    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        world_x = screen_x + self.x
        world_y = screen_y + self.y
        return (world_x, world_y)
