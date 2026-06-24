import pygame
from src.core.component import Component


class SpriteComponent(Component):
    """Renderiza imagen de la entidad"""
    
    def __init__(self, image_path=None, width=32, height=32):
        super().__init__()
        self.width = width
        self.height = height
        self.original_image = None
        self.image = None
        self.rotation = 0
        self.flip_x = False
        self.flip_y = False
        self.alpha = 255
        
        if image_path:
            self.load_image(image_path)
        else:
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            self.image.fill((255, 255, 255, 255))
            self.original_image = self.image.copy()
    
    def load_image(self, image_path):
        """Carga imagen desde archivo"""
        try:
            self.original_image = pygame.image.load(image_path)
            self.original_image = pygame.transform.scale(
                self.original_image, (self.width, self.height)
            )
            self.image = self.original_image.copy()
        except pygame.error as e:
            print(f"Error cargando imagen {image_path}: {e}")
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.image.fill((255, 255, 255, 255))
            self.original_image = self.image.copy()
    
    def set_image(self, surface):
        """Establece imagen directamente desde Surface"""
        self.original_image = surface
        self.image = surface.copy()
    
    def get_rect(self):
        """Retorna rect para renderizado"""
        return self.image.get_rect(topleft=(
            self.entity.position.x,
            self.entity.position.y
        ))
    
    def rotate(self, angle):
        """Rota la imagen"""
        self.rotation = angle % 360
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
    
    def set_rotation(self, angle):
        self.rotate(angle)
    
    def flip(self, horizontal=False, vertical=False):
        """Voltea imagen"""
        self.flip_x = horizontal
        self.flip_y = vertical
        self.image = pygame.transform.flip(
            self.original_image,
            self.flip_x,
            self.flip_y
        )
    
    def set_alpha(self, alpha):
        """Establece transparencia 0-255"""
        self.alpha = max(0, min(255, alpha))
        self.image.set_alpha(self.alpha)
    
    def render(self, surface):
        """Dibuja en pantalla"""
        if not self.entity:
            return

        animation_comp = self.entity.get_component("AnimationComponent")
        if animation_comp:
            frame = animation_comp.get_current_frame()
            if frame:
                surface.blit(frame, (self.entity.position.x, self.entity.position.y))
                return

        if self.image:
            rect = self.get_rect()
            surface.blit(self.image, rect)
    
    def set_size(self, width, height):
        """Redimensiona sprite"""
        self.width = width
        self.height = height
        self.original_image = pygame.transform.scale(
            self.original_image, (width, height)
        )
        self.image = self.original_image.copy()