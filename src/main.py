from src.core.game import Game
from src.ui.scene_menu import MenuScene

if __name__ == "__main__":
    juego = Game()
    juego.scene_manager.push_scene(MenuScene())
    juego.run()