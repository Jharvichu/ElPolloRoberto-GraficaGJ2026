import pygame
import sys
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from src.core.scene_manager import SceneManager


class Game:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.scene_manager = SceneManager()
        self._initialized = True

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            self.scene_manager.handle_input(event)

    def update(self, dt):
        self.scene_manager.update(dt)

    def draw(self):
        self.scene_manager.render(self.screen)
        pygame.display.flip()

    def run(self):
        while self.is_running:
            dt = self.clock.tick(FPS) / 1000.0
            self.process_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()