import math
from src.core.component import Component
from src.utils.vector2 import Vector2


class TransformComponent(Component):
    """Gestiona posición, rotación y escala de una entidad"""
    
    def __init__(self, x=0, y=0, rotation=0, scale=1.0):
        super().__init__()
        self.position = Vector2(x, y)
        self.rotation = rotation
        self.scale = scale
        self.previous_position = Vector2(x, y)
    
    def set_position(self, x, y):
        self.previous_position = self.position.copy()
        self.position = Vector2(x, y)
        self.entity.position = self.position
    
    def translate(self, dx, dy):
        self.set_position(self.position.x + dx, self.position.y + dy)
    
    def rotate(self, angle):
        self.rotation = (self.rotation + angle) % 360
    
    def set_rotation(self, angle):
        self.rotation = angle % 360
    
    def set_scale(self, scale):
        self.scale = max(0.1, scale)
    
    def get_forward(self):
        """Retorna Vector2 hacia la dirección que apunta"""
        rad = math.radians(self.rotation)
        return Vector2(math.cos(rad), math.sin(rad))