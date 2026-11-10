# ☀️ El Conflicto de los Dos Soles - Edición Pygame 🌙

Adaptación profesional completa en Python con **Pygame** de *El Conflicto de los Dos Soles*, con música ambiental, efectos de sonido de alta fidelidad, menú interactivo con partículas, selector de personajes y comandantes, sistema de misiones y hazañas, pantalla de ajustes con control de volumen, tutorial de reglas y pantallas dramáticas de Victoria y Game Over.

---
## Project University 

## 🎮 Características Principales

1. **Menú de Inicio Profesional**:
   - Diseño oscuro y celestial con auras solares y partículas flotantes.
   - Navegación interactiva por teclado y ratón con feedback sonoro y animaciones al pasar el cursor.
   - Acceso directo a Jugar, Personajes, Misiones, Ajustes, Reglas y Salir.

2. **Música y Efectos de Sonido Integrados**:
   - **Banda Sonora de Menú**: Melodía ambiental mística y celestial en arpegios polifónicos.
   - **Banda Sonora de Batalla**: Ritmo táctico propulsivo con bajo sintetizado y arreglos de tensión militar.
   - **12 Efectos de Sonido Especiales**: Movimiento de piezas, espadas e impactos, explosiones de destrucción, fanfarria de captura de bandera, magia de cartas arcanas, regeneración de vida ❤️, activación de trampas ☠, vórtices de portales 🌀, victoria épica y derrota fúnebre.

3. **Arte y Fondos Visuales Organizados (`assets/images/`)**:
   - **Fondo de Arte Celestial**: Integración del fondo épico `Proyecto_nuevo_1.jpg` en los menús y detrás del tablero táctico.
   - **Mazo de Cartas Ilustradas (`assets/images/cards/`)**: Las 12 cartas tácticas poseen sus ilustraciones dedicadas de alta definición (Marcha, Aura, Impacto, Transmuta, Recluta, Ascenso, Ceniza, Grillete, Viento, Emboscada, Hurto, Portal).
   - **Fichas y Siluetas Heráldicas (`assets/images/pieces/`)**: Las 24 combinaciones de fichas con siluetas vectoriales de ajedrez táctico.
   - **Insignias de Objetos Especiales (`assets/images/specials/`)**: Badges de Vida ❤️, Rayo ⚡, Trampa ☠ y Portal 🌀.

4. **Selector de Comandantes y Personajes**:
   - **Helio, el Heraldo Solar (Solcardena)**: Inicia con +1 Vida de Comandante (4 vidas) y sus peones poseen más resistencia.
   - **Archicanciller Lunaris (Royaume D'Aurelium)**: Escudos más duraderos y sus Médicos curan +1 HP adicional cada turno.
   - **Ignis, Señor de las Cenizas (Imperio de Varkhental)**: Recupera 1 Punto de Acción (PA) de inmediato al destruir una unidad enemiga.
   - **Espectro de la Sombra Jaki (Imperio Sthalgard)**: Inmune a las trampas mortales ☠ del mapa.

5. **Sistema de Misiones y Hazañas**:
   - Seguimiento en tiempo real y guardado persistente en `missions.json`:
     - *Primer Golpe*: Elimina 3 unidades enemigas en combate.
     - *Portador de Gloria*: Captura la bandera sagrada en el centro.
     - *Corazón Inmortal*: Recoge 3 Esencias de Vida ❤️ en el campo.
     - *Maestro Arcano*: Utiliza 4 cartas tácticas en batalla.
     - *Regicida*: Derrota a un General (Rey 🤴) enemigo.
     - *Victoria Impecable*: Gana una partida manteniendo 4 o más Vidas de Comandante.

6. **Menú de Ajustes Completo**:
   - Sliders interactivos de volumen de música (0% - 100%) y efectos de sonido FX (0% - 100%).
   - Botón de prueba de sonido instantáneo.
   - Selector de dificultad de la Inteligencia Artificial (Normal vs. Maestro).
   - Guardado automático en `settings.json`.

7. **Mecánicas Tácticas y Tablero 16x16**:
   - 4 Facciones en 2 Equipos:
     - **Equipo 1 (Alianza de Solcardena y Varkhental)**: Solcardena y Varkhental. Meta en [15,0].
     - **Equipo 2 (Coalición de Aurelium y Sthalgard)**: Aurelium y Sthalgard. Meta en [0,15].
   - **Objetos Especiales en el Campo**:
     - ❤️ **Vida**: Otorga +1 Vida al Comandante y cura +2 HP a la unidad.
     - ⚡ **Rayo Táctico**: +1 de alcance de desplazamiento.
     - ☠ **Trampa**: Inmoviliza 1 turno y resta 1 Vida de Comandante.
     - 🌀 **Portal**: Teletransporte inmediato a las márgenes del tablero.
   - **Cartas Tácticas**: Marcha Forzada, Aura Divina, Impacto de Meteorito, Transmutación, Reclutamiento, Ascenso Lunar, Ceniza Ardiente, Grillete, Viento de Batalla, Emboscada, Hurto de Sombras y Portal Umbrío.
   - **Sistema de Puntos de Acción (2 PA por turno)** con despliegue de reservas.
   - Registro de batalla en tiempo real en el HUD.

---

## 🚀 Cómo Ejecutar el Juego

### Requisitos:
- Python 3.10 o superior (compatible con Python 3.13).
- Paquete `pygame-ce` instalado:
  ```bash
  pip install pygame-ce
  ```

### Inicio Rápido:
Haz doble clic en:
```
ejecutar_juego.bat
```
O ejecuta en tu terminal:
```bash
python main.py
```

---

## ⌨️ Controles

- **Clic Izquierdo**: Seleccionar tropa, casilla de destino, carta táctica o botón.
- **Barra Espaciadora**: Pasar / Terminar turno anticipadamente.
- **Teclas 1, 2, 3**: Seleccionar y activar las Cartas Tácticas de tu mano.
- **ESC**: Pausar la partida o volver atrás en los menús.