import pygame
from src.core.scene import Scene
from src.core.game import Game
from src.entities.player import create_player, clamp_player_position
from src.utils.constants import MOVE_SPEED


class GameScene(Scene):
    def __init__(self):
        super().__init__()
        self.game = Game()
        self.player = create_player(640, 360)
        self.game.add_entity(self.player)
        self.bg_color = (40, 40, 40)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            input_comp = self.player.get_component("InputComponent")
            if input_comp:
                input_comp.handle_key_down(event)
        elif event.type == pygame.KEYUP:
            input_comp = self.player.get_component("InputComponent")
            if input_comp:
                input_comp.handle_key_up(event)

    def update(self, dt):
        input_comp = self.player.get_component("InputComponent")
        velocity_comp = self.player.get_component("VelocityComponent")

        if input_comp and velocity_comp:
            direction = input_comp.get_direction()
            velocity_comp.set_velocity(direction.x * MOVE_SPEED, direction.y * MOVE_SPEED)

        self.player.update(dt)

        clamp_player_position(self.player)

    def render(self, surface):
        surface.fill(self.bg_color)
