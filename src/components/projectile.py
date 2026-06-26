from enum import Enum
from src.core.component import Component
from src.utils.vector2 import Vector2


class ProjectileState(Enum):
    OUTGOING = "outgoing"
    RETURNING = "returning"


class ProjectileComponent(Component):
    """Componente para proyectiles: boomerang del jugador y disparos de enemigos."""

    def __init__(self, entity, config, direction: Vector2, owner):
        super().__init__()
        self.entity = entity
        self.config = config
        self.owner = owner
        self.state = ProjectileState.OUTGOING
        self.elapsed = 0.0
        self.bounces = 0
        self.initial_position = entity.position.copy()
        self.has_hit_owner = False  # evitar que el dueño se dañe a sí mismo inmediatamente

    def update(self, dt: float):
        """Actualizar proyectil: TTL, lógica de retorno, movimiento."""
        self.elapsed += dt

        # TTL: autodestruirse al alcanzar max_lifetime
        if self.elapsed >= self.config.max_lifetime:
            self.entity.destroy()
            return

        # Boomerang: cambiar a returning tras max_lifetime/2 o distancia máxima
        if self.config.is_boomerang and self.state == ProjectileState.OUTGOING:
            dist_traveled = (self.entity.position - self.initial_position).magnitude()

            if self.elapsed >= self.config.max_lifetime / 2 or dist_traveled >= self.config.return_distance:
                self._switch_to_returning()

        # Aplicar movimiento según estado
        if self.state == ProjectileState.RETURNING and self.config.is_boomerang:
            # Boomerang retornando: acelerar hacia owner
            direction_to_owner = (self.owner.position - self.entity.position).normalize()
            velocity = self.entity.get_component("VelocityComponent")
            if velocity:
                velocity.set_velocity(
                    direction_to_owner.x * self.config.return_speed,
                    direction_to_owner.y * self.config.return_speed
                )
                velocity.clamp_speed()

    def on_wall_hit(self, collision_normal: Vector2):
        """Rebote en pared"""
        if self.config.max_bounces <= 0:
            self.entity.destroy()
            return

        self.bounces += 1
        if self.bounces > self.config.max_bounces:
            self.entity.destroy()
            return

        # Invertir velocidad según el eje de colisión (aproximado por la normal)
        velocity = self.entity.get_component("VelocityComponent")
        if velocity:
            # Si collision_normal apunta hacia X, invertir Vx; si hacia Y, invertir Vy
            if abs(collision_normal.x) > abs(collision_normal.y):
                velocity.velocity.x *= -1
            else:
                velocity.velocity.y *= -1

    def on_hit_entity(self, target):
        """Infligir daño a entidad impactada"""
        # Evitar autoimpactarse al disparar
        if target is self.owner and not self.has_hit_owner:
            self.has_hit_owner = True
            return

        health = target.get_component("HealthComponent")
        if health:
            health.take_damage(self.config.damage, from_entity=self.owner)

        # Proyectiles no boomerang se destruyen al impactar
        if not self.config.is_boomerang:
            self.entity.destroy()

    def _switch_to_returning(self):
        """Cambiar estado a returning (solo boomerang)."""
        self.state = ProjectileState.RETURNING
