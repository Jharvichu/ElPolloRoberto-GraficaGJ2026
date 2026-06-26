from enum import Enum
from src.core.component import Component
from src.utils.vector2 import Vector2


class AIState(Enum):
    IDLE = "idle"
    CHASE = "chase"
    ATTACK = "attack"


class AIComponent(Component):
    """Componente de IA para enemigos (FSM: IDLE → CHASE → ATTACK)."""

    def __init__(self, entity, config, player):
        super().__init__()
        self.entity = entity
        self.config = config
        self.player = player
        self.state = AIState.IDLE
        self.chase_timer = 0.0
        self.attack_timer = 0.0
        self.last_direction = Vector2(0, -1)

        # Para desacoplar proyectiles de la Scene
        self.pending_projectile = None

    def update(self, dt):
        """Actualizar IA: cambio de estados, movimiento, ataque."""
        if not self.entity.active or not self.player.active:
            return

        distance_to_player = (self.player.position - self.entity.position).magnitude()

        # Transiciones de estado
        if distance_to_player < self.config.attack_range:
            self.state = AIState.ATTACK
        elif distance_to_player < self.config.chase_range:
            self.state = AIState.CHASE
        else:
            self.state = AIState.IDLE

        # Comportamiento por estado
        if self.state == AIState.IDLE:
            self._handle_idle()
        elif self.state == AIState.CHASE:
            self._handle_chase(self.player)
        elif self.state == AIState.ATTACK:
            self._handle_attack(self.player, dt)

    def _handle_idle(self):
        """Estado IDLE: no hacer nada."""
        velocity = self.entity.get_component("VelocityComponent")
        if velocity:
            velocity.set_velocity(0, 0)

    def _handle_chase(self, player):
        """Estado CHASE: perseguir al jugador con evitación de obstáculos."""
        direction = (player.position - self.entity.position).normalize()

        # Aplicar evitación de obstáculos (steering)
        adjusted_direction = self._apply_obstacle_avoidance(direction)

        self.last_direction = adjusted_direction

        velocity = self.entity.get_component("VelocityComponent")
        if velocity:
            velocity.set_velocity(
                adjusted_direction.x * self.config.max_speed,
                adjusted_direction.y * self.config.max_speed
            )

        # Actualizar animación
        animation = self.entity.get_component("AnimationComponent")
        if animation:
            animation.update_direction_from_velocity(adjusted_direction)

    def _apply_obstacle_avoidance(self, desired_direction: Vector2) -> Vector2:
        """Ajusta dirección si hay un obstáculo cercano (reducción suave de velocidad)."""
        # Este método se mantiene simple: la resolución de colisiones en la escena
        # se encarga de evitar que los enemigos atraviesen paredes.
        # La evitación principal se hace con el "sliding" en resolve_enemy_collisions.
        return desired_direction

    def _handle_attack(self, player, dt):
        """Estado ATTACK: disparar (Barbaran) o contacto (Galarreta)."""
        self.attack_timer -= dt

        # Galarreta: ataque cuerpo a cuerpo (solo reduce velocidad)
        if self.config.name == "Galarreta":
            velocity = self.entity.get_component("VelocityComponent")
            if velocity:
                velocity.set_velocity(0, 0)
            # El daño se aplica por contacto en la escena

        # Barbaran: dispara proyectiles
        elif self.config.name == "Barbaran":
            velocity = self.entity.get_component("VelocityComponent")
            if velocity:
                velocity.set_velocity(0, 0)

            if self.attack_timer <= 0:
                self.attack_timer = self.config.attack_cooldown
                direction = (player.position - self.entity.position).normalize()

                # Crear proyectil
                from src.entities.projectiles import create_enemy_projectile
                self.pending_projectile = create_enemy_projectile(
                    self.entity.position.x,
                    self.entity.position.y,
                    direction,
                    self.entity,
                    self.config
                )
