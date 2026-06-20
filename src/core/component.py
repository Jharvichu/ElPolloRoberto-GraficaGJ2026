from abc import ABC, abstractmethod

class Component(ABC):
    """Base class para todos los componentes"""
    def __init__(self):
        self.entity = None
        self.enabled = True
    
    def attach(self, entity):
        self.entity = entity
    
    def update(self, dt):
        pass
    
    def on_enable(self):
        pass
    
    def on_disable(self):
        pass