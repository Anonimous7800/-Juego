# ☀ | CHRONICLES OF TWO SUNS T2
## Documentación Técnica y Manual Integral del Código y Sistema de Juego

---

### 1. INTRODUCCIÓN Y ORIGEN DE LA OBRA

**Chronicles Of Two Suns T2** (*El Conflicto de los Dos Soles*) es un videojuego de estrategia táctica por turnos desarrollado en **Python** con el motor gráfico y multimedia **Pygame-CE (Community Edition)**. El juego combina la profundidad posicional del ajedrez tradicional con mecánicas modernas de guerra de cartas arcanas, puntos de acción (PA), control de trincheras en una cuadrícula de 16×16, captura de bandera sagrada y habilidades activas de comandantes heroicos.

#### 1.1 Origen en la Comunidad y Saga de Roleplay
El universo de este videojuego nació en **2018** dentro del servidor de roleplay y *Dungeons & Dragons* fundado por **Josue Gomez** bajo el alias de **Sadezu**. El proyecto representa la materialización de su sueño de transformar las leyendas, eras y batallas vividas por los jugadores en un videojuego estratégico.

#### 1.2 Cronología Oficial de la Saga
| Era / Período | Nombre de la Campaña | Descripción Histórica |
| :--- | :--- | :--- |
| **2018 – 2019** | **The Abyss** | El surgimiento de las primeras fuerzas primordiales y la caída de los antiguos reinos. |
| **2020 – 2024** | **The Exodus Chronicles** | La gran migración de los pueblos, la lucha por recursos sagrados y el alzamiento de nuevas naciones. |
| **2024 – 2025** | **Soul Of Velkanor** | La encarnación del alma de Velkanor y las guerras de fuego y éter que fracturaron el continente. |
| **2026 – Presente** | **The Chronicles Of Two Suns** | El amanecer de los Dos Soles celestiales y el choque final entre cuatro grandes imperios. |

#### 1.3 Créditos
- **Idea Original, Concepto e Historia**: Josue Gomez.
- **Desarrollo de Software y Arquitectura**: Josue Gomez y Oliver Camacho.
- **Agradecimientos Especiales**: A cada miembro de la comunidad de ayer y de hoy por construir y preservar esta historia.

---

### 2. LAS CUATRO NACIONES Y SUS COMANDANTES

El conflicto enfrenta a **4 Naciones** organizadas en **2 Equipos Aliados**:

```
      [EQUIPO 1 - ALIANZA DEL SOL Y FUEGO]
        ☀️ Solcardena (Amarillo, 'S')
        🔥 Imperio de Varkhental (Rojo, 'J')
                     VS
     [EQUIPO 2 - COALICIÓN LUNAR Y ESMERALDA]
        🌙 Royaume D'Aurelium (Morado, 'A')
        🗡️ Imperio Sthalgard (Verde, 'K')
```

#### Facciones en Detalle:
1. **Solcardena** (Color Amarillo `#FFD700`, Código `'S'`):
   - *Comandante*: **Helio, el Heraldo Solar**.
   - *Título*: Comandante Supremo de la Luz.
   - *Habilidad Pasiva / Rasgo*: **Firmeza Solar** — Inicia la batalla con +1 Vida de Comandante (4 vidas en lugar de 3) y sus soldados de infantería (peones) disponen de +1 punto de salud (HP) adicional.
   - *Lore*: Custodios de los Salones del Alba cuya fe inquebrantable inspira a sus tropas a resistir las ofensivas más feroces.

2. **Royaume D'Aurelium** (Color Morado `#B19CD9`, Código `'A'`):
   - *Comandante*: **Archicanciller Lunaris**.
   - *Título*: Oráculo de la Corona Lunar.
   - *Habilidad Pasiva / Rasgo*: **Velo de Crepúsculo** — El escudo otorgado por el hechizo Aura Solar perdura turnos adicionales y sus Médicos curan +1 HP extra a las unidades aliadas cercanas cada turno.
   - *Lore*: Sabios alquimistas y devotos del éter cósmico que canalizan el influjo de las lunas gemelas para sostener la vanguardia en batalla.

3. **Imperio de Varkhental** (Color Rojo `#FF5050`, Código `'J'`):
   - *Comandante*: **Ignis, Señor de las Cenizas**.
   - *Título*: Caudillo de las Forjas Volcánicas.
   - *Habilidad Pasiva / Rasgo*: **Furia Ardiente** — Al destruir exitosamente cualquier unidad enemiga en combate, recupera inmediatamente 1 Punto de Acción (PA).
   - *Lore*: Titanes forjados en el fuego de la Caldera Sagrada que avanzan con implacable disciplina militar.

4. **Imperio Sthalgard** (Color Verde `#4ECD91`, Código `'K'`):
   - *Comandante*: **Espectro de la Sombra Jaki**.
   - *Título*: Soberano del Vórtice Oscuro.
   - *Habilidad Pasiva / Rasgo*: **Paso Sombrío** — Inmune por completo al daño y penalizaciones de las trampas mortales (☠) en el tablero, y sus tropas obtienen +1 de alcance de desplazamiento tras atravesar portales.
   - *Lore*: Bastión esmeralda del norte compuesto por maestros de la táctica subterránea y señores de la defensa inexpugnable.

---

### 3. ARQUITECTURA DEL PROYECTO Y ESTRUCTURA DE ARCHIVOS

```
-Juego/
├── main.py                     # Punto de entrada principal y gestor de estados (State Machine)
├── ejecutar_juego.bat          # Lanzador por lotes optimizado para Windows
├── index.html                  # Versión web clásica para navegador
├── missions.json               # Almacenamiento persistente del progreso de misiones y hazañas
├── settings.json               # Almacenamiento persistente de opciones de audio y dificultad
├── generate_assets.py          # Generador procedural de texturas y fondos estelares
├── generate_button_icons.py    # Generador procedural de iconos vectoriales para botones
├── generate_card_images.py     # Generador procedural del arte de las 12 cartas mágicas
├── .gitignore                  # Filtro de archivos innecesarios para despliegue en GitHub
├── README.md                   # Resumen del proyecto y guía rápida de instalación
├── DOCUMENTACION_COMPLETA.md   # Este manual técnico exhaustivo
├── assets/                     # Recursos visuales y sonoros
│   ├── images/
│   │   ├── backgrounds/        # Fondos de pantalla y arte cósmico
│   │   ├── cards/              # Ilustraciones de las 12 cartas tácticas
│   │   ├── icons/              # Iconos de los botones de la interfaz
│   │   ├── pieces/             # Sprites heráldicos de las 24 variantes de fichas
│   │   └── specials/           # Sprites de objetos de tablero (Vida, Rayo, Trampa, Portal)
└── src/                        # Módulos del código fuente en Python
    ├── __init__.py             # Inicializador de paquete Python
    ├── constants.py            # Constantes globales, colores, stats, reglas y mazo
    ├── board.py                # Núcleo de la simulación del tablero, reglas de juego y combate
    ├── ui.py                   # Renderizado gráfico de tablero, piezas, HUD y partículas
    ├── menu.py                 # Pantallas de menú principal, selección, ajustes, créditos y modales
    ├── piece_graphics.py       # Renderizado vectorial de piezas, sombras y barras de HP
    ├── ai.py                   # Inteligencia artificial heurística para comandar las facciones CPU
    ├── tutorial.py             # Controlador del modo de instrucción militar interactiva
    ├── oracle.py               # Asesor militar asíncrono y sistema de crónica táctica
    ├── audio.py                # Gestor de audio y sintetizador de efectos y música
    ├── characters.py           # Datos, estadísticas, bonificaciones y lore de comandantes
    ├── missions.py             # Gestor y comprobador de misiones y logros militares
    ├── settings.py             # Gestor de lectura/escritura de preferencias de usuario
    └── asset_manager.py        # Cargador con caché inteligente de texturas e imágenes
```

---

### 4. DESCRIPCIÓN DETALLADA DE LOS MÓDULOS DEL CÓDIGO

#### 4.1 `main.py` — Ciclo de Vida y Máquina de Estados
El archivo `main.py` implementa la clase central `ConflictoDosSoles`.
- **Estados del Juego (`STATE_*`)**:
  - `STATE_MENU`: Menú principal con acceso a todos los modos.
  - `STATE_CHARACTERS`: Pantalla de selección de facción y comandante humano.
  - `STATE_MISSIONS`: Registro interactivo de misiones con scroll dinámico.
  - `STATE_SETTINGS`: Ajustes de volumen (Música / SFX) y dificultad de la IA.
  - `STATE_RULES`: Enciclopedia completa de reglas y atributos de tropas.
  - `STATE_CREDITS`: Pantalla oficial de créditos, saga histórica y agradecimientos.
  - `STATE_PLAYING`: Estado activo de combate bélico en el tablero de 16×16.
  - `STATE_PAUSED`: Ventana modal de pausa sobre el campo de batalla.
  - `STATE_TUTORIAL`: Sesión de entrenamiento militar interactivo paso a paso.
- **Métodos Principales**:
  - `run()`: Bucle principal a 60 FPS fijos que gestiona el `delta_time` (`dt`), sondea eventos de Pygame, actualiza partículas y estados, procesa el turno de la IA y dibuja la interfaz.
  - `start_game(faction_code)`: Instancia `BoardGame`, configura la IA y solicita consejo inicial al Oráculo táctico.
  - `start_tutorial()`: Inicia el controlador de instrucción militar `TutorialController`.
  - `handle_click(mouse_pos)`: Despacha las interacciones de ratón según el estado activo.
  - `handle_escape()`: Proporciona navegación universal de retroceso y menú de pausa.

#### 4.2 `src/constants.py` — Diccionario del Sistema y Constantes
- **Configuración de Pantalla**: Resolución nativa de `1280×720` a `60 FPS`.
- **Dimensiones del Tablero**: Tablero cuadrado de `N = 16` casillas (256 casillas en total). Zonas de trinchera y centro comprendidas entre `LO = 5` y `HI = 10`.
- **Paleta de Colores**: Definición de paletas cromáticas armónicas (RGB) para fondos oscuros de obsidiana, marcos dorados y auras de cada nación.
- **Estadísticas de Tropas (`UNIT_NAMES`, `UNIT_STATS`)**:
  - Peón / Soldado (`'P'`): Vida: 2 HP | Ataque: 1 | Rango de movimiento: 2 casillas al frente o 1 en cualquier dirección.
  - Torre / Tanque (`'R'`): Vida: 4 HP | Ataque: 3 | Rango: Hasta 6 casillas ortogonales en línea recta.
  - Caballo / Caballería (`'N'`): Vida: 3 HP | Ataque: 2 | Rango: Saltos en "L" ampliada (hasta 2×3 casillas).
  - Alfil / Médico (`'B'`): Vida: 2 HP | Ataque: 1 | Rango: 5 casillas en diagonal. Habilidad: Cura automáticamente +1 HP a aliados en sus 8 casillas vecinas al iniciar el turno.
  - Dama / Oficial (`'Q'`): Vida: 4 HP | Ataque: 3 | Rango: 6 casillas en cualquier dirección ortogonal o diagonal.
  - Rey / General (`'K'`): Vida: 5 HP | Ataque: 2 | Rango: 2 casillas en cualquier dirección. Unidad monarca crucial: perder a ambos generales de un equipo causa derrota militar inmediata.
- **Cartas Tácticas (`CARDS`)**: Catálogo de 12 cartas mágicas con costo de 1 PA y 1 uso por partida (Marcha Forzada, Aura Divina, Impacto de Meteorito, Transmutación, Reclutamiento, Ascenso Lunar, Ceniza Ardiente, Grillete, Viento de Batalla, Emboscada, Hurto de Sombras y Portal Umbrío).

#### 4.3 `src/board.py` — Motor del Tablero y Mecánicas Bélicas
La clase `BoardGame` es el corazón mecánico del juego:
- **Representación de la Cuadrícula**: Matriz bidimensional `16×16`. Cada celda contiene una cadena que codifica la facción y la tropa (ej. `'SP'` = Soldado de Solcardena, `'AK'` = General de Aurelium), `'BLOCKED'` para muros y obstáculos, o `None` si la casilla está vacía.
- **Control de Turnos y Puntos de Acción (PA)**: Cada facción cuenta con 2 PA al iniciar su turno. Mover una tropa, atacar, lanzar una carta táctica o desplegar una unidad de reserva consume PA.
- **Cálculo de Movimiento y Ataque (`calc_moves`)**: Evalúa el alcance geométrico de cada pieza, colisiones contra obstáculos y detección de unidades enemigas para ataques cuerpo a cuerpo o a distancia.
- **Sistema de Combate (`attack`)**:
  - Aplica el daño de la unidad atacante contra el HP del defensor.
  - Si el defensor sobrevive y está en rango de alcance adyacente, ejecuta un contraataque táctico.
  - Al reducir el HP de una unidad a 0, la elimina del tablero, genera efectos de partículas y actualiza el contador de bajas de la facción.
- **Vidas del Comandante (1 a 5 ❤️)**:
  - Cada nación inicia con 3 vidas de comandante (Solcardena con 4 por su rasgo).
  - Se pierde 1 vida si:
    1. Una unidad mayor (Tanque, Caballería, Médico, Oficial o General) es destruida.
    2. Dos soldados de infantería (peones) son abatidos.
    3. Una unidad pisa una trampa mortal (☠).
  - Llegar a 0 vidas elimina a dicha facción de la partida.
- **Objetos Especiales del Terreno**:
  - ❤️ **Vida Regenerativa**: Otorga +1 Vida al Comandante y cura +2 HP a la unidad que la recoge.
  - ⚡ **Rayo Táctico**: Concede +1 de alcance de desplazamiento inmediato.
  - ☠ **Trampa Oculta**: Inmoviliza a la víctima durante 1 turno y resta 1 vida de comandante.
  - 🌀 **Portal Dimensional**: Teletransporta instantáneamente a la tropa a las márgenes opuestas del mapa.
- **Condiciones de Victoria**:
  - **Victoria por Bandera Sagrada**: Recoger la bandera ⚑ situada en el centro del mapa y trasladarla hasta el bastión sagrado de la base aliada (`[15,0]` para el Equipo 1 o `[0,15]` para el Equipo 2).
  - **Victoria por Regicidio**: Destruir a los dos Generales (`'K'`) del equipo rival.

#### 4.4 `src/ui.py` — Renderizado Gráfico, HUD y Efectos Visuales
La clase `UIRenderer` transforma el estado de juego en una interfaz visual atractiva:
- **Perspectiva y Mapeo**: Convierte coordenadas de cuadrícula `(fila, columna)` a coordenadas de pantalla `(x, y)` centradas en el tablero.
- **Resaltado Táctico**: Dibuja halos dorados sobre casillas válidas de movimiento, auras carmesí sobre casillas de ataque enemigo y marcos brillantes sobre la unidad seleccionada.
- **HUD Lateral Informativo**:
  - Insignia de la facción en turno con su estandarte y nombre completo.
  - Corazones de vida del comandante (`❤️❤️❤️🖤🖤`).
  - Contador animado de Puntos de Acción disponibles (`PA`).
  - Estante de Cartas Tácticas con sus ilustraciones en alta definición y marcos reactivos al ratón.
  - Bandeja de tropas en reserva disponibles para despliegue.
  - Panel del Oráculo Ancestral Táctico con su estado de sincronización y botón de consulta.
- **Motor de Partículas**: Simula polvo luminoso, chispas doradas y auras mágicas flotantes alrededor de la bandera y las casillas sagradas.
- **Textos Flotantes (Floating Text Popups)**: Muestra cifras de daño (`-2 HP`), curación (`+1 HP`) y advertencias (`¡Ya actuó este turno!`, `¡Inmovilizado!`) con animación ascendente y desvanecimiento alfa.

#### 4.5 `src/piece_graphics.py` — Gráficos Vectoriales de Piezas
La clase `PieceGraphics` dibuja piezas militares con estética heráldica:
- Sombras elípticas proyectadas bajo la base de cada ficha.
- Auras de color representativas de la facción correspondiente.
- Ilustración vectorial estilizada para cada rango militar (casco de soldado, torre blindada, corcel de caballería, cruz médica, corona de oficial y corona real del general).
- Barra de vida (HP) sobre la cabeza de cada unidad para control táctico inmediato.

#### 4.6 `src/menu.py` — Gestión de Menús e Interfaces
La clase `MenuManager` orquesta todas las pantallas previas y posteriores al combate:
- **Menú Principal (`draw_main_menu`)**: Fondo dinámico con partículas, títulos con resplandor dorado, botones de navegación con iconos y barra inferior con los sellos de las 4 naciones.
- **Selector de Comandantes (`draw_character_select`)**: Muestra tarjetas informativas detalladas con retrato, estadísticas, descripción de habilidades pasivas y lore de cada líder.
- **Misiones y Hazañas (`draw_missions`)**: Panel deslizable con rueda de ratón o botones directos que exhibe el progreso en tiempo real de los logros militares.
- **Ajustes de Audio (`draw_settings`)**: Controles deslizantes (sliders) interactivos para regular de 0% a 100% la música y los efectos de sonido, selector de dificultad de la IA y botón de prueba.
- **Enciclopedia y Reglas (`draw_rules`)**: Guía detallada con la tabla de rangos, atributos, costos de despliegue y mecánicas de victoria.
- **Pantalla de Créditos (`draw_credits`)**: Presentación formal a dos columnas con el origen de la saga comunitaria, creadores, desarrollo y agradecimientos.
- **Modales de Fin de Partida**:
  - `draw_victory_modal`: Fanfarria dorada de victoria gloriosa con opción de revancha o salida al menú.
  - `draw_game_over_modal`: Modal dramático en tonos carmesí que anuncia el bando enemigo vencedor y la causa de la derrota.

#### 4.7 `src/ai.py` — Inteligencia Artificial Estratégica
La clase `AIEngine` proporciona rivalidad militar a las tres facciones controladas por el ordenador:
- Evalúa el tablero mediante una función heurística que pondera:
  1. Seguridad y captura de la bandera sagrada.
  2. Acercamiento al bastión enemigo si se porta la bandera.
  3. Eliminación prioritaria de unidades clave del adversario (Generales y Médicos).
  4. Recogida de orbes de Vida ❤️ y Rayos ⚡ en el campo de batalla.
  5. Despliegue de tropas de reserva cuando la vanguardia sufre bajas.
  6. Uso de cartas tácticas en momentos críticos (como curación mediante *Aura Divina* o daño a distancia con *Impacto de Meteorito*).
- Temporizador de pensamiento natural para evitar acciones instantáneas antinaturales.

#### 4.8 `src/tutorial.py` — Instrucción Militar Interactiva
La clase `TutorialController` guía al comandante novato a través de 5 lecciones prácticas:
1. **Paso 1: Movimiento y Puntos de Acción** — Selección y avance de tropas.
2. **Paso 2: Combate y Contraataque** — Enfrentamiento directo y cálculo de daño.
3. **Paso 3: Elixires de Vida y Trampas** — Recuperación de corazones y evasión de peligros.
4. **Paso 4: Hechizos de Guerra y Cartas** — Invocación de magia táctica.
5. **Paso 5: La Bandera Sagrada y Victoria** — Conquista del estandarte y llegada al bastión.

#### 4.9 `src/audio.py` — Gestor de Audio y Síntesis Polifónica
La clase `AudioManager` se encarga de la ambientación acústica:
- Dos temas musicales polifónicos continuos generados para Menú y Batalla.
- 12 efectos de sonido dedicados (clic, selección, movimiento, combate, impacto, bandera, carta mágica, curación de vida, trampa, portal, victoria y derrota).
- Control de volumen maestro y persistencia de configuración.

#### 4.10 `src/missions.py` y `src/settings.py` — Persistencia de Datos
- `MissionManager`: Monitorea el cumplimiento de objetivos bélicos y guarda el estado en `missions.json`.
- `SettingsManager`: Lee y escribe preferencias de volumen, pantalla completa y dificultad en `settings.json`.

---

### 5. GUÍA RÁPIDA DE CONTROLES

| Control / Tecla | Acción en el Juego |
| :--- | :--- |
| **Clic Izquierdo del Ratón** | Seleccionar tropa, casilla de destino, carta táctica, tropa en reserva o botón de interfaz. |
| **Rueda del Ratón / Drag** | Desplazar la lista de misiones o ajustar los sliders de volumen en Ajustes. |
| **Barra Espaciadora (`SPACE`)** | Finalizar el turno actual voluntariamente. |
| **Teclas `1`, `2`, `3`** | Seleccionar o deseleccionar rápidamente las cartas tácticas de la mano activa. |
| **Tecla `ESCAPE` (`ESC`)** | Pausar la batalla en curso o regresar al menú anterior en cualquier pantalla. |

---

### 6. REQUISITOS Y EJECUCIÓN

1. **Requisitos de Software**:
   - Python 3.10 o superior (completamente probado en Python 3.13).
   - Biblioteca `pygame-ce` (recomendada) o `pygame` estándar:
     ```bash
     pip install pygame-ce
     ```
2. **Ejecución Directa**:
   - En Windows, haz doble clic sobre el archivo:
     ```bash
     ejecutar_juego.bat
     ```
   - O ejecuta desde cualquier terminal:
     ```bash
     python main.py
     ```
