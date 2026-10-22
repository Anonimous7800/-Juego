import json
import os
import threading
import urllib.request
import urllib.error
import time

GEMINI_CONFIG = {
    'apiKey': os.environ.get('GEMINI_API_KEY', 'AQ.Ab8RN6LwvY7YkN_VONJ1wCkRIKyt8epQ2WW-td40W9ftao09TQ'),
    'primaryModel': 'gemini-3.8-flash',
    'fallbackModels': ['gemini-flash-latest', 'gemini-2.5-flash-lite', 'gemini-1.5-flash'],
    'baseUrl': 'https://generativelanguage.googleapis.com/v1beta/models'
}

class GeminiOracle:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GeminiOracle()
        return cls._instance

    def __init__(self):
        self.is_busy = False
        self.status = "Online"
        self.last_advice = "El Oráculo de los Soles aguarda el fragor del combate para predecir tu destino..."
        self.last_query_time = 0
        self.lock = threading.Lock()

    def get_status(self):
        return self.status

    def get_advice(self):
        return self.last_advice

    def solicitar_consejo_async(self, estado, on_complete=None):
        """Dispatches an asynchronous thread to query Gemini without blocking Pygame's loop."""
        with self.lock:
            if self.is_busy:
                return False
            self.is_busy = True
            self.status = "Analizando..."

        thread = threading.Thread(target=self._worker_query, args=(estado, on_complete), daemon=True)
        thread.start()
        return True

    def _worker_query(self, estado, on_complete):
        advice = None
        try:
            advice = self._call_gemini(estado)
        except Exception:
            advice = None

        if not advice:
            advice = self.obtener_consejo_heuristico(estado)
            status_result = "Modo Local"
        else:
            status_result = "Online"

        with self.lock:
            self.last_advice = advice
            self.status = status_result
            self.is_busy = False
            self.last_query_time = time.time()

        if on_complete:
            try:
                on_complete(advice)
            except Exception:
                pass

    def _call_gemini(self, estado):
        es_tutorial = estado.get('es_tutorial', False)
        if es_tutorial:
            system_instruction = (
                "Eres el Oráculo Ancestral Táctico, el instructor militar supremo en el juego 'Chronicles Of Two Suns T2'. "
                "Instruye al comandante en español con sabiduría cósmica y táctica. "
                "Da una indicación clara, inspiradora y concisa (máximo 2 oraciones, menos de 28 palabras)."
            )
            prompt = (
                f"Estás entrenando al comandante en el {estado.get('tutorial_paso_nombre', 'Paso de Entrenamiento')}. "
                f"Contexto táctico: {estado.get('tutorial_desc', '')}. "
                "Instruye al comandante sobre el movimiento o acción que debe ejecutar ahora."
            )
        else:
            system_instruction = (
                "Eres el Oráculo Táctico del juego 'El Conflicto de los Dos Soles'. "
                "Responde en español con una recomendación militar breve (máximo 2 oraciones, menos de 30 palabras), "
                "precisa, inspiradora y estratégica para el comandante."
            )
            prompt = (
                f"Estado de batalla: Turno: {estado.get('turno_nombre', 'Solcardena')}, "
                f"Facción del jugador: {estado.get('humano_nombre', 'Solcardena')}, "
                f"Vidas de comandante: {estado.get('vidas_restantes', 3)}/5, "
                f"PA disponibles: {estado.get('ap', 2)}/2, "
                f"Estado de la Bandera: {estado.get('bandera_info', 'En el centro')}, "
                f"Tropas enemigas cercanas: {estado.get('enemigos_cercanos', 0)}, "
                f"Cartas en mano: {estado.get('cartas_disponibles', 'Escudo Divino')}. "
                "¿Cuál es la mejor jugada militar inmediata?"
            )

        models_to_try = [GEMINI_CONFIG['primaryModel']] + GEMINI_CONFIG['fallbackModels']
        payload_dict = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system_instruction}]
            },
            "generationConfig": {
                "temperature": 0.6,
                "maxOutputTokens": 60
            }
        }
        body_bytes = json.dumps(payload_dict).encode('utf-8')

        for model in models_to_try:
            url = f"{GEMINI_CONFIG['baseUrl']}/{model}:generateContent?key={GEMINI_CONFIG['apiKey']}"
            req = urllib.request.Request(
                url,
                data=body_bytes,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            try:
                with urllib.request.urlopen(req, timeout=5.5) as resp:
                    if resp.status == 200:
                        raw = resp.read().decode('utf-8')
                        data = json.loads(raw)
                        candidates = data.get('candidates', [])
                        if candidates:
                            parts = candidates[0].get('content', {}).get('parts', [])
                            if parts:
                                text = parts[0].get('text', '').strip()
                                if text:
                                    text = text.replace('\n', ' ').strip('"\'')
                                    return text
            except Exception:
                continue

        return None

    def obtener_consejo_heuristico(self, estado):
        """Tactical heuristic advice when offline or as immediate fallback."""
        carried = estado.get('bandera_llevada', False)
        carrier_is_me = estado.get('portador_es_aliado', False)
        lives = estado.get('vidas_restantes', 3)
        ap = estado.get('ap', 2)
        active_card = estado.get('cartas_activas', None)

        if carried:
            if carrier_is_me:
                return "¡Tu bando tiene la Bandera Sagrada! Escolta con urgencia a tu portador hacia el bastión para asegurar la victoria total."
            else:
                return "¡Alerta máxima! El enemigo porta la Bandera Sagrada. Concentra todos tus ataques para interceptarlo antes del bastión."

        if lives <= 2:
            return "¡Tus Vidas de Comandante están en estado crítico! Prioriza recoger corazones de Vida ❤️ en el tablero para reabastecerte."

        if ap == 2:
            return "Tienes 2 PA completos. Despliega tropas de reserva o avanza hacia el centro del tablero para asegurar posiciones clave."

        return "Controla las trincheras y aprovecha los rayos ⚡ para extender el rango táctico de tus torres y generales."

    def cronica_evento_async(self, evento, faccion, on_complete=None):
        def _task():
            system = "Eres el gran cronista celestial del Conflicto de los Dos Soles."
            prompt = f"En máximo 10 palabras y tono de épica medieval: la facción {faccion} ha {evento}."
            fallback = f"Los anales registrarán que {faccion} ha {evento} con determinación."

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 30}
            }
            body = json.dumps(payload).encode('utf-8')
            for model in [GEMINI_CONFIG['primaryModel'], 'gemini-flash-latest']:
                try:
                    url = f"{GEMINI_CONFIG['baseUrl']}/{model}:generateContent?key={GEMINI_CONFIG['apiKey']}"
                    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'}, method='POST')
                    with urllib.request.urlopen(req, timeout=4.0) as resp:
                        if resp.status == 200:
                            data = json.loads(resp.read().decode('utf-8'))
                            text = data['candidates'][0]['content']['parts'][0]['text'].strip()
                            if text and on_complete:
                                on_complete(text.replace('\n', ' '))
                                return
                except Exception:
                    continue
            if on_complete:
                on_complete(fallback)

        threading.Thread(target=_task, daemon=True).start()
