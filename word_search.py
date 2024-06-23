import pygame
import sys
import random
import time

# using Trie for efficiently searching  word in grid 
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True


class Solution:
    def __init__(self, board, words):
        self.board = board
        self.words = words
        self.result = set()
        self.trie = Trie()
        for word in words:
            self.trie.insert(word)

    def findWords(self):
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col] in self.trie.root.children:
                    self.backtrack(row, col, self.trie.root, "")
        return list(self.result)

    def backtrack(self, row, col, parent, word_path):
        letter = self.board[row][col]
        curr_node = parent.children.get(letter)

        if not curr_node:
            return

        word_path += letter
        if curr_node.is_end_of_word:
            self.result.add(word_path)
            curr_node.is_end_of_word = False  

        self.board[row][col] = '#'  
        for row_offset, col_offset in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_row, new_col = row + row_offset, col + col_offset
            if 0 <= new_row < len(self.board) and 0 <= new_col < len(self.board[0]):
                if self.board[new_row][new_col] in curr_node.children:
                    self.backtrack(new_row, new_col, curr_node, word_path)

        self.board[row][col] = letter 

        if not curr_node.children:
            parent.children.pop(letter, None)


pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
GRID_SIZE = 12  
CELL_SIZE = SCREEN_WIDTH // GRID_SIZE
BG_COLOR = (255, 255, 255)
LINE_COLOR = (0, 0, 0)
FONT_COLOR = (0, 0, 0)
HIGHLIGHT_COLOR = (173, 216, 230)
FOUND_WORD_COLOR = (34, 139, 34)
HINT_SECTION_WIDTH = 200
HINT_SECTION_HEIGHT = SCREEN_HEIGHT
HINT_BG_COLOR = (240, 240, 240)
TIMER_COLOR = (255, 0, 0)
score = 0


screen = pygame.display.set_mode((SCREEN_WIDTH + HINT_SECTION_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Word Search Game")

# Font setting
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)


def draw_grid(board):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BG_COLOR, rect)
            pygame.draw.rect(screen, LINE_COLOR, rect, 1)

           
            if board[row][col]:
                letter_surface = font.render(board[row][col], True, FONT_COLOR)
                screen.blit(letter_surface, (col * CELL_SIZE + 10, row * CELL_SIZE + 10))


def draw_clues(clues):
    pygame.draw.rect(screen, HINT_BG_COLOR, (SCREEN_WIDTH, 0, HINT_SECTION_WIDTH, HINT_SECTION_HEIGHT))
    y_offset = 10  
    for index, clue in enumerate(clues):
        clue_text = f"{index + 1}. {clue}"
        clue_surface = small_font.render(clue_text, True, FONT_COLOR)
        screen.blit(clue_surface, (SCREEN_WIDTH + 10, y_offset))
        y_offset += 30


def draw_timer(elapsed_time):
    timer_text = f"Time: {elapsed_time:.1f}s"
    timer_surface = small_font.render(timer_text, True, TIMER_COLOR)
    screen.blit(timer_surface, (SCREEN_WIDTH + 10, SCREEN_HEIGHT - 50))


def generate_board(words):
    board = [["" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    placed_words = []

    for word in words:
        word_placed = False
        while not word_placed:
            orientation = random.choice(["horizontal", "vertical", "diagonal"])
            if orientation == "horizontal":
                start_row = random.randint(0, GRID_SIZE - 1)
                start_col = random.randint(0, GRID_SIZE - len(word))
                if all(board[start_row][start_col + i] == "" or board[start_row][start_col + i] == word[i] for i in range(len(word))):
                    for i in range(len(word)):
                        board[start_row][start_col + i] = word[i]
                    placed_words.append(word)
                    word_placed = True
            elif orientation == "vertical":
                start_row = random.randint(0, GRID_SIZE - len(word))
                start_col = random.randint(0, GRID_SIZE - 1)
                if all(board[start_row + i][start_col] == "" or board[start_row + i][start_col] == word[i] for i in range(len(word))):
                    for i in range(len(word)):
                        board[start_row + i][start_col] = word[i]
                    placed_words.append(word)
                    word_placed = True
            elif orientation == "diagonal":
                start_row = random.randint(0, GRID_SIZE - len(word))
                start_col = random.randint(0, GRID_SIZE - len(word))
                if all(board[start_row + i][start_col + i] == "" or board[start_row + i][start_col + i] == word[i] for i in range(len(word))):
                    for i in range(len(word)):
                        board[start_row + i][start_col + i] = word[i]
                    placed_words.append(word)
                    word_placed = True


    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if board[row][col] == "":
                board[row][col] = random.choice(letters)

    return board


def generate_words():
    words = ["EARTH", "PYTHON", "HELLO", "WORLD", "CODE"]
    random.shuffle(words)
    return words[:5]  


words = generate_words()
board = generate_board(words)
solution = Solution(board, words)
clues = ["Greeting", "Earth", "Programming language", "Game library", "Script"]


running = True
current_input = ""
selected_row, selected_col = 0, 0
direction = "across" 
found_words = []
start_time = time.time()

def display_found_words():
    y_offset = 200
    for word in found_words:
        word_surface = small_font.render(word, True, FOUND_WORD_COLOR)
        screen.blit(word_surface, (SCREEN_WIDTH + 10, y_offset))
        y_offset += 30

def highlight_word(word):
    found = False
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if solution.board[row][col] == word[0]:
                if check_word_in_direction(word, row, col, "across"):
                    highlight_cells(word, row, col, "across")
                    found = True
                if check_word_in_direction(word, row, col, "down"):
                    highlight_cells(word, row, col, "down")
                    found = True
    if found:
        global score
        score += 1  
        print("score",score)
    return found

def check_word_in_direction(word, start_row, start_col, direction):
    if direction == "across":
        if start_col + len(word) > GRID_SIZE:
            return False
        for i in range(len(word)):
            if solution.board[start_row][start_col + i] != word[i]:
                return False
        return True
    elif direction == "down":
        if start_row + len(word) > GRID_SIZE:
            return False
        for i in range(len(word)):
            if solution.board[start_row + i][start_col] != word[i]:
                return False
        return True
    return False

def highlight_cells(word, start_row, start_col, direction):
    if direction == "across":
        for i in range(len(word)):
            solution.board[start_row][start_col + i] = solution.board[start_row][start_col + i].upper()
    elif direction == "down":
        for i in range(len(word)):
            solution.board[start_row + i][start_col] = solution.board[start_row + i][start_col].upper()

def draw_score(score):
    score_text = f"Score: {score}"
    score_surface = small_font.render(score_text, True, TIMER_COLOR)
    screen.blit(score_surface, (SCREEN_WIDTH + 10, SCREEN_HEIGHT - 80))

while running:
    screen.fill(BG_COLOR)
    draw_grid(board)
    draw_clues(clues)


    display_found_words()

    elapsed_time = time.time() - start_time
    draw_timer(elapsed_time)


    draw_score(score)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if y < SCREEN_HEIGHT: 
                selected_row, selected_col = y // CELL_SIZE, x // CELL_SIZE
        elif event.type == pygame.KEYDOWN:
            if event.unicode.isalpha():
                board[selected_row][selected_col] = event.unicode.upper()
                current_input += event.unicode.upper()

             
                if current_input in words and highlight_word(current_input):
                    if current_input not in found_words:
                        found_words.append(current_input)
                    current_input = ""  
                else:
          
                    if direction == "across":
                        selected_col = (selected_col + 1) % GRID_SIZE
                    elif direction == "down":
                        selected_row = (selected_row + 1) % GRID_SIZE

            elif event.key == pygame.K_TAB:
                direction = "down" if direction == "across" else "across"

    rect = pygame.Rect(selected_col * CELL_SIZE, selected_row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, HIGHLIGHT_COLOR, rect)
    pygame.draw.rect(screen, LINE_COLOR, rect, 1)

    pygame.display.flip()

pygame.quit()
sys.exit()
