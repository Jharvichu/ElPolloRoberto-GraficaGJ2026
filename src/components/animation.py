import pygame
import os
from src.core.component import Component
from src.utils.vector2 import Vector2


class AnimationComponent(Component):
    """
    Componente de animación genérico y reutilizable.

    Maneja datos de animación y render de frames (sin lógica de transición de estados).
    Las transiciones de estado las maneja AnimationStateMachineComponent (si se usa FSM)
    o se controlan manualmente desde código externo.
    """

    def __init__(
        self,
        base_path: str,
        frame_duration: float = 0.1,
        default_state: str = "idle",
        directions: list = None,
        flip_map: dict = None,
    ):
        """
        Args:
            base_path: ruta a assets, ej: "assets/gfx/player", "assets/gfx/enemy/trol"
            frame_duration: tiempo (segundos) entre frames, ej: 0.1
            default_state: estado inicial, ej: "idle"
            directions: lista de direcciones soportadas, ej: ["down", "right", "up"]
                       Si None, no maneja direcciones (estados sin dirección)
            flip_map: dict mapping direcciones lógicas a (dirección_real, flip_x, flip_y)
                     Ej: {"left": ("right", True, False), "up_left": ("up_right", True, False)}
                     Si None, no aplica flipping
        """
        super().__init__()
        self.base_path = base_path
        self.frame_duration = frame_duration
        self.animations = {}
        self.current_state = default_state
        self.current_direction = directions[0] if directions else None
        self.frame_index = 0
        self.frame_timer = 0.0
        self.flip_x = False
        self.flip_y = False
        self.directions = directions or []
        self.flip_map = flip_map or {}

    def load_animation_set(self, state: str, directions_override: list = None):
        """Carga frames de un estado desde disco."""
        state_path = os.path.join(self.base_path, state)
        if state not in self.animations:
            self.animations[state] = {}

        if not os.path.exists(state_path):
            return

        dirs_to_load = directions_override or self.directions

        if not dirs_to_load:
            # Sin direcciones: carga todos los .png del directorio directamente
            frames = []
            frame_files = sorted([f for f in os.listdir(state_path) if f.endswith('.png')])
            for frame_file in frame_files:
                frame_path = os.path.join(state_path, frame_file)
                try:
                    surface = pygame.image.load(frame_path).convert_alpha()
                    frames.append(surface)
                except Exception as e:
                    print(f"Error loading frame {frame_path}: {e}")
            if frames:
                self.animations[state][None] = frames  # None key para "sin dirección"
        else:
            # Con dirección: estructura state/direction/frame_##.png
            for direction in dirs_to_load:
                dir_path = os.path.join(state_path, direction)
                if os.path.isdir(dir_path):
                    frames = []
                    frame_files = sorted([f for f in os.listdir(dir_path) if f.endswith('.png')])
                    for frame_file in frame_files:
                        frame_path = os.path.join(dir_path, frame_file)
                        try:
                            surface = pygame.image.load(frame_path).convert_alpha()
                            frames.append(surface)
                        except Exception as e:
                            print(f"Error loading frame {frame_path}: {e}")
                    if frames:
                        self.animations[state][direction] = frames

    def set_state(self, new_state: str):
        """Cambia el estado manualmente (transición sin dirección)"""
        if new_state != self.current_state:
            self.current_state = new_state
            self.frame_index = 0
            self.frame_timer = 0.0
            if new_state not in self.animations:
                self.load_animation_set(new_state)

    def set_direction(self, direction: str):
        """Establece dirección manualmente, respetando flip_map"""
        if not self.directions:
            return

        if direction in self.flip_map:
            actual_dir, flip_x, flip_y = self.flip_map[direction]
            self.current_direction = actual_dir
            self.flip_x = flip_x
            self.flip_y = flip_y
        else:
            self.current_direction = direction
            self.flip_x = False
            self.flip_y = False

    def update_direction_from_velocity(self, velocity: Vector2):
        """Calcula dirección basada en velocity. Solo para player-like entities."""
        if not self.directions or velocity.magnitude() == 0:
            return

        # Mapeo de 8 direcciones cardinales
        all_directions = {
            "down":         Vector2(0, 1),
            "down_right":   Vector2(1, 1).normalize(),
            "right":        Vector2(1, 0),
            "up_right":     Vector2(1, -1).normalize(),
            "up":           Vector2(0, -1),
            "up_left":      Vector2(-1, -1).normalize(),
            "left":         Vector2(-1, 0),
            "down_left":    Vector2(-1, 1).normalize(),
        }

        normalized_vel = velocity.normalize()
        best_direction = self.current_direction or "down"
        best_dot = -2

        for dir_name, dir_vector in all_directions.items():
            dot = normalized_vel.x * dir_vector.x + normalized_vel.y * dir_vector.y
            if dot > best_dot:
                best_dot = dot
                best_direction = dir_name

        self.set_direction(best_direction)

    def update(self, dt):
        """Actualiza el frame actual (avance temporal)"""
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0.0
            current_frames = self.animations.get(self.current_state, {}).get(self.current_direction, [])
            if current_frames:
                self.frame_index = (self.frame_index + 1) % len(current_frames)

    def get_current_frame(self) -> pygame.Surface:
        """Retorna el frame actual (ya volteado según flip_x/flip_y) o None"""
        frames = self.animations.get(self.current_state, {}).get(self.current_direction, [])
        if not frames:
            return None

        frame = frames[self.frame_index]
        if self.flip_x or self.flip_y:
            frame = pygame.transform.flip(frame, self.flip_x, self.flip_y)
        return frame