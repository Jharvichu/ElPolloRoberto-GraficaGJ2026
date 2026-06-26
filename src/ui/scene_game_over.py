import pygame
from src.core.scene import Scene
from src.core.scene_manager import SceneManager
from src.ui.scene_menu import MenuScene

class GameOverScene(Scene):
    def __init__(self):
        super().__init__()
        
        # cargar imagen de fondo
        try:
            self.bg = pygame.image.load("assets/gfx/imagen_perder.png").convert()
        except FileNotFoundError:
            print("Error: No se encontró assets/gfx/imagen_perder.png")
            self.bg = pygame.Surface((1280, 720))
            self.bg.fill((80, 0, 0)) 

        # fuentes
        pygame.font.init()
        self.font_title = pygame.font.SysFont("impact", 45) 
        self.font_prompt = pygame.font.SysFont("arial", 20, bold=True) 
        
        # textos
        self.text_color = (255, 100, 20) 
        
        # renderizamos dos líneas por separado
        self.title_line1 = self.font_title.render("TE HICIERON", True, self.text_color)
        self.title_shadow1 = self.font_title.render("TE HICIERON", True, (0, 0, 0)) 
        
        self.title_line2 = self.font_title.render("POLLO A LA BRASA", True, self.text_color)
        self.title_shadow2 = self.font_title.render("POLLO A LA BRASA", True, (0, 0, 0)) 
        
        self.prompt_surface = self.font_prompt.render("> Presiona ESPACIO o ENTER para volver al Menú <", True, (255, 255, 255))
        self.prompt_shadow = self.font_prompt.render("> Presiona ESPACIO o ENTER para volver al Menú <", True, (0, 0, 0))

        self.timer = 0.0
        self.show_prompt = True

    def on_enter(self):
        try:
            pygame.mixer.music.load("assets/bgm/cancion_perder.mp3")
            pygame.mixer.music.play(-1) 
        except pygame.error:
            print("Error: No se encontró assets/bgm/cancion_perder.mp3")

    def on_exit(self):
        pygame.mixer.music.stop()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                SceneManager().push_scene(MenuScene())

    def update(self, dt):
        self.timer += dt
        if self.timer >= 0.6: 
            self.show_prompt = not self.show_prompt
            self.timer = 0.0

    def render(self, surface):
        screen_w, screen_h = surface.get_size()
        bg_scaled = pygame.transform.scale(self.bg, (screen_w, screen_h))
        surface.blit(bg_scaled, (0, 0))
        
        # texto principal
        x_title = 40
        y_title1 = screen_h - 110 # Altura para la primera línea
        y_title2 = screen_h - 60  # Altura para la segunda línea
        
        # Dibujar Línea 1
        surface.blit(self.title_shadow1, (x_title + 3, y_title1 + 3))
        surface.blit(self.title_line1, (x_title, y_title1))
        
        # Dibujar Línea 2
        surface.blit(self.title_shadow2, (x_title + 3, y_title2 + 3))
        surface.blit(self.title_line2, (x_title, y_title2))
        
        # texto de indicacion
        if self.show_prompt:
            prompt_width = self.prompt_surface.get_width()
            x_prompt = screen_w - prompt_width - 40 # 40px de margen desde la derecha
            y_prompt = screen_h - 40
            
            surface.blit(self.prompt_shadow, (x_prompt + 2, y_prompt + 2))
            surface.blit(self.prompt_surface, (x_prompt, y_prompt))