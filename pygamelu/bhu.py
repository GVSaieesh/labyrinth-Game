import pygame
import random
import time

# Initialize pygame
pygame.init()

# Set up the screen
WIDTH, HEIGHT = 1200, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Magic Tower Puzzle Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)

# Fonts
font = pygame.font.Font(None, 36)

# Game Clock
clock = pygame.time.Clock()

# Define the Magic Tower Puzzle Bot
class MagicTowerPuzzleGame:
    def __init__(self, depth_limit=3, time_limit=30):
        self.puzzles = [
            {"question": "The more of me you take, the more you leave behind. What am I?",
     "answer": ["footsteps"],
     "hints": ["It involves movement.", "You leave them on the ground.", "You create them while walking."]},

    {"question": "The person who makes it sells it. The person who buys it never uses it. The person who uses it never knows they are using it. What is it?",
     "answer": ["coffin"],
     "hints": ["It's used after death.", "It is made of wood or metal.", "People are buried in it."]},

    {"question": "I can be cracked, made, told, and played. What am I?",
     "answer": ["joke"],
     "hints": ["It is meant to be funny.", "People tell it to make others laugh.", "It has a punchline."]},

    {"question": "I fly without wings, I cry without eyes. Wherever I go, darkness follows me. What am I?",
     "answer": ["cloud"],
     "hints": ["You can see me in the sky.", "I bring rain.", "I can block the sun."]},

    {"question": "The more you remove from me, the bigger I get. What am I?",
     "answer": ["hole"],
     "hints": ["It can be dug.", "It appears when something is missing.", "You find it in the ground or in objects."]},

    {"question": "I have hands but can’t clap. What am I?",
     "answer": ["clock"],
     "hints": ["You find me on walls or wrists.", "I tell time.", "I have two hands pointing to numbers."]},

    {"question": "What has an endless supply of letters but starts empty?",
     "answer": ["mailbox"],
     "hints": ["You use me to send and receive.", "I have a flag in some countries.", "You can find me outside houses."]},

    {"question": "I shave every day, but my beard stays the same. What am I?",
     "answer": ["barber"],
     "hints": ["I work in a shop.", "I cut hair.", "People visit me for grooming."]},

    

    {"question": "I go up but never come down. What am I?",
     "answer": ["age"],
     "hints": ["Everyone will count me.", "It increases every year.", "You celebrate it once a year."]}
]
        self.depth_limit = depth_limit
        self.time_limit = time_limit  # Global time for all puzzles
        self.score = 0
        self.current_puzzle = None
        self.hint_index = 0
        self.start_time = time.time()  # Global timer starts when game starts
        self.running = True
        self.input_text = ""
        self.start_new_puzzle()

    def start_new_puzzle(self):
        self.current_puzzle = random.choice(self.puzzles)
        self.hint_index = 0
        self.input_text = ""  # Reset input text to clear previous answer

    def check_answer(self):
        if self.input_text.lower().strip() in self.current_puzzle["answer"]:
            self.score += 10 - (self.hint_index * 2)
            self.start_new_puzzle()
            return "correct"
        return "incorrect"

    def get_hint(self):
        if self.hint_index < len(self.current_puzzle["hints"]):
            hint = self.current_puzzle["hints"][self.hint_index]
            self.hint_index += 1
            return hint
        return "No more hints!"

    def time_remaining(self):
        elapsed_time = time.time() - self.start_time
        return max(0, self.time_limit - elapsed_time)

# Initialize the game
game = MagicTowerPuzzleGame()

# Game Loop
while game.running:
    screen.fill(WHITE)
    
    if game.score >= 40:
        win_text = font.render("Congrats! You Won!", True, GREEN)
        screen.blit(win_text, (WIDTH // 2 - 100, HEIGHT // 2))
        pygame.display.flip()
        time.sleep(3)
        break
    
    games = font.render("You are trapped in a tower. Answer the questions to escape(score=40)", True, RED)
    screen.blit(games, (50, 50))
    
    question_text = font.render(game.current_puzzle["question"], True, BLACK)
    screen.blit(question_text, (50, 100))
    
    time_left = game.time_remaining()
    timer_text = font.render(f"Time Left: {int(time_left)}s", True, RED)
    screen.blit(timer_text, (600, 150))
    
    score_text = font.render(f"Score: {game.score}", True, BLUE)
    screen.blit(score_text, (600, 200))
    
    input_box = pygame.Rect(50, 150, 400, 40)
    pygame.draw.rect(screen, GRAY, input_box)
    user_text = font.render(game.input_text, True, BLACK)
    screen.blit(user_text, (60, 160))
    
    hint_box = pygame.Rect(50, 250, 150, 40)
    pygame.draw.rect(screen, GREEN, hint_box)
    hint_text = font.render("Get Hint", True, WHITE)
    screen.blit(hint_text, (70, 260))
    
    submit_box = pygame.Rect(250, 250, 150, 40)
    pygame.draw.rect(screen, BLUE, submit_box)
    submit_text = font.render("Submit", True, WHITE)
    screen.blit(submit_text, (270, 260))
    
    skip_box = pygame.Rect(450, 250, 150, 40)
    pygame.draw.rect(screen, RED, skip_box)
    skip_text = font.render("Skip", True, WHITE)
    screen.blit(skip_text, (490, 260))
    
    hint_display = font.render("" if game.hint_index == 0 else f"Hint: {game.current_puzzle['hints'][game.hint_index-1]}", True, BLACK)
    screen.blit(hint_display, (50, 350))
    
    if time_left <= 0:
        game.running = False
        print(f"⏳ Time's up! Final Score: {game.score}")
        break
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                game.check_answer()
            elif event.key == pygame.K_BACKSPACE:
                game.input_text = game.input_text[:-1]
            else:
                game.input_text += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if hint_box.collidepoint(event.pos):
                hint_display = font.render(game.get_hint(), True, BLACK)
            elif submit_box.collidepoint(event.pos):
                game.check_answer()
            elif skip_box.collidepoint(event.pos):
                game.score -= 5
                game.start_new_puzzle()
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()