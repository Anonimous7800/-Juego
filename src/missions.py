import json
import os

MISSIONS_FILE = "missions.json"

DEFAULT_MISSIONS = [
    {
        "id": "first_blood",
        "title": "Primer Golpe",
        "desc": "Elimina a 3 unidades enemigas en combate.",
        "icon": "btn_play",
        "target": 3,
        "progress": 0,
        "completed": False,
        "reward": "Insignia de Veterano"
    },
    {
        "id": "flag_bearer",
        "title": "Portador de Gloria",
        "desc": "Captura la bandera sagrada con cualquier tropa.",
        "icon": "btn_rules",
        "target": 1,
        "progress": 0,
        "completed": False,
        "reward": "Estandarte Dorado"
    },
    {
        "id": "heart_collector",
        "title": "Corazón Inmortal",
        "desc": "Recoge 3 Esencias de Vida en el campo de batalla.",
        "icon": "btn_characters",
        "target": 3,
        "progress": 0,
        "completed": False,
        "reward": "Elixir Solar"
    },
    {
        "id": "spellmaster",
        "title": "Maestro Arcano",
        "desc": "Utiliza 4 cartas tácticas en batalla.",
        "icon": "btn_rules",
        "target": 4,
        "progress": 0,
        "completed": False,
        "reward": "Tomo de Hechicería"
    },
    {
        "id": "general_slayer",
        "title": "Regicida",
        "desc": "Derrota a un General (Rey) enemigo.",
        "icon": "btn_characters",
        "target": 1,
        "progress": 0,
        "completed": False,
        "reward": "Corona Imperial"
    },
    {
        "id": "flawless_victory",
        "title": "Victoria Impecable",
        "desc": "Gana una partida manteniendo 4 o más Vidas.",
        "icon": "btn_missions",
        "target": 1,
        "progress": 0,
        "completed": False,
        "reward": "Escudo de la Luz Suprema"
    },
    {
        "id": "tutorial_grad",
        "title": "Iniciado de los Soles",
        "desc": "Completa la instrucción militar táctica.",
        "icon": "btn_tutorial",
        "target": 1,
        "progress": 0,
        "completed": False,
        "reward": "Medalla de Instrucción"
    },
    {
        "id": "oracle_seeker",
        "title": "Discípulo del Oráculo",
        "desc": "Consulta las visiones del Oráculo Ancestral 3 veces.",
        "icon": "btn_oracle",
        "target": 3,
        "progress": 0,
        "completed": False,
        "reward": "Prisma de Sabiduría"
    },
    {
        "id": "trench_master",
        "title": "Conquistador de Trincheras",
        "desc": "Mueve tropas hacia las trincheras 6 veces.",
        "icon": "btn_play",
        "target": 6,
        "progress": 0,
        "completed": False,
        "reward": "Pico de Trinchera"
    },
    {
        "id": "veteran_commander",
        "title": "Comandante Supremo",
        "desc": "Sobrevive a 15 rondas de combate bélico.",
        "icon": "btn_missions",
        "target": 15,
        "progress": 0,
        "completed": False,
        "reward": "Capa de Señor de la Guerra"
    }
]

class MissionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MissionManager, cls).__new__(cls)
            cls._instance.missions = [dict(m) for m in DEFAULT_MISSIONS]
            cls._instance.load()
        return cls._instance

    def load(self):
        if os.path.exists(MISSIONS_FILE):
            try:
                with open(MISSIONS_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    saved_map = {m["id"]: m for m in saved}
                    for m in self.missions:
                        if m["id"] in saved_map:
                            m["progress"] = saved_map[m["id"]].get("progress", 0)
                            m["completed"] = saved_map[m["id"]].get("completed", False)
            except Exception:
                pass

    def save(self):
        try:
            with open(MISSIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.missions, f, indent=4)
        except Exception:
            pass

    def add_progress(self, mission_id, amount=1):
        just_completed = []
        for m in self.missions:
            if m["id"] == mission_id and not m["completed"]:
                m["progress"] = min(m["target"], m["progress"] + amount)
                if m["progress"] >= m["target"]:
                    m["completed"] = True
                    just_completed.append(m)
        if just_completed:
            self.save()
        return just_completed

    def get_all(self):
        return self.missions

    def get_completed_count(self):
        return sum(1 for m in self.missions if m["completed"])
