import pygame


class AssetManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._surfaces = {}
        self._sounds = {}
        self._initialized = True

    def load_surface(self, path: str) -> pygame.Surface:
        if path not in self._surfaces:
            try:
                self._surfaces[path] = pygame.image.load(path)
            except pygame.error as e:
                print(f"Error loading surface {path}: {e}")
                return None
        return self._surfaces[path]

    def load_sound(self, path: str) -> pygame.mixer.Sound:
        if path not in self._sounds:
            try:
                self._sounds[path] = pygame.mixer.Sound(path)
            except pygame.error as e:
                print(f"Error loading sound {path}: {e}")
                return None
        return self._sounds[path]

    def get_surface(self, path: str) -> pygame.Surface:
        if path in self._surfaces:
            return self._surfaces[path]
        return self.load_surface(path)

    def get_sound(self, path: str) -> pygame.mixer.Sound:
        if path in self._sounds:
            return self._sounds[path]
        return self.load_sound(path)

    def clear(self):
        self._surfaces.clear()
        self._sounds.clear()
