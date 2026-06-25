from src.core.game import Game
from src.ui.scene_map import MapScene

if __name__ == "__main__":
    juego = Game()
    juego.scene_manager.push_scene(MapScene())
    juego.run()