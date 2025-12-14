import pygame
import sys
import math
from mancala import Play, MAX, MIN

# Initialisation de pygame
pygame.init()

# Constantes de l'interface
WIDTH, HEIGHT = 1200, 700
FPS = 60

# Couleurs modernes
BG_COLOR = (20, 25, 35)
BOARD_COLOR = (45, 52, 70)
PIT_COLOR = (60, 68, 88)
PIT_HOVER_COLOR = (80, 90, 110)
PIT_PLAYER_COLOR = (70, 130, 180)
PIT_COMPUTER_COLOR = (180, 70, 90)
STORE_COLOR = (35, 42, 58)
SEED_COLOR = (255, 215, 100)
TEXT_COLOR = (230, 230, 240)
ACCENT_COLOR = (100, 200, 255)
WINNER_COLOR = (50, 205, 50)
SHADOW_COLOR = (10, 15, 25, 100)

# Police
pygame.font.init()


class MancalaGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Mancala - Modern Edition")
        self.clock = pygame.time.Clock()
        self.play = Play()
        
        # Polices
        self.title_font = pygame.font.Font(None, 72)
        self.large_font = pygame.font.Font(None, 48)
        self.medium_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        
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
        
    def setup_positions(self):
        """Configure les positions des pits et stores"""
        # Dimensions
        pit_radius = 45
        store_width = 80
        store_height = 200
        spacing = 120
        
        # Centre du plateau
        center_x = WIDTH // 2
        center_y = HEIGHT // 2
        
        # Stores
        self.store_positions[1] = pygame.Rect(
            center_x + 350, center_y - store_height // 2, 
            store_width, store_height
        )
        self.store_positions[2] = pygame.Rect(
            center_x - 430, center_y - store_height // 2, 
            store_width, store_height
        )
        
        # Pits Player 1 (A-F) - en bas
        player1_pits = ['A', 'B', 'C', 'D', 'E', 'F']
        start_x = center_x - 300
        y_pos = center_y + 80
        
        for i, pit in enumerate(player1_pits):
            x = start_x + i * spacing
            self.pit_positions[pit] = (x, y_pos, pit_radius)
        
        # Pits Player 2 (G-L) - en haut (inversé)
        player2_pits = ['L', 'K', 'J', 'I', 'H', 'G']
        y_pos = center_y - 80
        
        for i, pit in enumerate(player2_pits):
            x = start_x + i * spacing
            self.pit_positions[pit] = (x, y_pos, pit_radius)
    
    def draw_rounded_rect(self, surface, color, rect, radius=10):
        """Dessine un rectangle avec coins arrondis"""
        pygame.draw.rect(surface, color, rect, border_radius=radius)
        
    def draw_pit(self, pit_name, x, y, radius, seeds, is_hoverable=False, is_hovered=False):
        """Dessine un pit avec effet 3D"""
        # Ombre
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
        
        # Pit principal
        pygame.draw.circle(self.screen, color, (x, y), radius)
        pygame.draw.circle(self.screen, (color[0] - 20, color[1] - 20, color[2] - 20), (x, y), radius, 3)
        
        # Effet de profondeur
        pygame.draw.circle(self.screen, (color[0] - 30, color[1] - 30, color[2] - 30), (x, y), radius - 5, 2)
        
        # Graines
        if seeds > 0:
            self.draw_seeds(x, y, radius - 10, seeds)
        
        # Texte du nombre de graines
        seed_text = self.medium_font.render(str(seeds), True, TEXT_COLOR)
        text_rect = seed_text.get_rect(center=(x, y + radius + 25))
        self.screen.blit(seed_text, text_rect)
        
        # Label du pit
        label = self.small_font.render(pit_name, True, ACCENT_COLOR)
        label_rect = label.get_rect(center=(x, y - radius - 25))
        self.screen.blit(label, label_rect)
    
    def draw_seeds(self, center_x, center_y, max_radius, count):
        """Dessine les graines dans un pit"""
        if count == 0:
            return
        
        if count <= 8:
            angle_step = 2 * math.pi / count
            for i in range(count):
                angle = i * angle_step
                seed_x = center_x + int(max_radius * 0.6 * math.cos(angle))
                seed_y = center_y + int(max_radius * 0.6 * math.sin(angle))
                pygame.draw.circle(self.screen, SEED_COLOR, (seed_x, seed_y), 6)
                pygame.draw.circle(self.screen, (200, 170, 70), (seed_x, seed_y), 6, 1)
        else:
            # Pour beaucoup de graines, dessiner un groupe
            for i in range(min(count, 15)):
                angle = (i / 15) * 2 * math.pi
                radius_var = max_radius * 0.5 * (0.5 + 0.5 * (i % 3) / 2)
                seed_x = center_x + int(radius_var * math.cos(angle))
                seed_y = center_y + int(radius_var * math.sin(angle))
                pygame.draw.circle(self.screen, SEED_COLOR, (seed_x, seed_y), 5)
    
    def draw_store(self, player_num, rect, seeds):
        """Dessine un store (magasin)"""
        # Ombre
        shadow_rect = rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        shadow_surf = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, SHADOW_COLOR, (0, 0, rect.width + 10, rect.height + 10), border_radius=15)
        self.screen.blit(shadow_surf, (shadow_rect.x - 5, shadow_rect.y - 5))
        
        # Store principal
        self.draw_rounded_rect(self.screen, STORE_COLOR, rect, 15)
        pygame.draw.rect(self.screen, ACCENT_COLOR, rect, 4, border_radius=15)
        
        # Label
        player_label = "COMPUTER" if player_num == 1 else "HUMAN"
        label = self.small_font.render(player_label, True, ACCENT_COLOR)
        label_rect = label.get_rect(center=(rect.centerx, rect.y + 30))
        self.screen.blit(label, label_rect)
        
        # Score
        score_text = self.large_font.render(str(seeds), True, TEXT_COLOR)
        score_rect = score_text.get_rect(center=(rect.centerx, rect.centery))
        self.screen.blit(score_text, score_rect)
        
        # Icône de graines
        seed_icon = self.small_font.render("●" * min(seeds // 3, 10), True, SEED_COLOR)
        icon_rect = seed_icon.get_rect(center=(rect.centerx, rect.bottom - 30))
        self.screen.blit(seed_icon, icon_rect)
    
    def draw_board(self):
        """Dessine le plateau de jeu"""
        # Fond dégradé
        for y in range(HEIGHT):
            color_factor = y / HEIGHT
            r = int(BG_COLOR[0] + (BG_COLOR[0] * 0.3) * color_factor)
            g = int(BG_COLOR[1] + (BG_COLOR[1] * 0.3) * color_factor)
            b = int(BG_COLOR[2] + (BG_COLOR[2] * 0.3) * color_factor)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))
        
        # Titre
        title = self.title_font.render("MANCALA", True, ACCENT_COLOR)
        title_rect = title.get_rect(center=(WIDTH // 2, 60))
        self.screen.blit(title, title_rect)
        
        # Plateau central
        board_rect = pygame.Rect(150, 150, WIDTH - 300, HEIGHT - 200)
        self.draw_rounded_rect(self.screen, BOARD_COLOR, board_rect, 20)
        
        # Stores
        self.draw_store(1, self.store_positions[1], self.play.game.state.board[1])
        self.draw_store(2, self.store_positions[2], self.play.game.state.board[2])
        
        # Pits
        mouse_pos = pygame.mouse.get_pos()
        possible_moves = self.play.game.state.possibleMoves('player2')
        
        for pit_name, (x, y, radius) in self.pit_positions.items():
            seeds = self.play.game.state.board[pit_name]
            is_hoverable = pit_name in possible_moves and not self.game_over and not self.computer_thinking
            
            # Vérifier si la souris survole ce pit
            is_hovered = False
            if is_hoverable:
                dist = math.sqrt((mouse_pos[0] - x)**2 + (mouse_pos[1] - y)**2)
                is_hovered = dist <= radius
            
            self.draw_pit(pit_name, x, y, radius, seeds, is_hoverable, is_hovered)
    
    def draw_status(self):
        """Affiche le statut du jeu"""
        if self.computer_thinking:
            status = self.medium_font.render("Computer is thinking...", True, ACCENT_COLOR)
            status_rect = status.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            self.screen.blit(status, status_rect)
        elif not self.game_over:
            status = self.medium_font.render("Your turn - Click a pit to play", True, ACCENT_COLOR)
            status_rect = status.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            self.screen.blit(status, status_rect)
    
    def draw_game_over(self):
        """Affiche l'écran de fin de jeu"""
        # Overlay semi-transparent
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Boîte de résultat
        result_rect = pygame.Rect(WIDTH // 2 - 300, HEIGHT // 2 - 150, 600, 300)
        self.draw_rounded_rect(self.screen, BOARD_COLOR, result_rect, 20)
        pygame.draw.rect(self.screen, ACCENT_COLOR, result_rect, 4, border_radius=20)
        
        # Texte du gagnant
        winner, score = self.play.game.findWinner()
        
        game_over_text = self.large_font.render("GAME OVER", True, ACCENT_COLOR)
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        self.screen.blit(game_over_text, game_over_rect)
        
        winner_text = self.medium_font.render(f"Winner: {winner}", True, WINNER_COLOR)
        winner_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        self.screen.blit(winner_text, winner_rect)
        
        score_text = self.medium_font.render(f"Score: {score}", True, TEXT_COLOR)
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        self.screen.blit(score_text, score_rect)
        
        # Instructions
        restart_text = self.small_font.render("Press SPACE to restart or ESC to quit", True, TEXT_COLOR)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 90))
        self.screen.blit(restart_text, restart_rect)
    
    def handle_click(self, pos):
        """Gère les clics de souris"""
        if self.game_over or self.computer_thinking:
            return
        
        possible_moves = self.play.game.state.possibleMoves('player2')
        
        for pit_name in possible_moves:
            if pit_name in self.pit_positions:
                x, y, radius = self.pit_positions[pit_name]
                dist = math.sqrt((pos[0] - x)**2 + (pos[1] - y)**2)
                
                if dist <= radius:
                    # Jouer le coup humain
                    self.play.game.state.doMove('player2', pit_name)
                    
                    # Vérifier fin de jeu
                    if self.play.game.gameOver():
                        self.game_over = True
                        return
                    
                    # Tour de l'ordinateur
                    self.computer_thinking = True
                    pygame.display.flip()
                    pygame.time.wait(500)  # Pause pour l'effet
                    
                    self.play.computerTurn()
                    self.computer_thinking = False
                    
                    # Vérifier fin de jeu après l'ordinateur
                    if self.play.game.gameOver():
                        self.game_over = True
                    
                    break
    
    def reset_game(self):
        """Réinitialise le jeu"""
        self.play = Play()
        self.game_over = False
        self.winner_message = ""
        self.computer_thinking = False
    
    def run(self):
        """Boucle principale du jeu"""
        running = True
        
        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic gauche
                        self.handle_click(event.pos)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE and self.game_over:
                        self.reset_game()
            
            # Dessin
            self.draw_board()
            self.draw_status()
            
            if self.game_over:
                self.draw_game_over()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()


# ==============================
# Programme principal
# ==============================
if __name__ == "__main__":
    game = MancalaGUI()
    game.run()
