import pygame
import random

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Word Rearrangement Puzzle")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)

# Fonts
font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 30)

# Define a list of valid words for the puzzle
valid_words = ["puzzle", "python", "climbing", "search", "algorithm", "heuristic"]

# Choose a random target word
target_word = random.choice(valid_words)

# Scramble the word to create the puzzle
def scramble(word):
    word = list(word)
    random.shuffle(word)
    return "".join(word)

scrambled_word = scramble(target_word)

# Hill Climbing Algorithm for Hints
def hill_climb_hint(word):
    """ Uses hill climbing to improve the scrambled word step by step. """
    word = list(word)
    
    def heuristic(w):
        """ Heuristic: Count how many letters are in the correct position. """
        return sum(1 for i in range(len(target_word)) if w[i] == target_word[i])

    current_score = heuristic(word)

    for _ in range(5):  # Try to improve for 5 iterations
        if current_score == len(target_word):
            break
        
        # Swap two random letters
        i, j = random.sample(range(len(word)), 2)
        word[i], word[j] = word[j], word[i]

        new_score = heuristic(word)

        # If the new state is better, accept it
        if new_score >= current_score:
            current_score = new_score
        else:
            # Revert the swap if no improvement
            word[i], word[j] = word[j], word[i]

    return "".join(word)

# Game variables
input_text = ""
attempts = 3
hint = ""

# Game loop
running = True
while running:
    screen.fill(WHITE)

    # Display scrambled word
    scrambled_surface = font.render(f"Scrambled Word: {scrambled_word}", True, BLUE)
    screen.blit(scrambled_surface, (WIDTH//2 - 150, 50))

    # Display attempts left
    attempts_surface = small_font.render(f"Attempts left: {attempts}", True, BLACK)
    screen.blit(attempts_surface, (WIDTH//2 - 50, 100))

    # Display hint if available
    if hint:
        hint_surface = small_font.render(f"Hint: {hint}", True, RED)
        screen.blit(hint_surface, (WIDTH//2 - 100, 150))

    # Display user input
    input_surface = font.render(input_text, True, BLACK)
    pygame.draw.rect(screen, BLACK, (WIDTH//2 - 100, 200, 200, 40), 2)  # Input box
    screen.blit(input_surface, (WIDTH//2 - 90, 210))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Check the user's guess
                if input_text.lower() == target_word:
                    print("🎉 Congratulations! You solved the puzzle.")
                    running = False
                else:
                    attempts -= 1
                    if attempts > 0:
                        hint = hill_climb_hint(scrambled_word)  # Generate hint
                    else:
                        print(f"😢 Game Over! The correct word was: {target_word}")
                        running = False
                input_text = ""  # Reset input

            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]  # Remove last character
            else:
                input_text += event.unicode  # Add typed character

pygame.quit()
