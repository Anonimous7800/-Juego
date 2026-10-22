
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

N = 16
LO = 5
HI = 10

COLOR_BG_DARK = (13, 11, 8)
COLOR_PANEL_BG = (22, 20, 16)
COLOR_PANEL_BORDER = (61, 52, 34)
COLOR_TEXT_LIGHT = (230, 226, 218)
COLOR_TEXT_GOLD = (255, 215, 0)
COLOR_TEXT_MUTED = (160, 148, 130)

COLOR_SOLCARDENA = (255, 215, 0)
COLOR_SOLCARDENA_BG = (43, 33, 19)
COLOR_AURELION = (177, 156, 217)
COLOR_AURELION_BG = (26, 26, 36)
COLOR_JOKI = (255, 80, 80)
COLOR_JOKI_BG = (45, 18, 18)
COLOR_JAKI = (78, 205, 145)
COLOR_JAKI_BG = (15, 43, 32)

FACTIONS = {
    'SOLCARDENA': {
        'name': 'Solcardena',
        'code': 'S',
        'color': COLOR_SOLCARDENA,
        'bg': COLOR_SOLCARDENA_BG,
        'team': 1,
        'lore': 'Imperio Solar. Maestros del honor y la estrategia expansiva.'
    },
    'AURELION': {
        'name': "Royaume D'Aurelium",
        'code': 'A',
        'color': COLOR_AURELION,
        'bg': COLOR_AURELION_BG,
        'team': 2,
        'lore': 'Reino Místico de la Luna. Sabios alquimistas y devotos del éter cósmico.'
    },
    'JOKI': {
        'name': 'Imperio de Varkhental',
        'code': 'J',
        'color': COLOR_JOKI,
        'bg': COLOR_JOKI_BG,
        'team': 1,
        'lore': 'Fuerza volcánica de acero y fuego. Guerreros temibles de implacable disciplina.'
    },
    'JAKI': {
        'name': 'Imperio Sthalgard',
        'code': 'K',
        'color': COLOR_JAKI,
        'bg': COLOR_JAKI_BG,
        'team': 2,
        'lore': 'Bastión esmeralda del norte. Titanes tácticos y señores de la defensa inexpugnable.'
    }
}

ORDER = ['SOLCARDENA', 'AURELION', 'JOKI', 'JAKI']

TEAM = {
    'S': 1,
    'J': 1,
    'A': 2,
    'K': 2
}

TEAM_NAMES = {
    1: 'Alianza de Solcardena y Varkhental',
    2: 'Coalición de Aurelium y Sthalgard'
}

UNIT_NAMES = {
    'P': 'Soldado',
    'R': 'Tanque',
    'N': 'Caballería',
    'B': 'Médico',
    'Q': 'Oficial',
    'K': 'General'
}

UNIT_ICONS = {
    'P': '⚔️',
    'R': '🛡️',
    'N': '🐎',
    'B': '⚕️',
    'Q': '👑',
    'K': '🤴'
}

ATK = {'P': 2, 'R': 4, 'N': 3, 'B': 1, 'Q': 3, 'K': 2}
MAX_HP = {'P': 3, 'R': 6, 'N': 4, 'B': 3, 'Q': 5, 'K': 8}
UNIT_COST = {'P': 1, 'B': 1, 'N': 1, 'R': 2, 'Q': 2, 'K': 2}

FWD = {
    'S': (-1, 0),
    'A': (1, 0),
    'J': (0, 1),
    'K': (0, -1)
}

ALL_DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

KNIGHT_JUMPS = []
for x, y in [(1, 2), (1, 3), (2, 3)]:
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            KNIGHT_JUMPS.append((x * sx, y * sy))
            KNIGHT_JUMPS.append((y * sx, x * sy))

CARDS = {
    'MARCHA': {
        'name': 'Marcha Forzada',
        'desc': 'Un peón avanza hasta 6 casillas en línea recta.',
        'hint': 'Elige un peón y luego su casilla destino (hasta 6 casillas).',
        'icon': '👢⚡',
        'type': 'AVANCE',
        'cost': 1
    },
    'AURA': {
        'name': 'Aura Solar',
        'desc': 'Una pieza tuya obtiene un escudo divino hasta tu próximo turno.',
        'hint': 'Elige una pieza aliada para otorgarle inmunidad.',
        'icon': '🛡️☀️',
        'type': 'ESCUDO',
        'cost': 1
    },
    'IMPACTO': {
        'name': 'Impacto Solar',
        'desc': 'Bloquea para siempre una casilla vacía con un meteorito.',
        'hint': 'Elige una casilla vacía (excepto bandera o bastiones meta 🏳️).',
        'icon': '☄️💥',
        'type': 'BLOQUEO',
        'cost': 1
    },
    'TRANSMUTA': {
        'name': 'Transmutación',
        'desc': 'Intercambia la posición de un peón con otra pieza aliada.',
        'hint': 'Elige un peón tuyo y luego la pieza aliada con la que permutar.',
        'icon': '🔄✨',
        'type': 'PERMUTA',
        'cost': 1
    },
    'RECLUTA': {
        'name': 'Reclutamiento',
        'desc': 'Invoca un nuevo peón en una casilla vacía de tu zona inicial.',
        'hint': 'Elige una casilla vacía de tus filas de despliegue.',
        'icon': '📯👥',
        'type': 'REFUERZO',
        'cost': 1
    },
    'ASCENSO': {
        'name': 'Ascenso Lunar',
        'desc': 'Promueve un peón aliado a Médico de campo (curación pasiva).',
        'hint': 'Elige un peón propio para transformarlo en Médico.',
        'icon': '🌙⚕️',
        'type': 'PROMOCIÓN',
        'cost': 1
    },
    'CENIZA': {
        'name': 'Ceniza Ardiente',
        'desc': 'Destruye instantáneamente a un peón enemigo sin escudo.',
        'hint': 'Elige un peón enemigo para calcinarlo.',
        'icon': '🔥💀',
        'type': 'DESTRUCCIÓN',
        'cost': 1
    },
    'GRILLETE': {
        'name': 'Grillete de Ceniza',
        'desc': 'Inmoviliza a una pieza enemiga (no General) durante 1 turno.',
        'hint': 'Elige una pieza enemiga a paralizar.',
        'icon': '⛓️🔥',
        'type': 'INMOVILIZAR',
        'cost': 1
    },
    'VIENTO': {
        'name': 'Viento Ardiente',
        'desc': 'Mueve la bandera sagrada suelta hasta 3 casillas.',
        'hint': 'Elige una casilla vacía a distancia ≤ 3 de la bandera.',
        'icon': '🌪️🔥',
        'type': 'TÁCTICA',
        'cost': 1
    },
    'EMBOSCADA': {
        'name': 'Emboscada',
        'desc': 'Coloca una trampa mortal ☠ en cualquier casilla vacía.',
        'hint': 'Elige una casilla vacía para tender la trampa.',
        'icon': '🗡️🕸️',
        'type': 'TRAMPA',
        'cost': 1
    },
    'HURTO': {
        'name': 'Hurto de Sombras',
        'desc': 'Roba la bandera al portador enemigo con tu pieza adyacente.',
        'hint': 'Elige tu pieza adyacente al portador enemigo.',
        'icon': '👤🗝️',
        'type': 'SIGILO',
        'cost': 1
    },
    'PORTAL': {
        'name': 'Portal Umbrío',
        'desc': 'Teletransporta una pieza aliada al cuadrante central.',
        'hint': 'Elige tu pieza (no Rey) y luego una casilla central vacía.',
        'icon': '🌀🌌',
        'type': 'TRASLADO',
        'cost': 1
    }
}

FACTION_HANDS = {
    'S': ['MARCHA', 'AURA', 'IMPACTO'],
    'A': ['TRANSMUTA', 'RECLUTA', 'ASCENSO'],
    'J': ['CENIZA', 'GRILLETE', 'VIENTO'],
    'K': ['EMBOSCADA', 'HURTO', 'PORTAL']
}

MAX_LIVES = 5
INIT_LIVES = 3
