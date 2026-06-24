from src.core.component import Component
from src.core.event_bus import EventBus


class AnimationStateMachineComponent(Component):
    """
    Máquina de estados para animaciones de cualquier entidad.

    Características:
    - Estados personalizables con duración, callbacks on_enter/on_exit
    - Transiciones condicionales (lambda que reciben la entidad)
    - Wildcard "any" para transiciones desde cualquier estado
    - Flags para condiciones de un solo disparo (eventos/clicks)
    - Vinculación con EventBus para reaccionar a eventos
    - Integración automática con AnimationComponent
    """

    def __init__(self, entity, initial_state="idle"):
        super().__init__()
        self.current_state = initial_state
        self.state_timer = 0.0
        self.previous_state = None

        # Configuración de estados
        self.states = {}
        self.transitions = []

        # Flags de acciones (para condiciones de un solo disparo)
        self.flags = {}

        # Event bindings
        self._event_subscriptions = {}

    def add_state(self, state_name: str, duration: float = float('inf'),
                  on_enter=None, on_exit=None, face_velocity: bool = False):
        """Agrega un estado a la máquina"""
        self.states[state_name] = {
            "duration": duration,
            "on_enter": on_enter,
            "on_exit": on_exit,
            "face_velocity": face_velocity,
        }

    def add_transition(self, from_state: str, to_state: str, condition):
        """Agrega una transición entre estados"""
        self.transitions.append((from_state, to_state, condition))

    def set_flag(self, flag_name: str, value: bool = True):
        """Establece un flag (útil para click, evento, etc.)"""
        self.flags[flag_name] = value

    def get_flag(self, flag_name: str, default: bool = False) -> bool:
        """Obtiene el valor de un flag sin modificarlo"""
        return self.flags.get(flag_name, default)

    def consume_flag(self, flag_name: str, default: bool = False) -> bool:
        """Lee y resetea un flag en una sola llamada. Útil para condiciones de un solo disparo"""
        value = self.flags.get(flag_name, default)
        if flag_name in self.flags:
            self.flags[flag_name] = False
        return value

    def bind_event(self, event_name: str, flag_name: str):
        """Vincula un evento del EventBus con un flag de la FSM"""
        if event_name not in self._event_subscriptions:
            def event_callback(**data):
                if data.get("entity") is self.entity:
                    self.set_flag(flag_name, True)

            self._event_subscriptions[event_name] = (flag_name, event_callback)
            EventBus().subscribe(event_name, event_callback)

    def update(self, dt):
        """Actualiza la máquina de estados (llamado por Entity.update())"""
        self.state_timer += dt

        animation_comp = self.entity.get_component("AnimationComponent")
        if not animation_comp:
            return

        # Evaluar transiciones desde estado actual
        for from_state, to_state, condition in self.transitions:
            if from_state == self.current_state or from_state == "any":
                try:
                    if condition(self.entity):
                        self._change_state(to_state, animation_comp)
                        break  # Solo una transición por frame
                except Exception as e:
                    print(f"Error evaluando transición {from_state}->{to_state}: {e}")

        # Actualizar dirección si el estado lo requiere
        state_config = self.states.get(self.current_state, {})
        if state_config.get("face_velocity"):
            velocity_comp = self.entity.get_component("VelocityComponent")
            if velocity_comp:
                animation_comp.update_direction_from_velocity(velocity_comp.velocity)

        # Establecer animación
        animation_comp.set_state(self.current_state)
        animation_comp.update(dt)

    def _change_state(self, new_state: str, animation_comp):
        """Cambia de estado con callbacks"""
        if new_state not in self.states:
            print(f"Estado {new_state} no registrado en máquina")
            return

        # Callback de salida del estado anterior
        old_config = self.states.get(self.current_state, {})
        if old_config.get("on_exit"):
            old_config["on_exit"]()

        # Cambiar estado
        self.previous_state = self.current_state
        self.current_state = new_state
        self.state_timer = 0.0

        # Callback de entrada al nuevo estado
        new_config = self.states.get(new_state, {})
        if new_config.get("on_enter"):
            new_config["on_enter"]()

    def force_state(self, new_state: str):
        """Fuerza un cambio de estado inmediato (sin respetar condiciones)"""
        animation_comp = self.entity.get_component("AnimationComponent")
        if animation_comp:
            self._change_state(new_state, animation_comp)

    def get_current_state(self) -> str:
        """Retorna el estado actual"""
        return self.current_state

    def is_in_state(self, state: str) -> bool:
        """Retorna si está en el estado especificado"""
        return self.current_state == state

    def state_elapsed(self) -> float:
        """Retorna el tiempo que ha pasado en el estado actual"""
        return self.state_timer

    def state_remaining(self) -> float:
        """Retorna el tiempo que queda en el estado actual"""
        state_config = self.states.get(self.current_state, {})
        duration = state_config.get("duration", float('inf'))
        if duration == float('inf'):
            return float('inf')
        return max(0, duration - self.state_timer)

    def has_state(self, state: str) -> bool:
        """Retorna la existencia del estado"""
        return state in self.states

    def get_all_states(self) -> list:
        """Retorna lista de todos los estados registrados"""
        return list(self.states.keys())

    def on_disable(self):
        """Desuscribirse de todos los eventos al desactivar la máquina"""
        event_bus = EventBus()
        for event_name, (flag_name, callback) in self._event_subscriptions.items():
            event_bus.unsubscribe(event_name, callback)
        self._event_subscriptions.clear()
