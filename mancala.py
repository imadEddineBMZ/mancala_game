import copy
import math

# Constantes
MAX = 1      # COMPUTER
MIN = -1     # HUMAN


# ==============================
# Classe MancalaBoard
# ==============================
class MancalaBoard:

    def __init__(self):
        # Plateau du jeu
        self.board = {
            'A': 4, 'B': 4, 'C': 4, 'D': 4, 'E': 4, 'F': 4,
            'G': 4, 'H': 4, 'I': 4, 'J': 4, 'K': 4, 'L': 4,
            1: 0,   # Store Player 1
            2: 0    # Store Player 2
        }

        # Pits de chaque joueur
        self.player1_pits = ('A', 'B', 'C', 'D', 'E', 'F')
        self.player2_pits = ('G', 'H', 'I', 'J', 'K', 'L')

        # Pits opposés
        self.opposite = {
            'A': 'L', 'B': 'K', 'C': 'J', 'D': 'I', 'E': 'H', 'F': 'G',
            'G': 'F', 'H': 'E', 'I': 'D', 'J': 'C', 'K': 'B', 'L': 'A'
        }

        # Ordre de distribution
        self.next_pit = {
            'A': 'B', 'B': 'C', 'C': 'D', 'D': 'E', 'E': 'F', 'F': 1,
            1: 'G', 'G': 'H', 'H': 'I', 'I': 'J', 'J': 'K', 'K': 'L', 'L': 2,
            2: 'A'
        }

    # Coups possibles pour un joueur
    def possibleMoves(self, player):
        moves = []
        pits = self.player1_pits if player == 'player1' else self.player2_pits
        for pit in pits:
            if self.board[pit] > 0:
                moves.append(pit)
        return moves

    # Exécuter un coup
    def doMove(self, player, pit):
        seeds = self.board[pit]
        self.board[pit] = 0
        current = pit

        store = 1 if player == 'player1' else 2
        opponent_store = 2 if store == 1 else 1
        own_pits = self.player1_pits if player == 'player1' else self.player2_pits

        while seeds > 0:
            current = self.next_pit[current]

            # Ne pas mettre dans le store adverse
            if current == opponent_store:
                continue

            self.board[current] += 1
            seeds -= 1

        # Capture
        if current in own_pits and self.board[current] == 1:
            opposite_pit = self.opposite[current]
            captured = self.board[opposite_pit]
            if captured > 0:
                self.board[store] += captured + 1
                self.board[current] = 0
                self.board[opposite_pit] = 0


# ==============================
# Classe Game
# ==============================
class Game:

    def __init__(self):
        self.state = MancalaBoard()
        self.playerSide = {
            MAX: 'player1',   # COMPUTER
            MIN: 'player2'    # HUMAN
        }

    # Vérifier fin du jeu
    def gameOver(self):
        p1_empty = all(self.state.board[p] == 0 for p in self.state.player1_pits)
        p2_empty = all(self.state.board[p] == 0 for p in self.state.player2_pits)

        if p1_empty or p2_empty:
            # Collecter graines restantes
            for pit in self.state.player1_pits:
                self.state.board[1] += self.state.board[pit]
                self.state.board[pit] = 0

            for pit in self.state.player2_pits:
                self.state.board[2] += self.state.board[pit]
                self.state.board[pit] = 0

            return True

        return False

    # Trouver le gagnant
    def findWinner(self):
        s1 = self.state.board[1]
        s2 = self.state.board[2]

        if s1 > s2:
            return "PLAYER 1 (COMPUTER)", s1
        elif s2 > s1:
            return "PLAYER 2 (HUMAN)", s2
        else:
            return "DRAW", s1

    # Fonction d'évaluation (équation du prof)
    def evaluate(self):
        return self.state.board[1] - self.state.board[2]


# ==============================
# Classe Play
# ==============================
class Play:

    def __init__(self):
        self.game = Game()

    def displayBoard(self):
        b = self.game.state.board
        print("\n      L  K  J  I  H  G")
        print("    ", b['L'], b['K'], b['J'], b['I'], b['H'], b['G'])
        print(b[2], "                   ", b[1])
        print("    ", b['A'], b['B'], b['C'], b['D'], b['E'], b['F'])
        print("      A  B  C  D  E  F\n")

    # Tour humain
    def humanTurn(self):
        moves = self.game.state.possibleMoves('player2')
        print("Your possible moves:", moves)
        pit = input("Choose a pit: ").upper()
        while pit not in moves:
            pit = input("Invalid move. Choose again: ").upper()
        self.game.state.doMove('player2', pit)

    # Tour ordinateur
    def computerTurn(self):
        _, pit = self.MinimaxAlphaBetaPruning(
            self.game, MAX, 5, -math.inf, math.inf
        )
        print("Computer plays:", pit)
        self.game.state.doMove('player1', pit)

    # Algorithme Minimax Alpha-Beta (exactement comme l'énoncé)
    def MinimaxAlphaBetaPruning(self, game, player, depth, alpha, beta):

        if game.gameOver() or depth == 1:
            bestValue = game.evaluate()
            return bestValue, None

        if player == MAX:
            bestValue = -math.inf
            bestPit = None
            for pit in game.state.possibleMoves(game.playerSide[player]):
                child_game = copy.deepcopy(game)
                child_game.state.doMove(game.playerSide[player], pit)
                value, _ = self.MinimaxAlphaBetaPruning(
                    child_game, -player, depth - 1, alpha, beta
                )
                if value > bestValue:
                    bestValue = value
                    bestPit = pit
                if bestValue >= beta:
                    break
                if bestValue > alpha:
                    alpha = bestValue
            return bestValue, bestPit

        else:
            bestValue = math.inf
            bestPit = None
            for pit in game.state.possibleMoves(game.playerSide[player]):
                child_game = copy.deepcopy(game)
                child_game.state.doMove(game.playerSide[player], pit)
                value, _ = self.MinimaxAlphaBetaPruning(
                    child_game, -player, depth - 1, alpha, beta
                )
                if value < bestValue:
                    bestValue = value
                    bestPit = pit
                if bestValue <= alpha:
                    break
                if bestValue < beta:
                    beta = bestValue
            return bestValue, bestPit


# ==============================
# Programme principal
# ==============================
if __name__ == "__main__":
    play = Play()

    while not play.game.gameOver():
        play.displayBoard()
        play.humanTurn()
        if play.game.gameOver():
            break
        play.computerTurn()

    play.displayBoard()
    winner, score = play.game.findWinner()
    print("Winner:", winner, "with score:", score)
