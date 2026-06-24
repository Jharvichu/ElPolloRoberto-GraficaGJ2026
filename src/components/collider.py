import pygame
from src.core.component import Component
from src.utils.constants import DEBUG_ENABLED, DEBUG_COLOR_SOLID, DEBUG_COLOR_TRIGGER, DEBUG_THICKNESS


class ColliderComponent(Component):
    """Gestiona colisiones y hitbox de una entidad"""
    def __init__(self, width, height, offset_x=0, offset_y=0, is_trigger=False, debug=None):
        super().__init__()
        self.width = width
        self.height = height
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.is_trigger = is_trigger
        self.debug = debug  # None = usar global, True/False = individual
        self.rect = pygame.Rect(0, 0, width, height)
    
    def get_rect(self):
        """Retorna rect actualizado"""
        self.rect.x = self.entity.position.x + self.offset_x
        self.rect.y = self.entity.position.y + self.offset_y
        return self.rect
    
    def check_collision(self, other_collider):
        """¿Colisiona con otro collider?"""
        return self.get_rect().colliderect(other_collider.get_rect())
    
    def get_collision_point(self, other_collider):
        """Retorna punto de colisión (Vector2)"""
        rect1 = self.get_rect()
        rect2 = other_collider.get_rect()
        
        if not rect1.colliderect(rect2):
            return None
        
        # Punto del centro del overlap
        overlap = rect1.clip(rect2)
        return (overlap.centerx, overlap.centery)
    
    def get_distance_to(self, other_collider):
        """Retorna distancia entre centros"""
        rect1 = self.get_rect()
        rect2 = other_collider.get_rect()
        
        dx = rect1.centerx - rect2.centerx
        dy = rect1.centery - rect2.centery
        
        import math
        return math.sqrt(dx**2 + dy**2)
    
    def set_size(self, width, height):
        """Cambia tamaño del collider"""
        self.width = width
        self.height = height
        self.rect.width = width
        self.rect.height = height
    
    def set_offset(self, x, y):
        """Cambia offset del collider respecto a position"""
        self.offset_x = x
        self.offset_y = y
    
    def contains_point(self, x, y):
        """¿Contiene punto?"""
        return self.get_rect().collidepoint(x, y)
    
    def get_center(self):
        """Retorna (x, y) del centro"""
        rect = self.get_rect()
        return (rect.centerx, rect.centery)
    
    def is_debug_enabled(self):
        """¿Debug activado para este collider?"""
        if self.debug is not None:
            return self.debug
        return ColliderComponent.DEBUG_ENABLED
    
    def render_debug(self, surface):
        """Dibuja contorno del collider (debug visual)"""
        if not self.is_debug_enabled():
            return
        
        rect = self.get_rect()
        color = self.DEBUG_COLOR_TRIGGER if self.is_trigger else self.DEBUG_COLOR_SOLID
        
        # Dibuja rect (contorno)
        pygame.draw.rect(surface, color, rect, self.DEBUG_THICKNESS)
        
        # Dibuja punto del centro
        center = self.get_center()
        pygame.draw.circle(surface, color, center, 3)
    
    @staticmethod
    def enable_debug_global():
        """Activa debug para todos los colliders"""
        ColliderComponent.DEBUG_ENABLED = True
    
    @staticmethod
    def disable_debug_global():
        """Desactiva debug para todos los colliders"""
        ColliderComponent.DEBUG_ENABLED = False
    
    @staticmethod
    def toggle_debug_global():
        """Alterna debug global"""
        ColliderComponent.DEBUG_ENABLED = not ColliderComponent.DEBUG_ENABLED