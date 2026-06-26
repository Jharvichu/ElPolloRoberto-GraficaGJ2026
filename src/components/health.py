from src.core.component import Component
from src.core.event_bus import EventBus


class HealthComponent(Component):
    """Componente para gestionar la salud de una entidad."""

    def __init__(self, max_hp: int = 100, invincibility_duration: float = 0.0):
        super().__init__()
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.invincibility_duration = invincibility_duration
        self.invincibility_timer = 0.0

    def take_damage(self, amount: int, from_entity=None):
        """Restar salud."""
        self.current_hp = max(0, self.current_hp - amount)
        event_bus = EventBus()
        event_bus.publish(
            "entity_damaged",
            entity=self.entity,
            damage=amount,
            from_entity=from_entity,
            remaining_hp=self.current_hp
        )

        if self.current_hp <= 0:
            self.entity.active = False
            event_bus.publish("entity_died", entity=self.entity, killer=from_entity)

    def heal(self, amount: int):
        """Sumar salud."""
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        actual_heal = self.current_hp - old_hp

        if actual_heal > 0:
            event_bus = EventBus()
            event_bus.publish("entity_healed", entity=self.entity, amount=actual_heal)
