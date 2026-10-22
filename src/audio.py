import os
import pygame
from src.settings import SettingsManager

class AudioManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioManager, cls).__new__(cls)
            cls._instance.initialized = False
            cls._instance.sounds = {}
            cls._instance.current_music = None
            cls._instance.settings = SettingsManager()
            cls._instance.init_mixer()
        return cls._instance

    def init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            self.load_all_sounds()
            self.set_music_volume(self.settings.get("music_volume", 0.7))
            self.set_sfx_volume(self.settings.get("sfx_volume", 0.85))
            self.initialized = True
        except Exception as e:
            print(f"Warning: Audio mixer failed to initialize: {e}")

    def load_all_sounds(self):
        sound_files = {
            'click': 'assets/sounds/sfx_click.wav',
            'select': 'assets/sounds/sfx_select.wav',
            'move': 'assets/sounds/sfx_move.wav',
            'attack': 'assets/sounds/sfx_attack.wav',
            'death': 'assets/sounds/sfx_death.wav',
            'card': 'assets/sounds/sfx_card.wav',
            'flag': 'assets/sounds/sfx_flag.wav',
            'life': 'assets/sounds/sfx_life.wav',
            'trap': 'assets/sounds/sfx_trap.wav',
            'portal': 'assets/sounds/sfx_portal.wav',
            'victory': 'assets/sounds/sfx_victory.wav',
            'gameover': 'assets/sounds/sfx_gameover.wav'
        }
        for name, path in sound_files.items():
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except Exception as e:
                    print(f"Could not load sound {path}: {e}")

    def play_sfx(self, name):
        if name in self.sounds:
            try:
                vol = self.settings.get("sfx_volume", 0.85)
                self.sounds[name].set_volume(vol)
                self.sounds[name].play()
            except Exception as e:
                print(f"Error playing sfx {name}: {e}")

    def play_music(self, track_name, loops=-1):
        path = f"assets/music/{track_name}.wav"
        if not os.path.exists(path):
            return
        if self.current_music == track_name and pygame.mixer.music.get_busy():
            return
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            vol = self.settings.get("music_volume", 0.7)
            pygame.mixer.music.set_volume(vol)
            pygame.mixer.music.play(loops)
            self.current_music = track_name
        except Exception as e:
            print(f"Error playing music {track_name}: {e}")

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
            self.current_music = None
        except Exception:
            pass

    def set_music_volume(self, vol):
        vol = max(0.0, min(1.0, vol))
        self.settings.set("music_volume", vol)
        try:
            pygame.mixer.music.set_volume(vol)
        except Exception:
            pass

    def set_sfx_volume(self, vol):
        vol = max(0.0, min(1.0, vol))
        self.settings.set("sfx_volume", vol)
        for s in self.sounds.values():
            s.set_volume(vol)
