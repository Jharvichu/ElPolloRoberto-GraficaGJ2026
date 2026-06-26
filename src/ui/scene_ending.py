import pygame
from src.core.scene import Scene
from src.core.scene_manager import SceneManager
from src.ui.scene_menu import MenuScene

class FinalScene(Scene):
    def __init__(self):
        super().__init__()
        
        # cargar el comic
        try:
            self.comic = pygame.image.load("assets/gfx/escena_final.png").convert()
        except FileNotFoundError:
            print("Error: No se encontró assets/gfx/escena_final.png")
            self.comic = pygame.Surface((1280, 720))
            self.comic.fill((50, 50, 50))

        # configurar tiempo
        self.timer = 0.0
        self.panel_duration = 5.0
        self.total_duration = 24.0 

        # cortar la imagen en 4 segmentos
        w, h = self.comic.get_size()
        self.panel_w = w // 2
        self.panel_h = h // 2
        self.panel_rects = [
            pygame.Rect(0, 0, self.panel_w, self.panel_h),
            pygame.Rect(self.panel_w, 0, self.panel_w, self.panel_h),
            pygame.Rect(0, self.panel_h, self.panel_w, self.panel_h),
            pygame.Rect(self.panel_w, self.panel_h, self.panel_w, self.panel_h)
        ]

    def on_enter(self):
        self.timer = 0.0
        try:
            pygame.mixer.music.load("assets/bgm/escena_final_song.mp3")
            pygame.mixer.music.play()
        except pygame.error:
            print("Error: No se encontró assets/bgm/escena_final_song.mp3")

    def on_exit(self):
        pygame.mixer.music.stop()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                self.terminar_escena()

    def update(self, dt):
        self.timer += dt 
        
        if self.timer >= self.total_duration:
            self.terminar_escena()

    def terminar_escena(self):
        SceneManager().push_scene(MenuScene())

    def render(self, surface):
        surface.fill((0, 0, 0)) 
        screen_w, screen_h = surface.get_size()
        # viñetas cada 5 seg
        if self.timer < 20.0:
            current_panel_idx = int(self.timer // self.panel_duration)
            if current_panel_idx > 3:
                current_panel_idx = 3
            time_in_panel = self.timer % self.panel_duration
            panel_surface = self.comic.subsurface(self.panel_rects[current_panel_idx]).copy()
            # efecto Ken Burns (Zoom)
            zoom_factor = 1.0 + (time_in_panel / self.panel_duration) * 0.15
            target_w = int(screen_w * zoom_factor)
            target_h = int(screen_h * zoom_factor)
            scaled_panel = pygame.transform.smoothscale(panel_surface, (target_w, target_h))
            
            # Fade-in al inicio de cada viñeta
            alpha = 255
            if time_in_panel < 1.0:
                alpha = int(255 * (time_in_panel / 1.0))
            scaled_panel.set_alpha(alpha)

            rect = scaled_panel.get_rect(center=(screen_w // 2, screen_h // 2))
            surface.blit(scaled_panel, rect)

        # comic completo los ultimos 4 segs
        else:
            time_in_full = self.timer - 20.0
            # Escalar el cómic completo para que llene toda la ventana
            scaled_full = pygame.transform.smoothscale(self.comic, (screen_w, screen_h))
            # Efecto de fade-in rápido (0.5 seg) para que la transición entre la viñeta 4 y el plano general sea suave
            alpha = 255
            if time_in_full < 0.5:
                alpha = int(255 * (time_in_full / 0.5))
            scaled_full.set_alpha(alpha)
            rect = scaled_full.get_rect(center=(screen_w // 2, screen_h // 2))
            surface.blit(scaled_full, rect)