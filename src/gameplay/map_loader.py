import pytmx
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class MapLoader:
    """Cargador de mapas TMX usando pytmx"""

    def __init__(self, tmx_path: str):
        self.tilemap = pytmx.load_pygame(tmx_path)

    def get_tilemap(self):
        return self.tilemap

    def get_map_size_pixels(self) -> Tuple[int, int]:
        """Retorna tamaño del mapa en píxeles"""
        return (self.tilemap.width * self.tilemap.tilewidth, self.tilemap.height * self.tilemap.tileheight)

    def get_collision_objects(self) -> List[Dict]:
        """Retorna lista de objetos de colisión"""
        objects = []
        for layer in self.tilemap.objectgroups:
            if layer.name == "colisiones":
                for obj in layer:
                    objects.append({
                        "x": obj.x,
                        "y": obj.y,
                        "width": obj.width,
                        "height": obj.height,
                    })
        return objects

    def get_player_spawn(self) -> Optional[Tuple[float, float]]:
        """Retorna posición de spawn del jugador"""
        for layer in self.tilemap.objectgroups:
            if layer.name == "player_spawn":
                for obj in layer:
                    return (obj.x, obj.y)
        return None

    def get_enemy_spawners(self) -> List[Dict]:
        """Retorna lista de spawners de enemigos"""
        spawners = []
        for layer in self.tilemap.objectgroups:
            if layer.name == "spawners":
                for obj in layer:
                    spawners.append({
                        "type": obj.type,
                        "x": obj.x,
                        "y": obj.y,
                    })
        return spawners

    def get_boss_spawns(self) -> List[Dict]:
        """Retorna lista de spawns de jefes"""
        bosses = []
        for layer in self.tilemap.objectgroups:
            if layer.name == "boss_spawn":
                for obj in layer:
                    bosses.append({
                        "name": obj.name,
                        "type": obj.type,
                        "x": obj.x,
                        "y": obj.y,
                    })
        return bosses

