# Sistema de Animación: Máquina de Estados (FSM) Reutilizable

## 📋 Descripción General

Se ha reestructurado completamente el sistema de animación para ser **genérico, reutilizable y totalmente desacoplado**. Usa un patrón de **Máquina de Estados (FSM)** como un verdadero componente ECS que puede aplicarse a cualquier entidad: jugador, enemigos, bosses, objetos, efectos visuales, etc.

### Características Clave

✅ **Máquina de estados genérica** — `AnimationStateMachineComponent` en `src/components/animation_state_machine.py`  
✅ **Transiciones por múltiples triggers**:
  - Velocidad (`velocity.magnitude() > threshold`)
  - Input/clicks (rising edge detection)
  - Timer/duración del estado
  - Eventos del EventBus
  - Flags personalizadas

✅ **Wildcard "any"** — transiciones válidas desde cualquier estado  
✅ **Callbacks** — `on_enter()` y `on_exit()` para lógica de transición  
✅ **Desacoplamiento total** — AnimationComponent solo maneja datos/render  
✅ **Sin doble avance de frame** — AnimationComponent se deshabilita cuando hay FSM  

---

## 🏗️ Arquitectura

### 1. AnimationComponent (src/components/animation.py)

**Responsabilidad**: Datos y render de frames (nada de lógica de estado).

```python
# Métodos principales:
animation.set_state(state_name)                           # Cambiar estado
animation.set_direction(direction)                        # Cambiar dirección con flip_map
animation.update_direction_from_velocity(velocity)        # Calcular dirección desde Vector2
animation.get_current_frame() -> pygame.Surface           # Retorna frame ya volteado
animation.update(dt)                                      # Avanza frame (sin transiciones)
```

**Parámetros**:
```python
AnimationComponent(
    base_path: str,                          # ruta al directorio de assets
    frame_duration: float = 0.1,             # segundos entre frames
    default_state: str = "idle",             # estado inicial
    directions: list = None,                 # ["down", "right", ...] o None
    flip_map: dict = None,                   # mapeo de direcciones a flips
)
```

**Cambios respecto a versión anterior**:
- ❌ Eliminado: `auto_transition_states` (parámetro y lógica)
- ❌ Eliminado: recibir `velocity` en `update()`
- ✅ Nuevo: `get_current_frame()` aplica flip_x/flip_y internamente
- ✅ Nuevo: `enabled=False` cuando hay FSM (previene doble actualización)

---

### 2. AnimationStateMachineComponent (src/components/animation_state_machine.py)

**Responsabilidad**: Orquestar transiciones de estado y coordinar con AnimationComponent.

```python
# Configurar estados
fsm.add_state(
    state_name="idle",
    duration=float('inf'),          # Duración infinita = sin auto-salida
    on_enter=callback,              # Se ejecuta al entrar
    on_exit=callback,               # Se ejecuta al salir
    face_velocity=True              # Actualizar dirección automáticamente
)

# Definir transiciones
fsm.add_transition(
    from_state="idle",
    to_state="run",
    condition=lambda entity: entity.get_component("VelocityComponent").velocity.magnitude() > 0.1
)

# Estados especiales (wildcard)
fsm.add_transition("any", "hurt", lambda entity: entity.hp <= 0)

# Flags para one-shot
fsm.set_flag("attack", True)
if fsm.consume_flag("attack"):  # Lee y resetea
    do_something()

# Vincular eventos
fsm.bind_event("entity_hurt", "hurt_flag")  # Cuando se publica event, flag se activa
fsm.add_transition("idle", "hurt", lambda entity: fsm.consume_flag("hurt_flag"))
```

**En el `update()` del juego**:
```python
entity.update(dt)  # Esto llama FSM.update() → Animation.update()
```

---

### 3. InputComponent (src/components/input.py)

**Nuevos métodos para edge detection**:
```python
input_comp.is_attacking_just_pressed()  # Rising edge (tecla presionada ESTE frame, no anterior)
input_comp.is_parrying_just_pressed()   # Rising edge
```

Esto permite transiciones por "click" real, no por "tecla sostenida".

---

### 4. SpriteComponent (src/components/sprite.py)

**Simplificado**: Ya no toca `animation.flip_x/flip_y`.

```python
# Antes:
if animation_comp:
    frame = animation_comp.get_current_frame()
    if animation_comp.flip_x:
        frame = pygame.transform.flip(frame, True, False)

# Ahora:
if animation_comp:
    frame = animation_comp.get_current_frame()  # Ya volteado
```

---

## 🎮 Cómo Usar: Ejemplo Player

```python
from src.entities.player import create_player

player = create_player(100, 100)

# Acceder a componentes
animation = player.get_component("AnimationComponent")
fsm = player.get_component("AnimationStateMachineComponent")
velocity = player.get_component("VelocityComponent")
input_comp = player.get_component("InputComponent")

# En tu game loop:
for entity in entities:
    entity.update(dt)  # Esto actualiza FSM, que a su vez actualiza Animation

# Acceso manual si es necesario:
if fsm.is_in_state("attack"):
    print(f"Ataque lleva {fsm.state_elapsed():.2f}s")

if fsm.state_remaining() < 0.1:
    print("Ataque casi termina")
```

---

## 👾 Ejemplo: Enemigo con FSM

```python
from src.core.entity import Entity
from src.components.animation import AnimationComponent
from src.components.animation_state_machine import AnimationStateMachineComponent
from src.components.velocity import VelocityComponent
from src.utils.vector2 import Vector2

def create_trol_with_fsm(x, y, player):
    enemy = Entity(x, y)
    
    velocity = VelocityComponent(max_speed=150)
    enemy.add_component("VelocityComponent", velocity)
    
    animation = AnimationComponent(
        base_path="assets/gfx/enemy/trol",
        frame_duration=0.15,
        default_state="idle",
        directions=["down", "right", "up"],
        flip_map={"left": ("right", True, False)}
    )
    animation.enabled = False
    animation.load_animation_set("idle")
    animation.load_animation_set("chase")
    animation.load_animation_set("hurt")
    enemy.add_component("AnimationComponent", animation)
    
    fsm = AnimationStateMachineComponent(enemy, initial_state="idle")
    
    fsm.add_state("idle", duration=float('inf'), face_velocity=True)
    fsm.add_state("chase", duration=float('inf'), face_velocity=True)
    fsm.add_state("hurt", duration=0.3)
    
    def distance_to_player():
        return (player.position - enemy.position).magnitude()
    
    fsm.add_transition("idle", "chase",
        lambda entity: distance_to_player() < 150)
    fsm.add_transition("chase", "idle",
        lambda entity: distance_to_player() > 200)
    
    # Transición por evento
    fsm.bind_event("entity_damaged", "got_hurt")
    fsm.add_transition("any", "hurt",
        lambda entity: fsm.consume_flag("got_hurt"))
    fsm.add_transition("hurt", "idle",
        lambda entity: fsm.state_elapsed() > 0.3)
    
    enemy.add_component("AnimationStateMachineComponent", fsm)
    
    return enemy

# En tu IA/game loop:
def update_trol(enemy, player, dt):
    velocity = enemy.get_component("VelocityComponent")
    fsm = enemy.get_component("AnimationStateMachineComponent")
    
    # Lógica de IA
    dist = (player.position - enemy.position).magnitude()
    if fsm.is_in_state("chase"):
        direction = (player.position - enemy.position).normalize()
        velocity.set_velocity(direction.x * 100, direction.y * 100)
    else:
        velocity.set_velocity(0, 0)
    
    # Update (FSM maneja la transición automáticamente)
    enemy.update(dt)
```

---

## 🎯 Transiciones: Casos de Uso Comunes

### 1. Velocidad
```python
fsm.add_transition("idle", "run",
    lambda entity: entity.get_component("VelocityComponent").velocity.magnitude() > 0.1)
fsm.add_transition("run", "idle",
    lambda entity: entity.get_component("VelocityComponent").velocity.magnitude() <= 0.1)
```

### 2. Input (Click)
```python
fsm.add_transition("idle", "attack",
    lambda entity: entity.get_component("InputComponent").is_attacking_just_pressed())
```

### 3. Timer
```python
fsm.add_state("attack", duration=0.4)
fsm.add_transition("attack", "idle",
    lambda entity: fsm.state_elapsed() > 0.4)
```

### 4. Evento (EventBus)
```python
fsm.bind_event("entity_hit", "take_damage")
fsm.add_transition("any", "hurt",
    lambda entity: fsm.consume_flag("take_damage"))
```

### 5. Condición Personalizada
```python
fsm.add_transition("idle", "flee",
    lambda entity: entity.get_component("HealthComponent").hp < 20)
```

### 6. Wildcard (Cualquier Estado)
```python
fsm.add_transition("any", "death",
    lambda entity: entity.hp <= 0)
```

---

## 📦 Estructura de Directorios

### Con Direcciones (Player-like, Enemigos)

```
assets/gfx/entity_name/
├── state1/
│   ├── direction1/
│   │   ├── frame_00.png
│   │   ├── frame_01.png
│   │   └── ...
│   └── direction2/
│       ├── frame_00.png
│       └── ...
└── state2/
    └── direction1/
        └── ...
```

### Sin Direcciones (Efectos, NPCs)

```
assets/gfx/effect_name/
├── explosion/
│   ├── frame_00.png
│   ├── frame_01.png
│   └── ...
└── poof/
    ├── frame_00.png
    └── ...
```

---

## 🔧 API Completa de AnimationStateMachineComponent

### Configuración
- `add_state(name, duration, on_enter, on_exit, face_velocity)` — registra estado
- `add_transition(from, to, condition)` — registra transición
- `set_flag(name, value)` — establece flag
- `get_flag(name, default)` — obtiene flag
- `consume_flag(name)` — lee y resetea flag

### Runtime
- `update(dt)` — actualiza máquina (llamado automáticamente por entity.update)
- `force_state(new_state)` — fuerza estado inmediato

### Query
- `get_current_state()` — estado actual
- `is_in_state(state)` — ¿está en estado?
- `state_elapsed()` — segundos en estado actual
- `state_remaining()` — segundos faltantes
- `has_state(state)` — ¿existe estado?
- `get_all_states()` — lista de estados

---

## 📝 Notas Importantes

1. **AnimationComponent.enabled = False**: Cuando una entidad tiene FSM, su AnimationComponent debe tener `enabled=False` para evitar doble avance de frame. La FSM se encarga de llamar `animation.update(dt)` en su propio `update()`.

2. **Condiciones reciben entity**: Las lambdas de transición reciben la entidad completa, así pueden acceder a cualquier componente:
   ```python
   lambda entity: entity.get_component("HealthComponent").hp < 50
   ```

3. **Closures para FSM**: Dentro de lambdas, puedes usar `fsm` por closure:
   ```python
   fsm.add_transition("attack", "idle", lambda entity: fsm.state_elapsed() > 0.4)
   ```

4. **EventBus filtering**: `bind_event` filtra por `entity=self.entity`, así eventos de otras entidades no afectan.

5. **Flags consumibles**: `consume_flag()` lee y resetea en una llamada, ideal para one-shots:
   ```python
   if fsm.consume_flag("attack"):  # True una sola vez
       # hacer algo
   ```

---

## 🎨 Ejemplos de Estados Adicionales

### Attack (Ataque)
```python
# En PlayerAnimationStateMachine.update():
if self.is_attacking:
    animation_comp.set_state("attack")
    if self.state_timer > self.attack_duration:
        # Crear hitbox alrededor del player
        damage_area = create_damage_area(
            self.entity.position,
            animation_comp.current_direction,
            damage=10
        )
        self.is_attacking = False
```

### Block (Bloqueo)
```python
elif self.is_blocking and input_comp.is_parrying_pressed():
    animation_comp.set_state("block")
    
    # Reducir daño recibido
    collider = self.entity.get_component("ColliderComponent")
    collider.damage_reduction = 0.5  # 50% menos daño
```

### Dash (Esquiva Rápida)
```python
if input_comp.is_action_pressed(InputAction.DASH):
    animation_comp.set_state("dash")
    
    # Movimiento rápido en dirección actual
    direction = animation_comp.current_direction
    dash_speed = 400
    velocity_comp.set_velocity(
        dash_direction.x * dash_speed,
        dash_direction.y * dash_speed
    )
    
    # I-frames (invulnerabilidad temporal)
    self.entity.is_invulnerable = True
    self.entity.invulnerable_timer = 0.3
```

### Hurt (Daño/Knockback)
```python
if self.entity.just_got_hit:
    animation_comp.set_state("hurt")
    self.state_timer = 0.0
    self.entity.just_got_hit = False
    
    # Knockback
    hit_direction = self.entity.hit_direction
    velocity_comp.set_velocity(
        hit_direction.x * 150,
        hit_direction.y * 150
    )
    
    # Parpadear (invulnerabilidad)
    self.entity.is_invulnerable = True
```

---

## 📚 Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `src/components/animation.py` | Quitado `auto_transition_states`, `get_current_frame()` aplica flip |
| `src/components/sprite.py` | Simplificado `render()`, no toca `flip_x` |
| `src/components/input.py` | Agregados `is_attacking_just_pressed()`, `is_parrying_just_pressed()` |
| `src/components/animation_state_machine.py` | **NUEVO** — FSM como Component |
| `src/entities/player.py` | Usa FSM, quita `auto_transition_states` |
| `src/ui/scene_game.py` | Elimina manejo especial de `animation.update(dt, velocity)` |
| `src/entities/enemies.py` | Quita parámetro `auto_transition_states=None` |
| `src/entities/bosses.py` | Quita parámetro `auto_transition_states=None` |
| `tests/test_components/test_animation.py` | **NUEVO** — Tests de AnimationComponent |
| `tests/test_components/test_animation_state_machine.py` | **NUEVO** — Tests de FSM |

---

## 🧪 Testing

**Ejecutar tests**:
```bash
pytest tests/ -v
```

**Verificar sistema de animación**:
```bash
python verify_animation_system.py
```

**Cobertura**:
- 10 tests de `AnimationComponent` (frame advance, direction, flip, render)
- 15 tests de `AnimationStateMachineComponent` (transiciones, callbacks, flags, eventos)
- 58 tests totales en la suite

---

## 🔄 Migración desde Sistema Viejo

Si tienes una entidad con `auto_transition_states`:

```python
# VIEJO:
animation = AnimationComponent(
    base_path="assets/gfx/enemy/trol",
    auto_transition_states={0: "idle", 0.1: "run"}
)

# NUEVO:
animation = AnimationComponent(base_path="assets/gfx/enemy/trol")
animation.enabled = False

fsm = AnimationStateMachineComponent(entity, initial_state="idle")
fsm.add_state("idle", face_velocity=True)
fsm.add_state("run", face_velocity=True)
fsm.add_transition("idle", "run", lambda e: e.get_component("VelocityComponent").velocity.magnitude() > 0.1)
fsm.add_transition("run", "idle", lambda e: e.get_component("VelocityComponent").velocity.magnitude() <= 0.1)
entity.add_component("AnimationComponent", animation)
entity.add_component("AnimationStateMachineComponent", fsm)
```

---

## 🚀 Próximas Mejoras Posibles

- Integrar IA de enemigos usando FSM
- Agregar transiciones suavizadas (fade/cross-dissolve entre estados)
- Sistema de animación de combo (attack → attack2 → attack3)
- Predicción de transiciones (pre-load assets)
- Editor visual de FSM

---

**Última actualización**: 2026-06-24  
**Estado**: Completo y testeado  
**Autor**: Reestructuración de sistema de animación
