from abc import ABC, abstractmethod


class Scene(ABC):
    def __init__(self):
        self.active = True
        self.entities = []

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

    def add_entity(self, entity):
        self.entities.append(entity)

    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)
