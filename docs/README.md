# 📚 Documentación — El Pollo Roberto

Este directorio contiene la documentación específica del proyecto.

---

## 📖 Guías Disponibles

### 1. [`animation_system.md`](animation_system.md)
**Sistema de Animación: Máquina de Estados (FSM) Reutilizable**

Documentación completa sobre cómo usar el nuevo sistema de animación:
- `AnimationComponent` — manejo de frames y renderizado
- `AnimationStateMachineComponent` — FSM genérico para transiciones
- Ejemplos de player, enemigos, bosses, efectos
- API completa y casos de uso comunes
- Migración desde sistema antiguo

**Leer si**: Necesitas agregar/entender animaciones en el juego.

---

### 2. [`roadmap.md`](roadmap.md)
**Roadmap de Expansión Futura**

Plan de desarrollo para agregar nuevos estados de animación al player:
- Estructura de directorio recomendada (attack, block, dash, hurt, etc.)
- Pasos para agregar nuevas animaciones
- Integración con FSM
- Tests de validación
- Fases de implementación (simple → stretch goals)

**Leer si**: Quieres expandir las animaciones del player con nuevos estados.

---

### 3. [`refactoring_summary.md`](refactoring_summary.md)
**Resumen de Refactorización (qué cambió y por qué)**

Historial detallado de la reestructuración del sistema:
- Cambios antes/después
- Características nuevas
- Casos de uso ahora soportados
- Archivos modificados/nuevos/eliminados
- Beneficios cuantitativos
- Notas de implementación

**Leer si**: Necesitas entender qué cambió en el sistema de animación.

---

## 📂 Estructura Recomendada

```
docs/
├── README.md                   # Este archivo
├── animation_system.md         # Guía del sistema de animación
├── roadmap.md                  # Plan de expansión
└── refactoring_summary.md      # Cambios de refactorización
```

---

## 🎯 Documentación General (en raíz)

Además de `docs/`, hay documentación importante en la raíz del proyecto:

- **`ARCHITECTURE.md`** — Arquitectura general del proyecto, stack tecnológico, patrones ECS
- **`MEMORY.md`** — Sistema de memoria para conversaciones
- **`README.md`** — Instalación y ejecución rápida

---

## 🔍 Búsqueda Rápida

### "¿Cómo agrego una animación de ataque?"
→ Ver [`roadmap.md`](roadmap.md) — Sección "Cómo Agregar Nuevas Animaciones"

### "¿Cuál es la API del AnimationComponent?"
→ Ver [`animation_system.md`](animation_system.md) — Sección "AnimationComponent"

### "¿Cómo creo una FSM para un enemigo?"
→ Ver [`animation_system.md`](animation_system.md) — Sección "Ejemplo: Enemigo con FSM"

### "¿Qué cambió del sistema antiguo?"
→ Ver [`refactoring_summary.md`](refactoring_summary.md) — Sección "Cambios Principales"

### "¿Cómo evito doble actualización de frames?"
→ Ver [`animation_system.md`](animation_system.md) — Sección "Notas Importantes"

---

## 🚀 Próximos Pasos

1. **Leer** [`animation_system.md`](animation_system.md) para entender la arquitectura
2. **Revisar** el código en `src/components/animation.py` y `src/components/animation_state_machine.py`
3. **Ejecutar** `python verify_animation_system.py` para validar el sistema
4. **Expandir** siguiendo [`roadmap.md`](roadmap.md) si deseas agregar nuevas animaciones

---

**Última actualización**: 2026-06-24  
**Estado**: Documentación consolidada y organizada
