class EventBus:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._subscribers = {}
        self._initialized = True

    def subscribe(self, event_name: str, callback):
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback):
        if event_name in self._subscribers:
            self._subscribers[event_name].remove(callback)

    def publish(self, event_name: str, **data):
        if event_name in self._subscribers:
            for callback in self._subscribers[event_name]:
                callback(**data)
