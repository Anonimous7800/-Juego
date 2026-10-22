import os
import pygame
from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT

class AssetManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AssetManager, cls).__new__(cls)
            cls._instance.bg_menu = None
            cls._instance.bg_game = None
            cls._instance.card_images = {}
            cls._instance.piece_images = {}
            cls._instance.special_images = {}
            cls._instance.icon_images = {}
            cls._instance.load_all()
        return cls._instance

    def load_all(self):
        self.load_backgrounds()
        self.load_cards()
        self.load_pieces()
        self.load_specials()
        self.load_icons()

    def load_backgrounds(self):
        bg_path = os.path.join("assets", "images", "backgrounds", "main_bg.jpg")
        if not os.path.exists(bg_path):
            bg_path = "Proyecto_nuevo_1.jpg"

        if os.path.exists(bg_path):
            try:
                raw_bg = pygame.image.load(bg_path).convert()
                scaled_menu = pygame.transform.smoothscale(raw_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
                vignette_menu = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                vignette_menu.fill((10, 8, 6, 75))
                scaled_menu.blit(vignette_menu, (0, 0))
                self.bg_menu = scaled_menu

                scaled_game = pygame.transform.smoothscale(raw_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
                vignette_game = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                vignette_game.fill((10, 8, 6, 140))
                scaled_game.blit(vignette_game, (0, 0))
                self.bg_game = scaled_game
            except Exception as e:
                print(f"Warning: Could not load background image: {e}")

    def load_cards(self):
        cards_dir = os.path.join("assets", "images", "cards")
        if os.path.exists(cards_dir):
            for fname in os.listdir(cards_dir):
                if fname.lower().endswith(".png"):
                    card_id = os.path.splitext(fname)[0].upper()
                    fpath = os.path.join(cards_dir, fname)
                    try:
                        surf = pygame.image.load(fpath).convert_alpha()
                        self.card_images[card_id] = surf
                    except Exception as e:
                        print(f"Error loading card image {fname}: {e}")

    def load_pieces(self):
        pieces_dir = os.path.join("assets", "images", "pieces")
        if os.path.exists(pieces_dir):
            for fname in os.listdir(pieces_dir):
                if fname.lower().endswith(".png"):
                    piece_key = os.path.splitext(fname)[0]
                    fpath = os.path.join(pieces_dir, fname)
                    try:
                        surf = pygame.image.load(fpath).convert_alpha()
                        self.piece_images[piece_key] = surf
                    except Exception as e:
                        print(f"Error loading piece image {fname}: {e}")

    def load_specials(self):
        specials_dir = os.path.join("assets", "images", "specials")
        if os.path.exists(specials_dir):
            for fname in os.listdir(specials_dir):
                if fname.lower().endswith(".png"):
                    sp_key = os.path.splitext(fname)[0]
                    fpath = os.path.join(specials_dir, fname)
                    try:
                        surf = pygame.image.load(fpath).convert_alpha()
                        self.special_images[sp_key] = surf
                    except Exception as e:
                        print(f"Error loading special image {fname}: {e}")

    def load_icons(self):
        icons_dir = os.path.join("assets", "images", "icons")
        if os.path.exists(icons_dir):
            for fname in os.listdir(icons_dir):
                if fname.lower().endswith(".png"):
                    icon_key = os.path.splitext(fname)[0]
                    fpath = os.path.join(icons_dir, fname)
                    try:
                        surf = pygame.image.load(fpath).convert_alpha()
                        self.icon_images[icon_key] = surf
                    except Exception as e:
                        print(f"Error loading icon image {fname}: {e}")

    def get_icon(self, name, size=None):
        surf = self.icon_images.get(name)
        if surf and size:
            return pygame.transform.smoothscale(surf, size)
        return surf

    def get_card_image(self, card_id, size=None):
        surf = self.card_images.get(card_id.upper())
        if surf and size:
            return pygame.transform.smoothscale(surf, size)
        return surf

    def get_piece_image(self, faction_code, piece_type, size=None):
        key = f"{faction_code}_{piece_type}"
        surf = self.piece_images.get(key)
        if surf and size:
            return pygame.transform.smoothscale(surf, size)
        return surf

    def get_special_image(self, sp_type, size=None):
        surf = self.special_images.get(sp_type)
        if surf and size:
            return pygame.transform.smoothscale(surf, size)
        return surf

    def get_menu_background(self):
        return self.bg_menu

    def get_game_background(self):
        return self.bg_game
