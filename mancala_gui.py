import pygame
import sys
import math
import os
import random
import copy
from mancala import Play, PlayAlt, MAX, MIN

# Initialisation de pygame
pygame.init()

# Constantes de l'interface
WIDTH, HEIGHT = 1200, 750
FPS = 60

# Couleurs vintage bois antique
BG_COLOR = (40, 30, 20)
BOARD_COLOR = (101, 67, 33)
PIT_COLOR = (139, 90, 43)
PIT_HOVER_COLOR = (160, 110, 60)
PIT_PLAYER_COLOR = (156, 102, 52)
PIT_COMPUTER_COLOR = (122, 79, 39)
STORE_COLOR = (80, 52, 28)
SEED_COLOR = (210, 180, 140)
SEED_DARK = (160, 130, 90)
TEXT_COLOR = (245, 222, 179)
ACCENT_COLOR = (218, 165, 32)
WINNER_COLOR = (50, 205, 50)  # Green for winner
LOSER_COLOR = (220, 20, 60)   # Red for loser
SHADOW_COLOR = (20, 15, 10, 120)
WOOD_GRAIN = (92, 64, 51)

# Chemins des assets
LOGO_PATH = os.path.join("assets", "logo.png")
FONT_PATH = os.path.join("font", "Wood 2.ttf")

# Police
pygame.font.init()


class MancalaGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Mancala - Antique Wood Edition")
        self.clock = pygame.time.Clock()
        self.play = Play()
        
        # Charger le logo
        self.logo = None
        try:
            logo_img = pygame.image.load(LOGO_PATH)
            self.logo = pygame.transform.scale(logo_img, (100, 100))
        except:
            print(f"Warning: Could not load logo from {LOGO_PATH}")
        
        # Polices personnalisées
        try:
            self.title_font = pygame.font.Font(FONT_PATH, 72)
            self.large_font = pygame.font.Font(FONT_PATH, 48)
            self.medium_font = pygame.font.Font(FONT_PATH, 36)
            self.small_font = pygame.font.Font(FONT_PATH, 28)
            self.label_font = pygame.font.Font(FONT_PATH, 32)
        except:
            print(f"Warning: Could not load font from {FONT_PATH}, using default")
            self.title_font = pygame.font.Font(None, 72)
            self.large_font = pygame.font.Font(None, 48)
            self.medium_font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 28)
            self.label_font = pygame.font.Font(None, 32)
        
        # Police SYSTÈME pour les numéros (sans fichier, toujours disponible)
        self.number_font = pygame.font.SysFont('Arial', 40, bold=True)
        
        # Positions des pits
        self.pit_positions = {}
        self.store_positions = {}
        self.setup_positions()
        
        # État du jeu
        self.selected_pit = None
        self.game_over = False
        self.winner_message = ""
        self.animating = False
        self.computer_thinking = False
        
        # Système d'animation
        self.animation_queue = []
        self.current_animation = None
        self.animation_progress = 0
        self.animation_speed = 0.05
        self.waiting_for_computer = False
        
        # Mode de jeu
        self.game_mode = None  # 'human_vs_computer' ou 'computer_vs_computer'
        self.show_menu = True
        self.play_alt = None  # Pour le deuxième ordinateur avec heuristique différente
        self.current_player = 'player2'  # Commence par player2 (humain ou computer2)
        self.extra_turn = False
        
    def setup_positions(self):
        """Configure les positions des pits et stores"""
        # Dimensions
        pit_radius = 45
        store_width = 80
        store_height = 200
        spacing = 120
        vertical_spacing = 140
        
        # Centre du plateau
        center_x = WIDTH // 2
        center_y = HEIGHT // 2 + 20
        
        # Stores
        self.store_positions[1] = pygame.Rect(
            center_x + 350, center_y - store_height // 2, 
            store_width, store_height
        )
        self.store_positions[2] = pygame.Rect(
            center_x - 430, center_y - store_height // 2, 
            store_width, store_height
        )
        
        # Pits Player 2 (G-L) - en haut (inversé) - COMPUTER
        player2_pits = ['L', 'K', 'J', 'I', 'H', 'G']
        start_x = center_x - 300
        y_pos = center_y - vertical_spacing // 2
        
        for i, pit in enumerate(player2_pits):
            x = start_x + i * spacing
            self.pit_positions[pit] = (x, y_pos, pit_radius)
        
        # Pits Player 1 (A-F) - en bas - HUMAN
        player1_pits = ['A', 'B', 'C', 'D', 'E', 'F']
        y_pos = center_y + vertical_spacing // 2
        
        for i, pit in enumerate(player1_pits):
            x = start_x + i * spacing
            self.pit_positions[pit] = (x, y_pos, pit_radius)
    
    def draw_wood_texture(self, surface, rect):
        """Dessine une texture de bois"""
        pygame.draw.rect(surface, BOARD_COLOR, rect, border_radius=20)
        
        # Grain de bois
        for i in range(rect.height // 20):
            y = rect.y + i * 20
            grain_color = (WOOD_GRAIN[0] + (i % 3) * 5, 
                          WOOD_GRAIN[1] + (i % 3) * 5, 
                          WOOD_GRAIN[2] + (i % 3) * 5)
            pygame.draw.line(surface, grain_color, 
                           (rect.x, y), (rect.x + rect.width, y), 1)
    
    def draw_rounded_rect(self, surface, color, rect, radius=10):
        """Dessine un rectangle avec coins arrondis"""
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    
    def draw_menu(self):
        """Dessine le menu de sélection du mode de jeu"""
        # Fond dégradé
        for y in range(HEIGHT):
            color_factor = y / HEIGHT
            r = int(BG_COLOR[0] + (BG_COLOR[0] * 0.4) * color_factor)
            g = int(BG_COLOR[1] + (BG_COLOR[1] * 0.4) * color_factor)
            b = int(BG_COLOR[2] + (BG_COLOR[2] * 0.4) * color_factor)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))
        
        # Titre
        title = self.title_font.render("MANCALA", True, ACCENT_COLOR)
        title_rect = title.get_rect(center=(WIDTH // 2, 100))
        shadow_title = self.title_font.render("MANCALA", True, (30, 20, 10))
        shadow_rect = shadow_title.get_rect(center=(WIDTH // 2 + 3, 103))
        self.screen.blit(shadow_title, shadow_rect)
        self.screen.blit(title, title_rect)
        
        # Sous-titre
        subtitle = self.medium_font.render("Select Game Mode", True, TEXT_COLOR)
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 180))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Bouton 1: Human vs Computer
        button_width = 1000
        button_height = 80
        button1_rect = pygame.Rect(WIDTH // 2 - button_width // 2, 280, button_width, button_height)

        mouse_pos = pygame.mouse.get_pos()
        button1_hover = button1_rect.collidepoint(mouse_pos)
        
        # Dessiner le bouton 1
        color1 = PIT_HOVER_COLOR if button1_hover else BOARD_COLOR
        self.draw_rounded_rect(self.screen, color1, button1_rect, 15)
        pygame.draw.rect(self.screen, ACCENT_COLOR, button1_rect, 4, border_radius=15)
        
        text1 = self.large_font.render("Human vs Computer", True, TEXT_COLOR)
        text1_rect = text1.get_rect(center=button1_rect.center)
        self.screen.blit(text1, text1_rect)
        
        # Bouton 2: Computer vs Computer
        button2_rect = pygame.Rect(WIDTH // 2 - 600, 400, 1200, 80)
        button2_hover = button2_rect.collidepoint(mouse_pos)
        
        # Dessiner le bouton 2
        color2 = PIT_HOVER_COLOR if button2_hover else BOARD_COLOR
        self.draw_rounded_rect(self.screen, color2, button2_rect, 15)
        pygame.draw.rect(self.screen, ACCENT_COLOR, button2_rect, 4, border_radius=15)
        
        text2 = self.large_font.render("Computer vs Computer", True, TEXT_COLOR)
        text2_rect = text2.get_rect(center=button2_rect.center)
        self.screen.blit(text2, text2_rect)
        
        # Instructions
        info = self.small_font.render("Standard AI VS Alternative AI", True, TEXT_COLOR)
        info_rect = info.get_rect(center=(WIDTH // 2, 520))
        self.screen.blit(info, info_rect)
        
        return button1_rect, button2_rect
    
    def draw_seed(self, x, y, radius=6):
        """Dessine une graine/balle individuelle avec effet 3D"""
        # Ombre
        pygame.draw.circle(self.screen, SEED_DARK, (x + 1, y + 1), radius)
        # Graine principale
        pygame.draw.circle(self.screen, SEED_COLOR, (x, y), radius)
        # Highlight pour effet 3D
        pygame.draw.circle(self.screen, (240, 210, 170), (x - 2, y - 2), radius // 2)
    
    def draw_animated_seed(self, start_pos, end_pos, progress):
        """Dessine une graine animée en mouvement"""
        x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
        y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress
        
        # Arc parabolique pour un effet de saut
        arc_height = 50
        y -= arc_height * math.sin(progress * math.pi)
        
        # Graine avec effet de trail
        seed_radius = 8
        # Trail
        trail_length = 5
        for i in range(trail_length):
            alpha = int(255 * (1 - i / trail_length) * 0.3)
            trail_x = x - (end_pos[0] - start_pos[0]) * (i * 0.02)
            trail_y = y - (end_pos[1] - start_pos[1]) * (i * 0.02)
            s = pygame.Surface((seed_radius * 2, seed_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*SEED_COLOR, alpha), (seed_radius, seed_radius), seed_radius - i)
            self.screen.blit(s, (int(trail_x) - seed_radius, int(trail_y) - seed_radius))
        
        # Graine principale animée
        self.draw_seed(int(x), int(y), seed_radius)
    
    def draw_seeds_in_pit(self, x, y, radius, num_seeds):
        """Dessine les graines à l'intérieur d'un pit"""
        if num_seeds == 0:
            return
        
        # Limiter l'affichage visuel à 20 graines max pour éviter l'encombrement
        display_seeds = min(num_seeds, 20)
        seed_radius = 6
        
        if display_seeds == 1:
            self.draw_seed(x, y, seed_radius)
        elif display_seeds == 2:
            self.draw_seed(x - 8, y, seed_radius)
            self.draw_seed(x + 8, y, seed_radius)
        elif display_seeds <= 6:
            # Disposition circulaire
            angle_step = 2 * math.pi / display_seeds
            circle_radius = radius // 3
            for i in range(display_seeds):
                angle = i * angle_step
                sx = x + int(circle_radius * math.cos(angle))
                sy = y + int(circle_radius * math.sin(angle))
                self.draw_seed(sx, sy, seed_radius)
        else:
            # Disposition en grille pour plus de graines
            grid_radius = radius - 15
            positions = []
            
            # Créer une grille de positions possibles
            for gx in range(-grid_radius, grid_radius, 10):
                for gy in range(-grid_radius, grid_radius, 10):
                    if math.sqrt(gx**2 + gy**2) < grid_radius:
                        positions.append((x + gx, y + gy))
            
            # Sélectionner aléatoirement des positions (avec seed fixe pour cohérence)
            random.seed(num_seeds * 100 + x + y)
            selected = random.sample(positions, min(display_seeds, len(positions)))
            
            for sx, sy in selected:
                self.draw_seed(sx, sy, seed_radius - 1)
    
    def draw_seeds_in_store(self, rect, num_seeds):
        """Dessine les graines dans un store"""
        if num_seeds == 0:
            return
        
        # Limiter l'affichage visuel
        display_seeds = min(num_seeds, 30)
        seed_radius = 5
        
        # Zone intérieure du store
        margin = 15
        inner_rect = rect.inflate(-margin * 2, -margin * 2)
        
        positions = []
        for gx in range(inner_rect.left, inner_rect.right, 10):
            for gy in range(inner_rect.top, inner_rect.bottom, 10):
                if inner_rect.collidepoint(gx, gy):
                    positions.append((gx, gy))
        
        random.seed(num_seeds * 100 + rect.x + rect.y)
        selected = random.sample(positions, min(display_seeds, len(positions)))
        
        for sx, sy in selected:
            self.draw_seed(sx, sy, seed_radius)
        
    def draw_pit(self, pit_name, x, y, radius, seeds, is_hoverable=False, is_hovered=False):
        """Dessine un pit avec effet bois sculpté et graines"""
        # Ombre externe
        shadow_surf = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surf, SHADOW_COLOR, (radius + 5, radius + 5), radius + 3)
        self.screen.blit(shadow_surf, (x - radius - 5, y - radius - 5))
        
        # Couleur du pit
        if pit_name in self.play.game.state.player1_pits:
            base_color = PIT_PLAYER_COLOR
        else:
            base_color = PIT_COMPUTER_COLOR
            
        if is_hovered and is_hoverable:
            color = PIT_HOVER_COLOR
        elif is_hoverable:
            color = base_color
        else:
            color = PIT_COLOR
        
        # Pit principal avec effet bois
        pygame.draw.circle(self.screen, color, (x, y), radius)
        
        # Bordure extérieure
        pygame.draw.circle(self.screen, (color[0] - 30, color[1] - 20, color[2] - 15), (x, y), radius, 4)
        
        # Effet de profondeur interne
        pygame.draw.circle(self.screen, (color[0] - 40, color[1] - 30, color[2] - 20), (x, y), radius - 8, 2)
        
        # Highlight supérieur
        pygame.draw.arc(self.screen, (color[0] + 20, color[1] + 15, color[2] + 10), 
                       (x - radius + 5, y - radius + 5, radius * 2 - 10, radius * 2 - 10), 
                       math.pi, math.pi * 2, 2)
        
        # Dessiner les graines à l'intérieur
        self.draw_seeds_in_pit(x, y, radius, seeds)
        
        # Label du pit (lettre) au-dessus
        label = self.label_font.render(pit_name, True, ACCENT_COLOR)
        label_rect = label.get_rect(center=(x, y - radius - 25))
        shadow_label = self.label_font.render(pit_name, True, (30, 20, 10))
        shadow_label_rect = shadow_label.get_rect(center=(x + 2, y - radius - 23))
        self.screen.blit(shadow_label, shadow_label_rect)
        self.screen.blit(label, label_rect)
    
    def draw_store(self, player_num, rect, seeds):
        """Dessine un store (magasin) style coffre en bois avec graines"""
        # Ombre
        shadow_rect = rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        shadow_surf = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, SHADOW_COLOR, (0, 0, rect.width + 10, rect.height + 10), border_radius=15)
        self.screen.blit(shadow_surf, (shadow_rect.x - 5, shadow_rect.y - 5))
        
        # Store principal
        self.draw_rounded_rect(self.screen, STORE_COLOR, rect, 15)
        
        # Dessiner les graines à l'intérieur
        self.draw_seeds_in_store(rect, seeds)
        
        # Bordure dorée
        pygame.draw.rect(self.screen, ACCENT_COLOR, rect, 5, border_radius=15)
        
        # Coins en métal
        corner_size = 15
        corners = [
            (rect.x, rect.y),
            (rect.right - corner_size, rect.y),
            (rect.x, rect.bottom - corner_size),
            (rect.right - corner_size, rect.bottom - corner_size)
        ]
        for cx, cy in corners:
            pygame.draw.rect(self.screen, ACCENT_COLOR, (cx, cy, corner_size, corner_size))
        
        # Le numéro sera dessiné ailleurs
    
    def draw_numbers(self):
        """Dessine tous les numéros de manière simple et claire"""
        # Numéros pour les pits
        for pit_name, (x, y, radius) in self.pit_positions.items():
            seeds = self.play.game.state.board[pit_name]
            
            # Position sous le pit
            text_y = y + radius + 20
            
            # Fond simple
            bg_rect = pygame.Rect(x - 30, text_y - 20, 60, 40)
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(self.screen, (255, 215, 0), bg_rect, 2)
            
            # Numéro en blanc
            text = self.number_font.render(str(seeds), True, (255, 255, 255))
            text_rect = text.get_rect(center=(x, text_y))
            self.screen.blit(text, text_rect)
        
        # Numéros pour les stores
        for store_id, rect in self.store_positions.items():
            seeds = self.play.game.state.board[store_id]
            
            # Position au-dessus du store
            text_y = rect.top - 40
            text_x = rect.centerx
            
            # Fond simple
            bg_rect = pygame.Rect(text_x - 40, text_y - 25, 80, 50)
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(self.screen, (255, 215, 0), bg_rect, 3)
            
            # Numéro en blanc
            text = self.number_font.render(str(seeds), True, (255, 255, 255))
            text_rect = text.get_rect(center=(text_x, text_y))
            self.screen.blit(text, text_rect)
    
    def get_pit_center(self, pit_id):
        """Retourne le centre d'un pit ou store"""
        if pit_id in self.pit_positions:
            x, y, radius = self.pit_positions[pit_id]
            return (x, y)
        elif pit_id in self.store_positions:
            rect = self.store_positions[pit_id]
            return (rect.centerx, rect.centery)
        return None
    
    def create_move_animation(self, from_pit, move_sequence):
        """Crée une séquence d'animation pour un mouvement"""
        animations = []
        for to_pit in move_sequence:
            start_pos = self.get_pit_center(from_pit)
            end_pos = self.get_pit_center(to_pit)
            if start_pos and end_pos:
                animations.append({
                    'start': start_pos,
                    'end': end_pos,
                    'from_pit': from_pit,
                    'to_pit': to_pit
                })
                from_pit = to_pit
        return animations
    
    def draw_board(self):
        """Dessine le plateau de jeu"""
        # Fond dégradé
        for y in range(HEIGHT):
            color_factor = y / HEIGHT
            r = int(BG_COLOR[0] + (BG_COLOR[0] * 0.4) * color_factor)
            g = int(BG_COLOR[1] + (BG_COLOR[1] * 0.4) * color_factor)
            b = int(BG_COLOR[2] + (BG_COLOR[2] * 0.4) * color_factor)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))
        
        # Titre centré
        title = self.title_font.render("MANCALA", True, ACCENT_COLOR)
        title_rect = title.get_rect(center=(WIDTH // 2, 50))
        shadow_title = self.title_font.render("MANCALA", True, (30, 20, 10))
        shadow_rect = shadow_title.get_rect(center=(WIDTH // 2 + 3, 53))
        self.screen.blit(shadow_title, shadow_rect)
        self.screen.blit(title, title_rect)
        
        # Labels selon le mode de jeu
        if self.game_mode == 'computer_vs_computer':
            label1_text = "AI one"
            label2_text = "AI two"
        else:
            label1_text = "COMPUTER"
            label2_text = "HUMAN"
        
        computer_label = self.label_font.render(label1_text, True, ACCENT_COLOR)
        computer_rect = computer_label.get_rect(topright=(WIDTH - 180, 120))
        shadow_computer = self.label_font.render(label1_text, True, (30, 20, 10))
        shadow_comp_rect = shadow_computer.get_rect(topright=(WIDTH - 178, 122))
        self.screen.blit(shadow_computer, shadow_comp_rect)
        self.screen.blit(computer_label, computer_rect)
        
        human_label = self.label_font.render(label2_text, True, ACCENT_COLOR)
        human_rect = human_label.get_rect(topleft=(180, 120))
        shadow_human = self.label_font.render(label2_text, True, (30, 20, 10))
        shadow_human_rect = shadow_human.get_rect(topleft=(182, 122))
        self.screen.blit(shadow_human, shadow_human_rect)
        self.screen.blit(human_label, human_rect)
        
        # Plateau central
        board_rect = pygame.Rect(150, 180, WIDTH - 300, HEIGHT - 280)
        self.draw_wood_texture(self.screen, board_rect)
        
        # Bordure dorée du plateau
        pygame.draw.rect(self.screen, ACCENT_COLOR, board_rect, 6, border_radius=20)
        
        # Décoration intérieure
        inner_rect = board_rect.inflate(-20, -20)
        pygame.draw.rect(self.screen, (218, 165, 32, 100), inner_rect, 2, border_radius=15)
        
        # Stores
        self.draw_store(1, self.store_positions[1], self.play.game.state.board[1])
        self.draw_store(2, self.store_positions[2], self.play.game.state.board[2])
        
        # Pits
        mouse_pos = pygame.mouse.get_pos()
        possible_moves = self.play.game.state.possibleMoves('player2')
        
        for pit_name, (x, y, radius) in self.pit_positions.items():
            seeds = self.play.game.state.board[pit_name]
            is_hoverable = pit_name in possible_moves and not self.game_over and not self.computer_thinking
            
            is_hovered = False
            if is_hoverable:
                dist = math.sqrt((mouse_pos[0] - x)**2 + (mouse_pos[1] - y)**2)
                is_hovered = dist <= radius
            
            self.draw_pit(pit_name, x, y, radius, seeds, is_hoverable, is_hovered)
        
        # Dessiner tous les NUMÉROS par-dessus (dernière étape)
        self.draw_numbers()
        
        # Dessiner les graines animées par-dessus
        if self.current_animation:
            self.draw_animated_seed(
                self.current_animation['start'],
                self.current_animation['end'],
                self.animation_progress
            )
    
    def draw_status(self):
        """Affiche le statut du jeu"""
        if self.computer_thinking:
            status = self.medium_font.render("Computer is thinking...", True, ACCENT_COLOR)
            status_rect = status.get_rect(center=(WIDTH // 2, HEIGHT - 40))
            shadow_status = self.medium_font.render("Computer is thinking...", True, (30, 20, 10))
            shadow_rect = shadow_status.get_rect(center=(WIDTH // 2 + 2, HEIGHT - 38))
            self.screen.blit(shadow_status, shadow_rect)
            self.screen.blit(status, status_rect)
        elif not self.game_over:
            status = self.medium_font.render("Your turn - Click a pit to play", True, ACCENT_COLOR)
            status_rect = status.get_rect(center=(WIDTH // 2, HEIGHT - 40))
            shadow_status = self.medium_font.render("Your turn - Click a pit to play", True, (30, 20, 10))
            shadow_rect = shadow_status.get_rect(center=(WIDTH // 2 + 2, HEIGHT - 38))
            self.screen.blit(shadow_status, shadow_rect)
            self.screen.blit(status, status_rect)
    
    def draw_game_over(self):
        """Affiche l'écran de fin de jeu avec winner/loser"""
        # Overlay semi-transparent
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 15, 10, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Boîte de résultat
        result_rect = pygame.Rect(WIDTH // 2 - 350, HEIGHT // 2 - 200, 700, 400)
        self.draw_wood_texture(self.screen, result_rect)
        pygame.draw.rect(self.screen, ACCENT_COLOR, result_rect, 6, border_radius=20)
        
        # Décoration intérieure
        inner_rect = result_rect.inflate(-20, -20)
        pygame.draw.rect(self.screen, ACCENT_COLOR, inner_rect, 2, border_radius=15)
        
        # Déterminer le gagnant
        winner, score = self.play.game.findWinner()
        player1_score = self.play.game.state.board[1]
        player2_score = self.play.game.state.board[2]
        
        # GAME OVER
        game_over_text = self.large_font.render("GAME OVER", True, ACCENT_COLOR)
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 130))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Noms des joueurs selon le mode
        if self.game_mode == 'computer_vs_computer':
            player1_name = "COMPUTER 1"
            player2_name = "COMPUTER 2"
        else:
            player1_name = "COMPUTER"
            player2_name = "HUMAN"
        
        # WINNER
        if winner == "player1":
            winner_name = player1_name
            loser_name = player2_name
        else:
            winner_name = player2_name
            loser_name = player1_name
        
        winner_text = self.large_font.render(f"WINNER {winner_name}", True, WINNER_COLOR)
        winner_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        shadow_winner = self.large_font.render(f"WINNER {winner_name}", True, (30, 20, 10))
        shadow_winner_rect = shadow_winner.get_rect(center=(WIDTH // 2 + 2, HEIGHT // 2 - 58))
        self.screen.blit(shadow_winner, shadow_winner_rect)
        self.screen.blit(winner_text, winner_rect)
        
        # LOSER
        loser_text = self.large_font.render(f"LOSER {loser_name}", True, LOSER_COLOR)
        loser_rect = loser_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        shadow_loser = self.large_font.render(f"LOSER {loser_name}", True, (30, 20, 10))
        shadow_loser_rect = shadow_loser.get_rect(center=(WIDTH // 2 + 2, HEIGHT // 2 + 2))
        self.screen.blit(shadow_loser, shadow_loser_rect)
        self.screen.blit(loser_text, loser_rect)
        
        # Scores avec la même logique simple que les numéros des pits
        # Player 1 Score
        y_pos = HEIGHT // 2 + 70
        
        # Rectangle fond pour player1
        p1_rect = pygame.Rect(WIDTH // 2 - 150, y_pos - 20, 120, 45)
        pygame.draw.rect(self.screen, (0, 0, 0), p1_rect)
        pygame.draw.rect(self.screen, (255, 215, 0), p1_rect, 3)
        
        # Texte player1
        p1_label = self.number_font.render(player1_name, True, (255, 215, 0))
        p1_label_rect = p1_label.get_rect(center=(WIDTH // 2 - 90, y_pos - 35))
        self.screen.blit(p1_label, p1_label_rect)
        
        p1_score_text = self.number_font.render(str(player1_score), True, (255, 255, 255))
        p1_score_rect = p1_score_text.get_rect(center=(WIDTH // 2 - 90, y_pos))
        self.screen.blit(p1_score_text, p1_score_rect)
        
        # Rectangle fond pour player2
        p2_rect = pygame.Rect(WIDTH // 2 + 30, y_pos - 20, 120, 45)
        pygame.draw.rect(self.screen, (0, 0, 0), p2_rect)
        pygame.draw.rect(self.screen, (255, 215, 0), p2_rect, 3)
        
        # Texte player2
        p2_label = self.number_font.render(player2_name, True, (255, 215, 0))
        p2_label_rect = p2_label.get_rect(center=(WIDTH // 2 + 90, y_pos - 35))
        self.screen.blit(p2_label, p2_label_rect)
        
        p2_score_text = self.number_font.render(str(player2_score), True, (255, 255, 255))
        p2_score_rect = p2_score_text.get_rect(center=(WIDTH // 2 + 90, y_pos))
        self.screen.blit(p2_score_text, p2_score_rect)
        
        # Instructions
        restart_text = self.small_font.render("Press SPACE to restart or ESC to quit", True, ACCENT_COLOR)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 170))
        self.screen.blit(restart_text, restart_rect)
    
    def execute_move_with_animation(self, player, pit_name):
        """Exécute un mouvement avec animation"""
        # Capturer l'état avant le mouvement
        old_board = copy.deepcopy(self.play.game.state.board)
        seeds_to_distribute = old_board[pit_name]
        
        # Exécuter le mouvement et obtenir extra_turn
        extra_turn = self.play.game.state.doMove(player, pit_name)
        self.extra_turn = extra_turn
        
        # Créer la séquence d'animation
        move_sequence = []
        
        # Déterminer la séquence de distribution selon les règles
        current = pit_name
        store = 1 if player == 'player1' else 2
        opponent_store = 2 if store == 1 else 1
        seeds = seeds_to_distribute
        
        next_pit_map = {
            'A': 'B', 'B': 'C', 'C': 'D', 'D': 'E', 'E': 'F', 'F': 1,
            1: 'G', 'G': 'H', 'H': 'I', 'I': 'J', 'J': 'K', 'K': 'L', 'L': 2,
            2: 'A'
        }
        
        while seeds > 0:
            current = next_pit_map[current]
            
            # Ne pas mettre dans le store adverse
            if current == opponent_store:
                continue
            
            move_sequence.append(current)
            seeds -= 1
        
        # Créer les animations
        self.animation_queue = self.create_move_animation(pit_name, move_sequence)
        self.animating = True
    
    def handle_click(self, pos):
        """Gère les clics de souris"""
        if self.game_over or self.computer_thinking or self.animating:
            return
        
        # Mode humain vs computer uniquement
        if self.game_mode != 'human_vs_computer':
            return
        
        # Seulement si c'est le tour du joueur humain
        if self.current_player != 'player2':
            return
        
        possible_moves = self.play.game.state.possibleMoves('player2')
        
        for pit_name in possible_moves:
            if pit_name in self.pit_positions:
                x, y, radius = self.pit_positions[pit_name]
                dist = math.sqrt((pos[0] - x)**2 + (pos[1] - y)**2)
                
                if dist <= radius:
                    # Jouer le coup humain avec animation
                    self.execute_move_with_animation('player2', pit_name)
                    
                    # Vérifier fin de jeu
                    if self.play.game.gameOver():
                        self.game_over = True
                        return
                    
                    # Préparer le prochain tour après l'animation
                    self.waiting_for_computer = True
                    
                    break
    
    def handle_menu_click(self, pos):
        """Gère les clics dans le menu"""
        button1_rect = pygame.Rect(WIDTH // 2 - 250, 280, 500, 80)
        button2_rect = pygame.Rect(WIDTH // 2 - 250, 400, 500, 80)
        
        if button1_rect.collidepoint(pos):
            # Human vs Computer
            self.game_mode = 'human_vs_computer'
            self.show_menu = False
            self.current_player = 'player2'  # Humain commence
        elif button2_rect.collidepoint(pos):
            # Computer vs Computer
            self.game_mode = 'computer_vs_computer'
            self.show_menu = False
            self.play_alt = PlayAlt(self.play.game)
            self.current_player = 'player2'  # Computer2 commence
            self.waiting_for_computer = True  # Démarrer le jeu automatiquement
    
    def update_animation(self):
        """Met à jour l'état de l'animation"""
        if not self.animating:
            # Si on attend le tour de l'ordinateur après l'animation du joueur
            if self.waiting_for_computer:
                self.waiting_for_computer = False
                
                # Vérifier si le joueur actuel a un tour supplémentaire
                if self.extra_turn:
                    self.extra_turn = False
                    # Le même joueur continue
                    if self.current_player == 'player1':
                        # Computer 1 continue
                        pygame.time.wait(300)
                        self.computer_thinking = True
                        computer_pit = self.play.getComputerMove()
                        self.computer_thinking = False
                        self.execute_move_with_animation('player1', computer_pit)
                        if self.play.game.gameOver():
                            self.game_over = True
                        else:
                            self.waiting_for_computer = True
                    else:
                        # Player2 continue (humain ou computer2)
                        if self.game_mode == 'computer_vs_computer':
                            pygame.time.wait(300)
                            self.computer_thinking = True
                            computer_pit = self.play_alt.getComputerMove()
                            self.computer_thinking = False
                            self.execute_move_with_animation('player2', computer_pit)
                            if self.play.game.gameOver():
                                self.game_over = True
                            else:
                                self.waiting_for_computer = True
                        # Sinon c'est un humain, il peut jouer
                    return
                
                # Changer de joueur
                if self.current_player == 'player2':
                    # Tour de Computer 1
                    self.current_player = 'player1'
                    self.computer_thinking = True
                    pygame.time.wait(500)
                    computer_pit = self.play.getComputerMove()
                    self.computer_thinking = False
                    self.execute_move_with_animation('player1', computer_pit)
                    if self.play.game.gameOver():
                        self.game_over = True
                    else:
                        self.waiting_for_computer = True
                else:
                    # Tour de Player2 (humain ou computer2)
                    self.current_player = 'player2'
                    if self.game_mode == 'computer_vs_computer':
                        self.computer_thinking = True
                        pygame.time.wait(500)
                        computer_pit = self.play_alt.getComputerMove()
                        self.computer_thinking = False
                        self.execute_move_with_animation('player2', computer_pit)
                        if self.play.game.gameOver():
                            self.game_over = True
                        else:
                            self.waiting_for_computer = True
            return
        
        if self.current_animation is None:
            # Démarrer la prochaine animation
            if self.animation_queue:
                self.current_animation = self.animation_queue.pop(0)
                self.animation_progress = 0
            else:
                # Toutes les animations sont terminées
                self.animating = False
                return
        
        # Avancer l'animation
        self.animation_progress += self.animation_speed
        
        if self.animation_progress >= 1.0:
            # Animation terminée
            self.current_animation = None
            self.animation_progress = 0
    
    def reset_game(self):
        """Réinitialise le jeu"""
        self.play = Play()
        self.game_over = False
        self.winner_message = ""
        self.computer_thinking = False
        self.animation_queue = []
        self.current_animation = None
        self.animation_progress = 0
        self.waiting_for_computer = False
        self.current_player = 'player2'
        self.extra_turn = False
        self.show_menu = True
        self.game_mode = None
        self.play_alt = None
    
    def run(self):
        """Boucle principale du jeu"""
        running = True
        
        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.show_menu:
                            self.handle_menu_click(event.pos)
                        else:
                            self.handle_click(event.pos)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE and self.game_over:
                        self.reset_game()
            
            # Afficher le menu ou le jeu
            if self.show_menu:
                self.draw_menu()
            else:
                # Mettre à jour les animations
                self.update_animation()
                
                # Dessin
                self.draw_board()
                self.draw_status()
                
                if self.game_over:
                    self.draw_game_over()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = MancalaGUI()
    game.run()