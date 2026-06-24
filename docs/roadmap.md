# 🛣️ Roadmap del Proyecto: El Pollo Roberto

## Visión General

**El Pollo Roberto: La Vida Da Vueltas** es un roguelite de acción top-down, completamente funcional con:
- ✅ Sistema de animaciones genérico y reutilizable (FSM-based)
- ✅ Componentes ECS completos (Transform, Velocity, Animation, Sprite, Collider, etc.)
- ✅ Player con movimiento, boomerang y sistema de parry
- ✅ 3 tipos de enemigos con IA
- ✅ 3 bosses desafiantes
- ✅ Audio y efectos visuales integrados

---

## 📋 Expansión Futura de Animaciones del Player

### Estructura Actual
```
assets/gfx/player_test/
├── idle/       ✅ (4 frames)
└── run/        ✅ (6 frames)
```

### Estructura Propuesta (Roadmap)
```
assets/gfx/player/
├── idle/              (4 frames por dirección)
│   ├── down/
│   ├── down_right/
│   ├── right/
│   ├── up_right/
│   └── up/
│
├── run/               (6 frames por dirección)
│   ├── down/
│   ├── down_right/
│   ├── right/
│   ├── up_right/
│   └── up/
│
├── attack/            (4 frames por dirección) — NEW
│   ├── down/
│   ├── down_right/
│   ├── right/
│   ├── up_right/
│   └── up/
│
├── block/             (2 frames por dirección) — NEW
│   ├── down/
│   ├── down_right/
│   ├── right/
│   ├── up_right/
│   └── up/
│
├── dash/              (3 frames por dirección) — NEW
│   ├── down/
│   ├── down_right/
│   ├── right/
│   ├── up_right/
│   └── up/
│
├── hurt/              (2 frames knockback) — NEW
│   ├── down/
│   ├── down_right/
│   ├── right/
│   ├── up_right/
│   └── up/
│
├── throw/             (4 frames proyectil) — STRETCH
│   ├── down/
│   ├── down_right/
│   ├── right/
│   ├── up_right/
│   └── up/
│
└── death/             (4 frames) — STRETCH
    └── (sin dirección)
```

---

## 🎯 Cómo Agregar Nuevas Animaciones

### Paso 1: Crear Assets
1. Crea directorios según la estructura de arriba
2. Coloca PNG frames numerados: `frame_00.png`, `frame_01.png`, etc.

### Paso 2: Actualizar Player Factory
En `src/entities/player.py`:

```python
def create_player(x: float = 640, y: float = 360) -> Entity:
    player = Entity(x, y)
    # ... componentes existentes ...
    
    animation = AnimationComponent(
        base_path="assets/gfx/player",
        frame_duration=0.1,
        default_state="idle",
        directions=["down", "down_right", "right", "up_right", "up"],
        flip_map={...}
    )
    
    # Cargar TODOS los estados
    for state in ["idle", "run", "attack", "block", "dash", "hurt"]:
        animation.load_animation_set(state)
    
    animation.enabled = False
    player.add_component("AnimationComponent", animation)
    
    # ... resto del código ...
```

### Paso 3: Configurar Transiciones en FSM
En `_build_player_animation_fsm()`:

```python
def _build_player_animation_fsm(player: Entity) -> AnimationStateMachineComponent:
    fsm = AnimationStateMachineComponent(player, initial_state="idle")
    
    # Estados
    fsm.add_state("idle", duration=float('inf'), face_velocity=True)
    fsm.add_state("run", duration=float('inf'), face_velocity=True)
    fsm.add_state("attack", duration=0.4, face_velocity=False)
    fsm.add_state("block", duration=float('inf'), face_velocity=False)
    fsm.add_state("dash", duration=0.3, face_velocity=True)
    fsm.add_state("hurt", duration=0.3, face_velocity=False)
    
    # Transiciones: idle <-> run por velocidad
    fsm.add_transition("idle", "run",
        lambda entity: entity.get_component("VelocityComponent").velocity.magnitude() > 0.1)
    fsm.add_transition("run", "idle",
        lambda entity: entity.get_component("VelocityComponent").velocity.magnitude() <= 0.1)
    
    # Transiciones: a attack por input
    fsm.add_transition("idle", "attack",
        lambda entity: entity.get_component("InputComponent").is_attacking_just_pressed())
    fsm.add_transition("run", "attack",
        lambda entity: entity.get_component("InputComponent").is_attacking_just_pressed())
    fsm.add_transition("attack", "idle",
        lambda entity: fsm.state_elapsed() > 0.4)
    
    # Transiciones: block por input
    fsm.add_transition("idle", "block",
        lambda entity: entity.get_component("InputComponent").is_parrying_just_pressed())
    fsm.add_transition("run", "block",
        lambda entity: entity.get_component("InputComponent").is_parrying_just_pressed())
    fsm.add_transition("block", "idle",
        lambda entity: not entity.get_component("InputComponent").is_parrying_pressed())
    
    # Transición: hurt (desde cualquier estado excepto death)
    fsm.add_transition("any", "hurt",
        lambda entity: entity.hp_just_changed and not entity.just_died)
    fsm.add_transition("hurt", "idle",
        lambda entity: fsm.state_elapsed() > 0.3)
    
    # Transición: death (desde cualquier estado)
    fsm.add_transition("any", "death",
        lambda entity: entity.hp <= 0)
    
    return fsm
```

---

## 🎮 Estados por Implementar

### FASE 1: Attack (Simple)
- ✅ Estado de ataque con duración fija (0.4s)
- ✅ Transición desde idle/run con input
- ✅ Regresa a idle automáticamente
- ❓ Crear hitbox durante ataque

### FASE 2: Block/Parry (Medio)
- ✅ Estado de bloqueo indefinido
- ✅ Mantener bloqueando mientras se presiona tecla
- ✅ Reducir daño recibido 50%
- ❓ Animación diferente al parry

### FASE 3: Dash (Medio)
- ✅ Estado de dash con movimiento rápido
- ✅ Duración 0.3s
- ✅ I-frames (invulnerabilidad temporal)
- ❓ Efecto visual de velocidad

### FASE 4: Hurt (Simple)
- ✅ Estado de knockback/daño
- ✅ Duración 0.3s
- ✅ Parpadeo (invulnerabilidad)
- ❓ Knockback dirección

### FASE 5: Throw (Stretch)
- ❌ Estado de lanzar proyectil
- ❌ Animación diferente por dirección
- ❌ Integración con ProjectileComponent

### FASE 6: Death (Stretch)
- ❌ Animación de muerte (sin dirección)
- ❌ Game Over trigger
- ❌ Pantalla de retry

---

## 🔍 Validación

Test básico para cada estado nuevo:

```python
def test_player_block_animation():
    player = create_player(640, 360)
    animation = player.get_component("AnimationComponent")
    fsm = player.get_component("AnimationStateMachineComponent")
    input_comp = player.get_component("InputComponent")
    
    # Simular pulsación de parry
    input_comp.previous_keys_pressed = set()
    input_comp.keys_pressed = {pygame.K_LSHIFT}
    input_comp.update(0.016)
    
    # Trigger FSM
    player.update(0.016)
    
    # Verificar estado
    assert fsm.is_in_state("block")
    assert animation.current_state == "block"
    
    # Soltar tecla
    input_comp.previous_keys_pressed = {pygame.K_LSHIFT}
    input_comp.keys_pressed = set()
    input_comp.update(0.016)
    player.update(0.016)
    
    # Debe volver a idle
    assert fsm.is_in_state("idle")
```

---

## 📊 Distribución de Trabajo

| Fase | Estado | Frames | Transiciones | Esfuerzo | Duración |
|------|--------|--------|-------------|----------|----------|
| 1 | attack | 4×5 = 20 | 4 | BAJO | 1-2h |
| 2 | block | 2×5 = 10 | 4 | BAJO | 1h |
| 3 | dash | 3×5 = 15 | 2 | MEDIO | 1.5h |
| 4 | hurt | 2×5 = 10 | 4 | BAJO | 1h |
| 5 | throw | 4×5 = 20 | 2 | MEDIO | 2h |
| 6 | death | 4 | 1 | BAJO | 1h |

**Total**: ~165 frames, ~8h de trabajo (si assets ya existen)

---

## 🏗️ Arquitectura Recomendada para Futuras Mecánicas

### Componentes Necesarios
```
PlayerEntity
├── TransformComponent
├── VelocityComponent
├── InputComponent
├── ColliderComponent
├── HealthComponent          ← NEW
├── AnimationComponent
├── SpriteComponent
├── AnimationStateMachineComponent
├── CombatComponent          ← NEW (ataque, rango, cooldown)
├── ParryComponent           ← NEW (ventana de tiempo)
└── DashComponent            ← NEW (cooldown, i-frames)
```

### Lógica de Combate Centralizada
```python
class PlayerCombatController:
    def __init__(self, player):
        self.player = player
        self.fsm = player.get_component("AnimationStateMachineComponent")
        self.health = player.get_component("HealthComponent")
        self.combat = player.get_component("CombatComponent")
    
    def update(self, dt, enemies):
        # Detectar si debe atacar
        if self.fsm.is_in_state("attack"):
            hitbox = self.get_attack_hitbox()
            for enemy in enemies:
                if hitbox.colliderect(enemy.collider):
                    enemy.take_damage(self.combat.attack_power)
        
        # Detectar si está siendo golpeado
        for enemy in enemies:
            if self.collider.colliderect(enemy.attack_area):
                self.take_damage(enemy.attack_power)
```

---

## 🎯 Siguiente Paso Inmediato

**REVISAR**: ¿Qué causa el cuadrado blanco al moverse diagonal?

→ Ver: `src/entities/player.py:create_player()` línea 67

El problema:
- Player solo tiene 4 sprites (down, right, up, left)
- FSM calcula 8 direcciones (incluyendo diagonales)
- Cuando se intenta acceder a "down_right", no existe el sprite → cuadrado blanco

**Solución**: Actualizar `flip_map` para redondear diagonales a cardinales

Ver sección siguiente en el README para detalles.

---

**Última actualización**: 2026-06-24  
**Estado**: En progreso (MVP completado, expansión futura)  
**Autor**: Dev Team
