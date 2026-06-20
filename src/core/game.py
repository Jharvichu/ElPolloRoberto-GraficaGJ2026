import pygame
import sys
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, BG_COLOR

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.is_running = True
    
    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False

    def update(self):
        pass

    def draw(self):
        # Renderizado en pantalla
        self.screen.fill(BG_COLOR)
        pygame.display.flip()

    def run(self):
        # El Game Loop principal
        while self.is_running:
            self.process_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()