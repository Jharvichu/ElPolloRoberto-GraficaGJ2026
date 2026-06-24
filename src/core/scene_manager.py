class SceneManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.current_scene = None
        self._initialized = True

    def push_scene(self, scene):
        if self.current_scene:
            self.current_scene.on_exit()
        self.current_scene = scene
        scene.on_enter()

    def pop_scene(self):
        if self.current_scene:
            self.current_scene.on_exit()
            self.current_scene = None

    def handle_input(self, event):
        if self.current_scene:
            self.current_scene.handle_input(event)

    def update(self, dt):
        if self.current_scene:
            self.current_scene.update(dt)

    def render(self, surface):
        if self.current_scene:
            self.current_scene.render(surface)
