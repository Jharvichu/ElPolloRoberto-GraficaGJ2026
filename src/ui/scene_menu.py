import pygame
import sys
from src.core.scene import Scene
from src.core.scene_manager import SceneManager
from src.ui.scene_map import MapScene

class MenuScene(Scene):
    def __init__(self):
        super().__init__()
        self.font_menu = pygame.font.SysFont("arial", 36)
        self.opciones = ["Jugar", "Salir"]
        self.seleccion_actual = 0 

        # Cargar imagenes
        # Usamos convert_alpha() para que respete la transparencia de logo PNG
        try:
            self.fondo = pygame.image.load("assets/gfx/menu_fondo.png").convert()
            self.logo = pygame.image.load("assets/gfx/menu_logo.png").convert_alpha()
            self.logo = pygame.transform.scale(self.logo, (500, 200))
        except FileNotFoundError:
            print("No se encontraron fondo.png o logo.png en assets/gfx/. Usando colores por defecto.")
            self.fondo = None
            self.logo = None

    def on_enter(self):
        # Reproducir música
        # Este método se ejecuta automáticamente al abrir el juego
        try:
            pygame.mixer.music.load("assets/bgm/menu_song.mp3")
            # El -1 hace que la canción se repita en bucle infinito
            pygame.mixer.music.play(-1) 
        except pygame.error:
            print("No se encontró musica.mp3 en assets/bgm/")

    def on_exit(self):
        # Parar música
        # Este método se ejecuta justo antes de pasar al juego
        pygame.mixer.music.stop()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.seleccion_actual = (self.seleccion_actual - 1) % len(self.opciones)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.seleccion_actual = (self.seleccion_actual + 1) % len(self.opciones)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.ejecutar_accion()

    def ejecutar_accion(self):
        if self.seleccion_actual == 0:
            # Al hacer push_scene, se llamará a on_exit() y la música parará
            SceneManager().push_scene(MapScene())
        elif self.seleccion_actual == 1:
            pygame.quit()
            sys.exit()

    def update(self, dt):
        pass

    def render(self, surface):
        # Fondo
        if self.fondo:
            # Escalamos el fondo al tamaño exacto de la ventana por si es más pequeño/grande
            fondo_escalado = pygame.transform.scale(self.fondo, surface.get_size())
            surface.blit(fondo_escalado, (0, 0))
        else:
            surface.fill((20, 20, 20)) 

        # Logo
        if self.logo:
            # Lo centramos en la parte superior (Y = 200)
            rect_logo = self.logo.get_rect(center=(surface.get_width()//2, 150))
            surface.blit(self.logo, rect_logo)
        else:
            # Si no encuentra el logo, pone un texto amarillo
            font_title = pygame.font.SysFont("arial", 64, bold=True)
            texto_titulo = font_title.render("EL POLLO ROBERTO", True, (255, 200, 0))
            rect_titulo = texto_titulo.get_rect(center=(surface.get_width()//2, 150))
            surface.blit(texto_titulo, rect_titulo)

        # Opciones
        for i, opcion in enumerate(self.opciones):
            color = (255, 255, 255) 
            texto = opcion

            if i == self.seleccion_actual:
                color = (255, 200, 0)
                texto = f"> {opcion} <"

            texto_opcion = self.font_menu.render(texto, True, color)
            # Colocamos las opciones un poco más abajo (Y = 350)
            rect_opcion = texto_opcion.get_rect(center=(surface.get_width()//2, 350 + (i * 60)))
            surface.blit(texto_opcion, rect_opcion)