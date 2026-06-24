from src.core.game import Game
from src.ui.scene_game import GameScene

if __name__ == "__main__":
    juego = Game()
    juego.scene_manager.push_scene(GameScene())
    juego.run()