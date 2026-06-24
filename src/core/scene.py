from abc import ABC, abstractmethod


class Scene(ABC):
    def __init__(self):
        self.active = True

    @abstractmethod
    def handle_input(self, event):
        pass

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def render(self, surface):
        pass

    def on_enter(self):
        pass

    def on_exit(self):
        pass
