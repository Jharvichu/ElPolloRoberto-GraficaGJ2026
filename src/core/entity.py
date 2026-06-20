from src.utils.vector2 import Vector2

class Entity:
    """Contenedor de componentes"""
    def __init__(self, x=0, y=0):
        self.position = Vector2(x, y)
        self.components = {}
        self.active = True
    
    def add_component(self, component_type, component):
        """Agrega componente: player.add_component(HealthComponent, HealthComponent(100))"""
        self.components[component_type] = component
        component.attach(self)
        component.on_enable()
        return component
    
    def get_component(self, component_type):
        """Obtiene componente: health = player.get_component(HealthComponent)"""
        return self.components.get(component_type)
    
    def has_component(self, component_type):
        return component_type in self.components
    
    def update(self, dt):
        for component in self.components.values():
            if component.enabled:
                component.update(dt)
    
    def destroy(self):
        self.active = False