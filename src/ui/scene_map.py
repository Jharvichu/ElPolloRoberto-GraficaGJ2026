from src.core.scene import Scene
from src.core.game import Game
from src.core.camera import Camera
from src.gameplay.room import Room
from src.entities.player import create_player, create_static_collider as factory_create_static_collider
from src.utils.constants import MOVE_SPEED, CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_SMOOTHING, SCREEN_WIDTH, SCREEN_HEIGHT
from src.components.collider import ColliderComponent


class MapScene(Scene):
    def __init__(self):
        super().__init__()
        self.game = Game()
        self.room = Room("assets/maps/levels/mapa.tmx")
        self.setup_player()
        self.setup_camera()
        self.create_static_colliders()

        # Guardar referencias a componentes para evitar búsquedas repetidas
        self.input_comp = self.player.get_component("InputComponent")
        self.velocity_comp = self.player.get_component("VelocityComponent")

    def handle_input(self, event):
        """Maneja eventos de entrada"""
        pass

    def update(self, dt):
        """Actualiza la escena"""
        self.camera.update(dt)

        # Guardar posición anterior para resolución de colisiones
        prev_x, prev_y = self.player.position.x, self.player.position.y

        # Actualizar entidades (incluyendo input)
        for entity in self.entities[:]:
            if entity.active:
                entity.update(dt)

        # Aplicar movimiento basado en input (después de que InputComponent se actualice)
        direction = self.input_comp.input_direction
        self.velocity_comp.set_velocity(direction.x * MOVE_SPEED, direction.y * MOVE_SPEED)

        # Manejar acciones especiales
        if self.input_comp.is_toggle_colliders_just_pressed():
            ColliderComponent.toggle_debug_global()

        # Resolver colisiones del jugador con paredes
        self.resolve_player_collisions(prev_x, prev_y)
    
    def render(self, surface):
        """Renderiza la escena"""
        surface.fill((40, 40, 40))
        camera_offset = self.camera.get_offset()
        self.room.render(surface, camera_offset)

        for entity in self.entities:
            if entity.active and entity.has_component('SpriteComponent'):
                sprite = entity.get_component('SpriteComponent')
                if sprite and hasattr(sprite, 'render'):
                    sprite.render(surface, camera_offset)

        for entity in self.entities:
            if entity.active and entity.has_component('ColliderComponent'):
                collider = entity.get_component('ColliderComponent')
                if collider and hasattr(collider, 'render_debug'):
                    collider.render_debug(surface, camera_offset)

    def setup_player(self):
        """Crea el jugador y lo posiciona en el spawn del mapa"""
        spawn_pos = self.room.get_player_spawn()
        self.player = create_player(spawn_pos[0], spawn_pos[1])
        self.add_entity(self.player)
        
    def setup_camera(self):
        """Configura la cámara para seguir al jugador"""
        self.camera = Camera(CAMERA_WIDTH, CAMERA_HEIGHT, self.room.map_width, self.room.map_height)
        self.camera.smoothing = CAMERA_SMOOTHING
        self.camera.set_target(self.player)
    
    def create_static_colliders(self):
        """Crea entidades de colisión basadas en los datos del mapa"""
        collision_objects = self.room.get_collision_objects()
        for collision_data in collision_objects:
            collider_entity = factory_create_static_collider(
                collision_data["x"],
                collision_data["y"],
                collision_data["width"],
                collision_data["height"]
            )
            self.add_entity(collider_entity)

    def resolve_player_collisions(self, prev_x: float, prev_y: float):
        """Resuelve colisiones del jugador separando ejes X e Y"""
        player_collider = self.player.get_component("ColliderComponent")
        if not player_collider:
            return

        # Intentar revertir solo X si hay colisión
        if self.check_collisions_with_walls():
            self.player.position.x = prev_x
            # Si sigue colisionando, también revertir Y
            if self.check_collisions_with_walls():
                self.player.position.y = prev_y

    def check_collisions_with_walls(self) -> bool:
        """¿Colisiona el jugador con alguna pared?"""
        player_collider = self.player.get_component("ColliderComponent")

        for entity in self.entities:
            if entity is self.player or not entity.active:
                continue

            wall_collider = entity.get_component("ColliderComponent")
            if wall_collider and player_collider.check_collision(wall_collider):
                return True

        return False
