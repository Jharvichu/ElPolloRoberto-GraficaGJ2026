import pygame
from src.core.scene import Scene
from src.core.game import Game
from src.core.camera import Camera
from src.core.scene_manager import SceneManager
from src.core.event_bus import EventBus
from src.gameplay.room import Room
from src.entities.player import create_player, create_static_collider as factory_create_static_collider
from src.entities.enemies import create_enemy_barbaran, create_enemy_galarreta, create_enemy_keiko
from src.entities.projectiles import create_boomerang
from src.utils.constants import MOVE_SPEED, CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_SMOOTHING
from src.utils.vector2 import Vector2
from src.components.collider import ColliderComponent
from src.config.player_config import PLAYER_CONFIG


class MapScene(Scene):
    def __init__(self):
        super().__init__()
        self.game = Game()
        self.room = Room("assets/maps/levels/mapa.tmx")

        # Control de spawn de Keiko (ANTES de setup_enemies)
        self.keiko_spawned = False
        self.boss_spawn_data = []

        self.setup_player()
        self.setup_camera()
        self.create_static_colliders()
        self.setup_enemies()

        # Guardar referencias a componentes para evitar búsquedas repetidas
        self.input_comp = self.player.get_component("InputComponent")
        self.velocity_comp = self.player.get_component("VelocityComponent")

        # Fuente para UI
        pygame.font.init()
        self.font_ui = pygame.font.SysFont("arial", 24, bold=True)

        # Suscribirse a evento de muerte del jugador
        event_bus = EventBus()
        event_bus.subscribe("entity_died", self._on_entity_died)

    def handle_input(self, event):
        pass

    def update(self, dt):
        """Actualiza la escena"""
        self.camera.update(dt)

        # Guardar posición anterior para resolución de colisiones
        prev_x, prev_y = self.player.position.x, self.player.position.y

        # Guardar posiciones anteriores de enemigos
        enemy_prev_positions = {}
        for entity in self.entities:
            if entity is not self.player and entity.active and entity.has_component("AIComponent"):
                enemy_prev_positions[id(entity)] = (entity.position.x, entity.position.y)

        # Actualizar entidades (incluyendo input, excluyendo IA de enemigos)
        for entity in self.entities[:]:
            if entity.active:
                # Actualizar componentes excepto AIComponent (se maneja aparte)
                for comp_name, component in entity.components.items():
                    if component.enabled and comp_name != "AIComponent":
                        component.update(dt)

        # Aplicar movimiento basado en input (después de que InputComponent se actualice)
        direction = self.input_comp.input_direction
        self.velocity_comp.set_velocity(direction.x * MOVE_SPEED, direction.y * MOVE_SPEED)

        # Manejar ataque del jugador (lanzar boomerang)
        self._handle_player_attack()

        # Actualizar IA de enemigos y recoger proyectiles pendientes
        self.update_enemy_ai(dt)

        # Actualizar proyectiles (movimiento, colisiones, TTL)
        self.update_projectiles(dt)

        # Verificar si el boomerang se destruyó, cambiar de vuelta a con sombrero
        if self.active_boomerang and not self.active_boomerang.active:
            self._set_player_animation_state("con_sombrero")
            self.active_boomerang = None

        # Manejar acciones especiales
        if self.input_comp.is_toggle_colliders_just_pressed():
            ColliderComponent.toggle_debug_global()

        # Resolver colisiones del jugador con paredes
        self.resolve_player_collisions(prev_x, prev_y)

        # Resolver colisiones de enemigos con paredes
        self.resolve_enemy_collisions(enemy_prev_positions)

        # Verificar contacto del jugador con enemigos cuerpo a cuerpo (Galarreta)
        self._check_player_enemy_contact()

        # Limpiar entidades inactivas
        self.entities = [e for e in self.entities if e.active]

        # Verificar si Keiko debe spawnear (todos los enemigos regulares eliminados)
        self._check_spawn_boss()
    
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

        # Renderizar vida del jugador en la esquina superior izquierda
        player_health = self.player.get_component("HealthComponent")
        if player_health:
            health_text = f"Vida: {player_health.current_hp}/{player_health.max_hp}"
            text_surface = self.font_ui.render(health_text, True, (50, 255, 50))
            surface.blit(text_surface, (20, 20))

    def setup_player(self):
        """Crea el jugador y lo posiciona en el spawn del mapa"""
        spawn_pos = self.room.get_player_spawn()
        self.player = create_player(spawn_pos[0], spawn_pos[1])
        self.add_entity(self.player)
        self.active_boomerang = None
        
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

    def setup_enemies(self):
        """Crea enemigos desde los spawners del mapa"""
        spawners = self.room.get_enemy_spawners()
        boss_spawners = self.room.get_boss_spawns()

        for spawner in spawners:
            enemy_type = spawner.get("type").lower()
            x = spawner["x"]
            y = spawner["y"]

            if enemy_type == "galarreta":
                enemy = create_enemy_galarreta(x, y, self.player)
                self.add_entity(enemy)
            elif enemy_type == "barbaran":
                enemy = create_enemy_barbaran(x, y, self.player)
                self.add_entity(enemy)

        # Guardar datos de spawners de Keiko para después
        for boss_spawn in boss_spawners:
            enemy_type = boss_spawn.get("name")
            if enemy_type == "keiko":
                self.boss_spawn_data.append(boss_spawn)

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

    def resolve_enemy_collisions(self, enemy_prev_positions: dict):
        """Resuelve colisiones de enemigos con paredes (separation + sliding)."""
        for entity in self.entities:
            if entity is self.player or not entity.active or not entity.has_component("AIComponent"):
                continue

            entity_id = id(entity)
            if entity_id not in enemy_prev_positions:
                continue

            prev_x, prev_y = enemy_prev_positions[entity_id]
            enemy_collider = entity.get_component("ColliderComponent")
            if not enemy_collider:
                continue

            # Si hay colisión, intentar estrategias de resolución
            if self._check_enemy_wall_collision(entity):
                # Estrategia 1: Sliding en X solamente
                entity.position.y = prev_y
                if not self._check_enemy_wall_collision(entity):
                    continue

                # Estrategia 2: Sliding en Y solamente
                entity.position.x = prev_x
                if not self._check_enemy_wall_collision(entity):
                    continue

                # Estrategia 3: Separation - separar ligeramente de la colisión
                entity.position.x = prev_x
                entity.position.y = prev_y

                # Encontrar el muro que colisiona y separarse de él
                for collider_entity in self.entities:
                    if collider_entity is entity or not collider_entity.active:
                        continue
                    if collider_entity.has_component("AIComponent") or collider_entity.has_component("ProjectileComponent"):
                        continue

                    wall_collider = collider_entity.get_component("ColliderComponent")
                    if wall_collider and enemy_collider.check_collision(wall_collider):
                        # Calcular dirección de separación
                        separation_vec = (entity.position - collider_entity.position).normalize()
                        entity.position.x += separation_vec.x * 5.0
                        entity.position.y += separation_vec.y * 5.0

                        # Si sigue colisionando, seguir separando
                        if self._check_enemy_wall_collision(entity):
                            entity.position.x += separation_vec.x * 5.0
                            entity.position.y += separation_vec.y * 5.0

                        break

    def _check_enemy_wall_collision(self, enemy) -> bool:
        """¿Colisiona el enemigo con alguna pared?"""
        enemy_collider = enemy.get_component("ColliderComponent")
        if not enemy_collider:
            return False

        for entity in self.entities:
            if entity is enemy or entity is self.player or not entity.active:
                continue

            # Solo revisar colliders estáticos (paredes), no otros enemigos ni proyectiles
            if entity.has_component("AIComponent") or entity.has_component("ProjectileComponent"):
                continue

            wall_collider = entity.get_component("ColliderComponent")
            if wall_collider and enemy_collider.check_collision(wall_collider):
                return True

        return False

    def _handle_player_attack(self):
        """Crea boomerang si el jugador presiona la tecla de ataque (máximo 1 activo)."""
        if not self.input_comp.is_attacking_just_pressed():
            return

        # Solo permitir un boomerang activo a la vez
        if self.active_boomerang and self.active_boomerang.active:
            return

        # Obtener dirección de disparo desde la animación del jugador
        facing_direction = self.get_player_facing_direction()

        # Crear boomerang
        boomerang = create_boomerang(
            self.player.position.x,
            self.player.position.y,
            facing_direction,
            self.player
        )
        self.add_entity(boomerang)
        self.active_boomerang = boomerang

        # Cambiar animación del jugador a sin sombrero
        self._set_player_animation_state("sin_sombrero")

    def get_player_facing_direction(self) -> Vector2:
        """Retorna la dirección hacia la que mira el jugador."""
        
        velocity = self.player.get_component("VelocityComponent")
        if velocity and velocity.velocity.magnitude() > 0:
            return velocity.velocity.normalize()

        animation = self.player.get_component("AnimationComponent")
        if animation and animation.current_direction:
            # Convertir nombre de dirección a vector
            direction_map = {
                "down":         Vector2(0, 1),
                "down_right":   Vector2(1, 1).normalize(),
                "right":        Vector2(1, 0),
                "up_right":     Vector2(1, -1).normalize(),
                "up":           Vector2(0, -1),
                "up_left":      Vector2(-1, -1).normalize(),
                "left":         Vector2(-1, 0),
                "down_left":    Vector2(-1, 1).normalize(),
            }
            if animation.current_direction in direction_map:
                return direction_map[animation.current_direction]

        # Fallback final: arriba
        return Vector2(0, -1)

    def update_enemy_ai(self, dt):
        """Actualiza la IA de todos los enemigos y maneja proyectiles pendientes."""
        for entity in self.entities:
            if entity is self.player or not entity.active:
                continue

            ai = entity.get_component("AIComponent")
            if ai:
                ai.update(dt)

                # Manejar proyectil único (Barbaran)
                if hasattr(ai, 'pending_projectile') and ai.pending_projectile:
                    self.add_entity(ai.pending_projectile)
                    ai.pending_projectile = None

                # Manejar múltiples proyectiles (Keiko)
                if hasattr(ai, 'pending_projectiles') and ai.pending_projectiles:
                    for projectile in ai.pending_projectiles:
                        self.add_entity(projectile)
                    ai.pending_projectiles.clear()

    def update_projectiles(self, dt):
        """Actualiza proyectiles: movimiento, colisiones y TTL."""
        for projectile in self.entities:
            if not projectile.active or projectile is self.player:
                continue

            projectile_comp = projectile.get_component("ProjectileComponent")
            if not projectile_comp:
                continue

            # Actualizar componente (TTL, estado boomerang)
            projectile_comp.update(dt)

            # Colisión con paredes (colliders estáticos)
            self._check_projectile_wall_collisions(projectile, projectile_comp)

            # Colisión con entidades dañables (enemigos/jugador)
            self._check_projectile_entity_collisions(projectile, projectile_comp)

    def _check_projectile_wall_collisions(self, projectile, projectile_comp):
        """Detecta colisiones de proyectil con paredes."""
        proj_collider = projectile.get_component("ColliderComponent")
        if not proj_collider:
            return

        for entity in self.entities:
            if entity is projectile or entity is self.player or not entity.active:
                continue

            # Revisar solo colliders estáticos (paredes)
            if entity.has_component("AIComponent"):
                continue  # Saltar enemigos aquí, se manejan aparte

            wall_collider = entity.get_component("ColliderComponent")
            if wall_collider and proj_collider.check_collision(wall_collider):
                # Calcular normal de colisión aproximada
                collision_point = proj_collider.get_collision_point(wall_collider)
                if collision_point:
                    normal = (Vector2(collision_point[0], collision_point[1]) - projectile.position).normalize()
                    projectile_comp.on_wall_hit(normal)
                else:
                    projectile_comp.on_wall_hit(Vector2(1, 0))

    def _check_projectile_entity_collisions(self, projectile, projectile_comp):
        """Detecta colisiones de proyectil con entidades (usa triggers para daño)."""
        proj_collider = projectile.get_component("ColliderComponent")
        if not proj_collider:
            return

        # Proyectil del jugador impacta enemigos (usar trigger del enemigo)
        if hasattr(projectile, 'is_boomerang') and projectile.is_boomerang:
            for entity in self.entities:
                if entity is projectile or entity is self.player or not entity.active:
                    continue

                if not entity.has_component("AIComponent"):
                    continue

                # Usar TriggerComponent si existe, sino usar ColliderComponent
                entity_trigger = entity.get_component("TriggerComponent") or entity.get_component("ColliderComponent")
                if entity_trigger and proj_collider.check_collision(entity_trigger):
                    projectile_comp.on_hit_entity(entity)

        # Proyectiles de enemigos impactan al jugador (usar trigger del jugador)
        else:
            player_trigger = self.player.get_component("TriggerComponent") or self.player.get_component("ColliderComponent")
            if player_trigger and proj_collider.check_collision(player_trigger):
                projectile_comp.on_hit_entity(self.player)

    def _set_player_animation_state(self, state: str):
        """Cambia la animación del jugador (con_sombrero o sin_sombrero)."""
        animation = self.player.get_component("AnimationComponent")
        if not animation:
            return

        # Mapeo de estados a carpetas de assets
        asset_paths = {
            "con_sombrero": "assets/gfx/pollo_con_sombrero",
            "sin_sombrero": "assets/gfx/pollo_sin_sombrero",
        }

        if state not in asset_paths:
            return

        # Cambiar la base_path y recargar las animaciones
        new_path = asset_paths[state]
        animation.base_path = new_path

        # Recargar los estados de animación disponibles
        animation.animations.clear()
        for anim_state in ["idle", "run"]:
            try:
                animation.load_animation_set(anim_state)
            except Exception:
                pass  # Si no existe el estado, simplemente ignorar

        # Ajustar escala según el estado de animación
        if state in PLAYER_CONFIG.ANIMATION_SCALE:
            transform = self.player.get_component("TransformComponent")
            if transform:
                transform.scale = PLAYER_CONFIG.ANIMATION_SCALE[state]

    def _check_player_enemy_contact(self):
        """Detecta contacto del jugador con enemigos (Galarreta hace daño cuerpo a cuerpo)."""
        from src.components.ai import AIState

        # Usar trigger del jugador para detectar daño
        player_trigger = self.player.get_component("TriggerComponent") or self.player.get_component("ColliderComponent")
        if not player_trigger:
            return

        for entity in self.entities:
            if entity is self.player or not entity.active:
                continue

            # Solo revisar enemigos con AIComponent
            ai = entity.get_component("AIComponent")
            if not ai or ai.state != AIState.ATTACK:
                continue

            # Solo Galarreta hace daño por contacto
            if ai.config.name != "Galarreta":
                continue

            # Usar trigger del enemigo
            entity_trigger = entity.get_component("TriggerComponent") or entity.get_component("ColliderComponent")
            if entity_trigger and player_trigger.check_collision(entity_trigger):
                # Aplicar daño al jugador
                player_health = self.player.get_component("HealthComponent")
                if player_health:
                    player_health.take_damage(ai.config.damage_to_player, entity)

    def _check_spawn_boss(self):
        """Verifica si todos los enemigos regulares están muertos. Si es así, spawnea a Keiko."""
        if self.keiko_spawned or not self.boss_spawn_data:
            return

        # Contar enemigos regulares (Galarreta y Barbaran) activos
        regular_enemies_alive = 0
        for entity in self.entities:
            if entity is self.player or not entity.active:
                continue
            ai = entity.get_component("AIComponent")
            if ai and ai.config.name in ["Galarreta", "Barbaran"]:
                regular_enemies_alive += 1

        # Si no hay enemigos regulares vivos, spawnear a Keiko
        if regular_enemies_alive == 0:
            self.keiko_spawned = True
            for boss_spawn in self.boss_spawn_data:
                x = boss_spawn["x"]
                y = boss_spawn["y"]
                enemy = create_enemy_keiko(x, y, self.player)
                self.add_entity(enemy)

    def _on_entity_died(self, entity=None, **kwargs):
        """Callback cuando una entidad muere. Si es el jugador, ir a game over. Si es Keiko, ir a ending."""
        if entity is self.player:
            from src.ui.scene_game_over import GameOverScene
            SceneManager().push_scene(GameOverScene())
        elif entity and entity.has_component("AIComponent"):
            ai = entity.get_component("AIComponent")
            if ai and ai.config.name == "Keiko":
                from src.ui.scene_ending import FinalScene
                SceneManager().push_scene(FinalScene())
