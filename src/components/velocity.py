from src.core.component import Component
from src.utils.vector2 import Vector2


class VelocityComponent(Component):
    """Gestiona velocidad, aceleración y movimiento"""
    
    def __init__(self, max_speed=300, acceleration=1.0, friction=0.95):
        super().__init__()
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.max_speed = max_speed
        self.friction = friction  # 0-1, qué tan rápido se detiene
    
    def set_velocity(self, vx, vy):
        self.velocity = Vector2(vx, vy)
    
    def add_velocity(self, vx, vy):
        self.velocity.x += vx
        self.velocity.y += vy
    
    def set_acceleration(self, ax, ay):
        self.acceleration = Vector2(ax, ay)
    
    def apply_force(self, fx, fy):
        """Aplica fuerza (suma a aceleración)"""
        self.acceleration.x += fx
        self.acceleration.y += fy
    
    def clamp_speed(self):
        """Limita velocidad al máximo"""
        mag = self.velocity.magnitude()
        if mag > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed
    
    def update(self, dt):
        # v = v + a*dt
        self.velocity += self.acceleration * dt
        
        # Limita velocidad
        self.clamp_speed()
        
        # Actualiza posición
        self.entity.position += self.velocity * dt
        
        # Fricción (disminuye aceleración)
        self.acceleration *= self.friction
    
    def stop(self):
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)