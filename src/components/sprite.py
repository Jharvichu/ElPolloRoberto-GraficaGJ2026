import pygame
from src.core.component import Component


class SpriteComponent(Component):
    """Renderiza imagen de la entidad"""
    
    def __init__(self, width=32, height=32, image_path=None):
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
        """Retorna rect para renderizado (centrado en position)"""
        return self.image.get_rect(center=(
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

    def _get_scaled_image(self, image):
        """Escala imagen según TransformComponent.scale_x y scale_y"""
        transform_comp = self.entity.get_component("TransformComponent")
        scale_x = transform_comp.scale_x if transform_comp else 1.0
        scale_y = transform_comp.scale_y if transform_comp else 1.0

        if scale_x == 1.0 and scale_y == 1.0:
            return image

        scaled_width = int(image.get_width() * scale_x)
        scaled_height = int(image.get_height() * scale_y)
        return pygame.transform.scale(image, (scaled_width, scaled_height))

    def render(self, surface, camera_offset=(0, 0)):
        """Dibuja en pantalla (centrado en position)"""
        if not self.entity:
            return

        offset_x, offset_y = camera_offset
        x = int(self.entity.position.x + offset_x)
        y = int(self.entity.position.y + offset_y)

        animation_comp = self.entity.get_component("AnimationComponent")
        if animation_comp:
            frame = animation_comp.get_current_frame()
            if frame:
                frame = self._get_scaled_image(frame)
                rect = frame.get_rect(center=(x, y))
                surface.blit(frame, rect)
                return

        if self.image:
            image_to_render = self._get_scaled_image(self.image)
            rect = image_to_render.get_rect(center=(x, y))
            surface.blit(image_to_render, rect)
    
    def set_size(self, width, height):
        """Redimensiona sprite"""
        self.width = width
        self.height = height
        self.original_image = pygame.transform.scale(
            self.original_image, (width, height)
        )
        self.image = self.original_image.copy()