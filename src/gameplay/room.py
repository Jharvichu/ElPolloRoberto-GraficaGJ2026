from src.gameplay.map_loader import MapLoader
from typing import Tuple, Optional, List


class Room:
    """Gestiona una sala (mapa, spawners, colisiones, renderizado)"""

    def __init__(self, tmx_path: str):
        self.map_loader = MapLoader(tmx_path)
        self.tilemap = self.map_loader.get_tilemap()
        self.map_width, self.map_height = self.map_loader.get_map_size_pixels()

    def render(self, surface, camera_offset: Tuple[int, int] = (0, 0)):
        """Renderiza el mapa en la surface con offset de cámara"""
        offset_x, offset_y = camera_offset

        for layer in self.tilemap.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, gid in layer:
                    if gid:
                        tile = self.tilemap.get_tile_image_by_gid(gid)
                        if tile:
                            screen_x = x * self.tilemap.tilewidth + offset_x
                            screen_y = y * self.tilemap.tileheight + offset_y
                            surface.blit(tile, (screen_x, screen_y))

    def get_player_spawn(self) -> Optional[Tuple[float, float]]:
        """Retorna punto de spawn del jugador en esta sala"""
        return self.map_loader.get_player_spawn()

    def get_collision_objects(self) -> List[dict]:
        """Retorna objetos de colisión del mapa"""
        return self.map_loader.get_collision_objects()

    def get_enemy_spawners(self) -> List[dict]:
        """Retorna spawners de enemigos en esta sala"""
        return self.map_loader.get_enemy_spawners()

    def get_boss_spawns(self) -> List[dict]:
        """Retorna spawns de jefes en esta sala"""
        return self.map_loader.get_boss_spawns()
