#pygame
import pygame
import heapq
import random
import sys
import os
from typing import Dict, List, Tuple, Set

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CRYSTAL_BLUE = (100, 149, 237)
SHADOW_PURPLE = (72, 61, 139)
ORANGE = (255, 165, 0)
TEAL = (0, 128, 128)

# Font settings
FONT_SM = 24
FONT_MD = 32
FONT_LG = 48

class LUMOS:
    """LUMOS - Labyrinth Unity Master Operating System"""
    def __init__(self):
        self.personality_traits = ["wise", "helpful", "playful"]
        self.greetings = ["Welcome, seeker! I am LUMOS.", "Greetings! Let me illuminate your path."]
        self.encouragements = ["You're doing well!", "Every challenge makes you stronger!"]
        self.hints = {
            "Ancient Entrance": {"general": "Ancient secrets hide in plain sight...",
                               "puzzle": "The answer lies in what you use every day.",
                               "combat": "Stone can be worn down with persistence."},
            "Crystal Caverns": {"general": "Listen to the crystals' song...",
                              "puzzle": "Patterns repeat in nature.",
                              "combat": "Crystals amplify energy."},
            "Shadow Maze": {"general": "Not all shadows are feared...",
                          "puzzle": "Consider natural opposites.",
                          "combat": "Light and shadow dance."},
            "Elemental Chambers": {"general": "Elements seek balance...",
                                 "puzzle": "Life gives and takes equally.",
                                 "combat": "Each element has its counter."},
            "Time-Lost Library": {"general": "Time flows differently here...",
                                "puzzle": "Some things constantly move.",
                                "combat": "Time can be manipulated."}
        }

    def greet(self): return random.choice(self.greetings)
    def encourage(self): return random.choice(self.encouragements)
    def give_hint(self, location, context=None):
        if context and location in self.hints:
            return self.hints[location].get(context, self.hints[location]["general"])
        return "Trust your instincts..."

class RandomEncounter:
    """Handles random encounters"""
    def __init__(self):
        self.encounters = {
            "Crystal Guardian": {
                "description": "A crystalline figure materializes!",
                "options": [
                    ("Use sonic resonance", "The crystal shatters harmlessly!", 20),
                    ("Physical attack", "Your attack bounces off!", -10),
                    ("Use water", "The crystal grows stronger!", -15),
                    ("Dodge and observe", "You learn its pattern.", 5)
                ]
            },
            "Shadow Wisp": {
                "description": "A dark form circles you...",
                "options": [
                    ("Use light source", "The shadow dissipates!", 25),
                    ("Use wind", "The wisp scatters briefly...", 10),
                    ("Physical attack", "Your attack passes through!", -10),
                    ("Stand still", "The wisp loses interest.", 5)
                ]
            },
            "Time Anomaly": {
                "description": "Reality warps around you!",
                "options": [
                    ("Use time crystal", "You stabilize the anomaly!", 30),
                    ("Run away", "Time catches up to you!", -15),
                    ("Stand ground", "You resist the temporal pull.", 10),
                    ("Use any item", "The item gets lost in time.", -5)
                ]
            }
        }

    def get_random_encounter(self): return random.choice(list(self.encounters.items()))[1]

class Node:
    def __init__(self, name, description, neighbors, puzzle=None, items=None, boss=None, required_items=None, position=(0, 0)):
        self.name = name
        self.description = description
        self.neighbors = neighbors
        self.puzzle = puzzle or {}
        self.items = items or []
        self.boss = boss or {}
        self.required_items = required_items or []
        self.visited = False
        self.locked = bool(required_items)
        self.puzzle_attempts = 0
        self.stuck_count = 0
        self.position = position  # (x, y) position for map drawing
        self.color = self.get_color_for_node()

    def get_color_for_node(self):
        if "Ancient" in self.name:
            return ORANGE
        elif "Crystal" in self.name:
            return CRYSTAL_BLUE
        elif "Shadow" in self.name:
            return SHADOW_PURPLE
        elif "Elemental" in self.name:
            return GREEN
        elif "Time" in self.name:
            return PURPLE
        return BLUE

class HintNode:
    def __init__(self, state, parent=None, action=None, path_cost=0, heuristic=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.heuristic = heuristic

    def __lt__(self, other):
        return (self.path_cost + self.heuristic) < (other.path_cost + other.heuristic)

    def path(self):
        """Reconstruct the path from this node to the root."""
        path = []
        current = self
        while current:
            path.append(current.action)
            current = current.parent
        return list(reversed(path))[1:]  # Exclude the initial None action

class Button:
    def __init__(self, text, x, y, width, height, color=LIGHT_GRAY, hover_color=GRAY, text_color=BLACK, font_size=FONT_SM):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=5)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class LabyrinthGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("LUMOS Labyrinth Game")
        self.clock = pygame.time.Clock()
        self.fonts = {
            'small': pygame.font.Font(None, FONT_SM),
            'medium': pygame.font.Font(None, FONT_MD),
            'large': pygame.font.Font(None, FONT_LG)
        }

        # Game state
        self.levels = {1: "Ancient Entrance", 2: "Crystal Caverns", 3: "Shadow Maze",
                      4: "Elemental Chambers", 5: "Time-Lost Library"}
        self.current_level = 1
        self.current_location = self.levels[1]
        self.inventory = []
        self.health = 100
        self.score = 0
        self.labyrinth = self._create_labyrinth()
        self.hint_history = []
        self.lumos = LUMOS()
        self.encounter_generator = RandomEncounter()
        self.last_encounter_location = None
        self.total_puzzles = sum(1 for node in self.labyrinth.values() if node.puzzle)
        self.solved_puzzles = 0
        self.player_turns = 0
        self.location_visits = {}
        self.hint_effectiveness = {}

        # Game screens
        self.current_screen = "main_menu"  # main_menu, game, puzzle, boss, encounter, game_over, win
        self.current_message = ""
        self.message_queue = []
        self.lumos_message = self.lumos.greet()
        self.encounter_result = ""

        # Buttons
        self.buttons = {}
        self._init_main_menu_buttons()

        # Current encounter/puzzle/boss data
        self.current_encounter = None
        self.selected_puzzle_option = None
        self.boss_battle_state = {"player_health": 0, "boss_health": 0}

    def _create_labyrinth(self) -> Dict[str, Node]:
        # Create labyrinth with position data for map visualization
        return {
            "Ancient Entrance": Node(
                "Ancient Entrance", "(Level 1: Starting point)",
                [("Crystal Caverns", 2)],
                puzzle={"type": "riddle", "question": "What has keys but no locks, space but no room?",
                       "options": ["A Keyboard", "A Map", "A Phone", "A Book"],
                       "correct_option": 0, "hint": "Think about computer peripherals",
                       "solved": False, "complexity": 1},
                items=["Bronze Key"],
                position=(150, 350)
            ),
            "Crystal Caverns": Node(
                "Crystal Caverns", "(Level 2: Glittering crystals)",
                [("Shadow Maze", 3), ("Ancient Entrance", 1)],
                puzzle={"type": "pattern", "question": "What comes next: Triangle, Square, Pentagon, ?",
                       "options": ["Circle", "Hexagon", "Octagon", "Triangle"],
                       "correct_option": 1, "hint": "Count the sides",
                       "solved": False, "complexity": 2},
                items=["Crystal Shard"],
                position=(300, 200)
            ),
            "Shadow Maze": Node(
                "Shadow Maze", "(Level 3: Shifting shadows)",
                [("Elemental Chambers", 4), ("Crystal Caverns", 2)],
                puzzle={"type": "riddle", "question": "I grow without life, need air but no lungs, water kills me. What am I?",
                       "options": ["Tree", "Fire", "Shadow", "Echo"],
                       "correct_option": 1, "hint": "I bring warmth",
                       "solved": False, "complexity": 3},
                items=["Shadow Essence"],
                required_items=["Bronze Key"],
                position=(500, 350)
            ),
            "Elemental Chambers": Node(
                "Elemental Chambers", "(Level 4: Four elements)",
                [("Time-Lost Library", 5), ("Shadow Maze", 3)],
                puzzle={"type": "elements", "question": "When elements balance, what's at center?",
                       "options": ["Spirit", "Void", "Life", "Harmony"],
                       "correct_option": 2, "hint": "What does balance create?",
                       "solved": False, "complexity": 4},
                items=["Elemental Key"],
                required_items=["Crystal Shard", "Shadow Essence"],
                position=(650, 200)
            ),
            "Time-Lost Library": Node(
                "Time-Lost Library", "(Level 5: Final chamber)",
                [("Elemental Chambers", 4)],
                boss={"name": "Chronos Guardian", "health": 100,
                     "attacks": ["Time Reversal", "Age Acceleration", "Temporal Freeze"],
                     "weakness": "Elemental Key", "defeated": False},
                required_items=["Elemental Key"],
                position=(800, 350)
            )
        }

    def _init_main_menu_buttons(self):
        self.buttons["main_menu"] = [
            Button("Start Game", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 50, BLUE, CRYSTAL_BLUE, WHITE, FONT_MD),
            Button("Quit", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 70, 200, 50, RED, (200, 0, 0), WHITE, FONT_MD)
        ]

    def _init_game_buttons(self):
        # Clear existing game buttons
        self.buttons["game"] = []

        # Current node and its neighbors
        current = self.labyrinth[self.current_location]
        y_pos = 400

        # Add navigation buttons
        for i, (location, difficulty) in enumerate(current.neighbors):
            btn_text = f"Go to {location}"
            self.buttons["game"].append(
                Button(btn_text, SCREEN_WIDTH//2 - 150, y_pos, 300, 40, BLUE, CRYSTAL_BLUE, WHITE)
            )
            y_pos += 50

        # Add utility buttons
        self.buttons["game"].append(
            Button("View Inventory", SCREEN_WIDTH//2 - 150, y_pos, 300, 40, GREEN, (0, 200, 0), WHITE)
        )
        y_pos += 50

        self.buttons["game"].append(
            Button("Ask LUMOS for advice", SCREEN_WIDTH//2 - 150, y_pos, 300, 40, PURPLE, (100, 0, 100), WHITE)
        )

    def _init_puzzle_buttons(self):
        self.buttons["puzzle"] = []

        node = self.labyrinth[self.current_location]
        puzzle = node.puzzle

        y_pos = 350
        for i, option in enumerate(puzzle['options']):
            self.buttons["puzzle"].append(
                Button(option, SCREEN_WIDTH//2 - 150, y_pos, 300, 40, LIGHT_GRAY, WHITE, BLACK)
            )
            y_pos += 50

        # Back button
        self.buttons["puzzle"].append(
            Button("Back", SCREEN_WIDTH//2 - 150, y_pos + 20, 300, 40, RED, (200, 0, 0), WHITE)
        )

    def _init_boss_buttons(self):
        self.buttons["boss"] = []

        node = self.labyrinth[self.current_location]
        boss = node.boss

        y_pos = 400
        self.buttons["boss"].append(
            Button("Attack", SCREEN_WIDTH//2 - 150, y_pos, 300, 40, RED, (200, 0, 0), WHITE)
        )
        y_pos += 50

        self.buttons["boss"].append(
            Button("Defend", SCREEN_WIDTH//2 - 150, y_pos, 300, 40, BLUE, CRYSTAL_BLUE, WHITE)
        )

        # Add weakness button if available
        if boss.get("weakness", "") in self.inventory:
            y_pos += 50
            self.buttons["boss"].append(
                Button(f"Use {boss['weakness']}", SCREEN_WIDTH//2 - 150, y_pos, 300, 40, YELLOW, (200, 200, 0), BLACK)
            )

        y_pos += 50
        self.buttons["boss"].append(
            Button("Run away", SCREEN_WIDTH//2 - 150, y_pos, 300, 40, GRAY, LIGHT_GRAY, BLACK)
        )

    def _init_encounter_buttons(self):
        self.buttons["encounter"] = []

        if not self.current_encounter:
            return

        y_pos = 400
        for i, (action, _, _) in enumerate(self.current_encounter['options']):
            self.buttons["encounter"].append(
                Button(action, SCREEN_WIDTH//2 - 150, y_pos, 300, 40, LIGHT_GRAY, WHITE, BLACK)
            )
            y_pos += 50

    def _init_result_buttons(self):
        self.buttons["result"] = [
            Button("Continue", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50, BLUE, CRYSTAL_BLUE, WHITE)
        ]

    def _init_game_over_buttons(self):
        self.buttons["game_over"] = [
            Button("Main Menu", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 100, 200, 50, BLUE, CRYSTAL_BLUE, WHITE)
        ]

    def _init_win_buttons(self):
        self.buttons["win"] = [
            Button("Main Menu", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 100, 200, 50, BLUE, CRYSTAL_BLUE, WHITE)
        ]

    def _init_inventory_buttons(self):
        self.buttons["inventory"] = [
            Button("Back", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50, BLUE, CRYSTAL_BLUE, WHITE)
        ]

    def handle_random_encounter(self):
        """Handle a random encounter event"""
        if random.random() < 0.3 and self.current_location != self.last_encounter_location:
            self.last_encounter_location = self.current_location
            self.current_encounter = self.encounter_generator.get_random_encounter()
            self.current_screen = "encounter"
            self._init_encounter_buttons()
            return True
        return False

    def determine_hint_difficulty(self):
        progress_percentage = (self.solved_puzzles / self.total_puzzles) * 100 if self.total_puzzles > 0 else 0
        game_stage = 1 + int(progress_percentage / 20)  # 1-5 stages based on progress
        current_node = self.labyrinth[self.current_location]
        stuck_count = current_node.stuck_count

        # Base difficulty adjustments
        if progress_percentage < 30:
            base_difficulty = 1  # Easy
        elif progress_percentage < 70:
            base_difficulty = 2  # Medium
        else:
            base_difficulty = 3  # Hard

        # Stuck count adjustments
        stuck_adjustment = min(2, stuck_count // 3)  # Increase difficulty for every 3 turns stuck

        # Final difficulty level
        final_difficulty = min(3, max(1, base_difficulty + stuck_adjustment))

        # Scale random encounter chance
        encounter_chance = 0.1  # Default chance
        encounter_chance += (game_stage - 1) * 0.05  # Increase with game stage
        encounter_chance = min(0.3, encounter_chance) #cap the chance

        # Scale boss health
        if current_node.boss and not current_node.boss.get("defeated", False):
            boss = current_node.boss
            base_health = boss.get("health", 100)
            scaled_health = base_health + (game_stage - 1) * 20 # Increase with game stage
            boss["health"] = int(scaled_health) #update the health

        # Return difficulty string
        if final_difficulty == 1:
            return "Easy"
        elif final_difficulty == 2:
            return "Medium"
        else:
            return "Hard"
        
    def adjust_dynamic_difficulty(self):

        progress_percentage = (self.solved_puzzles / self.total_puzzles) * 100 if self.total_puzzles > 0 else 0
        game_stage = 1 + int(progress_percentage / 20)  # 1-5 stages based on progress
        current_node = self.labyrinth[self.current_location]

        # Adjust encounter chance
        encounter_chance = 0.1  # Base chance
        encounter_chance += (game_stage - 1) * 0.05  # Increase with game stage
        self.encounter_chance = min(0.3, encounter_chance) #cap the chance

        # Adjust boss difficulty
        if current_node.boss and not current_node.boss.get("defeated", False):
            boss = current_node.boss
            base_health = boss.get("health", 100)
            scaled_health = base_health + (game_stage - 1) * 20
            boss["health"] = int(scaled_health)

            # Scale boss attack and damage
            self.boss_attack_multiplier = 1 + (game_stage - 1) * 0.2
            self.boss_damage_multiplier = 1 + (game_stage - 1) * 0.15

        # Adjust puzzle complexity (example)
        if current_node.puzzle and not current_node.puzzle.get("solved", False):
            complexity = current_node.puzzle.get("complexity", 1)
            scaled_complexity = complexity + (game_stage - 1) * 0.5 #increase complexity with game stage
            current_node.puzzle["complexity"] = min(5, scaled_complexity) #cap complexity

        # Adjust heuristic weights (example)
        self.puzzle_weight = 5 + (game_stage - 1) * 1 #increase puzzle weight
        self.urgency_weight = 15 + (game_stage - 1) * 2 #increase urgency weight    
    
    def update_hint_effectiveness(self, hint, was_helpful):
    
        if hint not in self.hint_effectiveness:
            self.hint_effectiveness[hint] = []
        
        self.hint_effectiveness[hint].append(was_helpful)
        
        # Adjust stuck count based on hint effectiveness
        current_node = self.labyrinth[self.current_location]
        if was_helpful:
            current_node.stuck_count = max(0, current_node.stuck_count - 1)
        else:
            current_node.stuck_count += 1

    def generate_hints(self, state):
        location = state.get("location", self.current_location)
        inventory = state.get("inventory", self.inventory)
        past_hints = state.get("past_hints", self.hint_history)
        solved_puzzles = state.get("solved_puzzles", self.solved_puzzles)

        node = self.labyrinth[location]
        hints = []

        level_num = 1
        for lvl, loc in self.levels.items():
            if loc == location:
                level_num = lvl
                break

        difficulty = self.determine_hint_difficulty()

        # Puzzle hints
        if node.puzzle and not node.puzzle.get("solved", False):
            if "Ancient Entrance" in location:
                general = "The answer is something common you use daily."
                specific = "Think about things with keys and spaces..."
                very_specific = "It's a device you're likely using right now."

            elif "Crystal Caverns" in location:
                general = "Look for a mathematical pattern in shapes."
                specific = "Count the sides of each shape and see what changes."
                very_specific = "Each shape has one more side than the previous."

            elif "Shadow Maze" in location:
                general = "Think about what grows without being alive."
                specific = "What needs air but has no lungs, and water extinguishes it?"
                very_specific = "It brings light and warmth but can be dangerous."

            elif "Elemental Chambers" in location:
                general = "Consider what elements create when they're in balance."
                specific = "When earth, air, fire, and water come together, what emerges?"
                very_specific = "What emerges from a perfect balance of opposing forces?"

            elif "Time-Lost Library" in location:
                general = "The guardian's weakness is tied to the elements."
                specific = f"Use what you found in the Elemental Chambers."
                very_specific = f"The {node.boss['weakness']} is key to victory."
            else:
                general = f"Focus on the puzzle in {location}."
                specific = node.puzzle.get("hint", "Look at the options.")
                if 'correct_option' in node.puzzle:
                    try:
                        correct_answer = node.puzzle['options'][node.puzzle['correct_option']]
                        very_specific = f"The answer is {correct_answer}."
                    except IndexError:
                        very_specific = "The correct answer is not available."
                else:
                    very_specific = "The correct answer is not available."

            if difficulty == "Easy":
                hints.append((very_specific, 1))
                hints.append((specific, 3))
            elif difficulty == "Medium":
                hints.append((specific, 1))
                hints.append((general, 3))
            else:
                hints.append((general, 1))

        # Required items hints
        if node.locked:
            for item in node.required_items:
                if item not in inventory:
                    for ploc, pnode in self.labyrinth.items():
                        if item in pnode.items:
                            if level_num <= 3:
                                hint = f"You need to find the {item} in the {ploc}."
                            else:
                                hint = f"A key from {ploc} will unlock this path."
                            hints.append((hint, 2))

        # Boss hints
        if node.boss and not node.boss.get("defeated", False):
            if "weakness" in node.boss:
                weakness = node.boss["weakness"]
                if weakness in inventory:
                    if level_num <= 3:
                        hint = f"Use the {weakness} against {node.boss['name']}!"
                    else:
                        hint = f"Your elemental treasure will be effective here."
                    hints.append((hint, 2))
                else:
                    if level_num <= 3:
                        hint = f"{node.boss['name']} has a weakness to something elemental."
                    else:
                        hint = f"Balance the elements to defeat what lies ahead."
                    hints.append((hint, 4))

        # Navigation hints
        for next_loc, diff in node.neighbors:
            if next_loc not in [v["location"] for v in state.get("visited_locations", [])]:
                if level_num <= 2:
                    hint = f"You should explore the {next_loc} next."
                else:
                    hint = f"An unexplored path leads to new discoveries."
                hints.append((hint, 3))

        # Health hints
        if state.get("player_health", self.health) < 30:
            hints.append(("Consider finding a way to restore your health.", 1))
            hints.append(("Some items or locations might offer healing.", 2))

        # Player history analysis (example)
        player_history = state.get("player_history", [])  # Assume we track this
        if player_history.count("skipped_puzzle") > 2:
            hints.append(("Don't avoid challenges. Facing them is key.", 4))

        # Apply redundancy penalties
        final_hints = []
        for hint, cost in hints:
            adjusted_cost = cost

            repetition_count = past_hints.count(hint)
            if repetition_count > 0:
                adjusted_cost += 5 * repetition_count

            final_hints.append((hint, adjusted_cost))

        return final_hints
        
    def analyze_player_history(self, state):

        player_history = state.get("player_history",)  # Get player history from state
        analysis = {}  # Dictionary to store analysis results

        # Example: Count skipped puzzles
        skipped_puzzle_count = player_history.count("skipped_puzzle")
        analysis["skipped_puzzle_count"] = skipped_puzzle_count

        # Example: Count repeated locations
        location_counts = {}
        for action in player_history:
            if action.startswith("moved_to:"):
                location = action.split(":")[1]
                location_counts[location] = location_counts.get(location, 0) + 1
        analysis["location_counts"] = location_counts

        # Example: Count combat actions
        combat_action_count = 0
        for action in player_history:
            if action in ["attack", "defend", "run_away", "use_weakness"]:
                combat_action_count += 1
        analysis["combat_action_count"] = combat_action_count

        # Example: Check if player frequently uses hints
        hint_request_count = player_history.count("asked_for_hint")
        analysis["hint_request_count"] = hint_request_count

        # Example: Check if player has low health encounters.
        low_health_encounters = player_history.count("low_health_encounter")
        analysis["low_health_encounters"] = low_health_encounters

        return analysis
    
    def increment_player_turn(self):
   
        self.player_turns += 1
        
        # Track location visits
        if self.current_location not in self.location_visits:
            self.location_visits[self.current_location] = 0
        self.location_visits[self.current_location] += 1
        
        # Update stuck count if player stays in same location
        if self.player_turns > 3 and self.location_visits.get(self.current_location, 0) > 2:
            current_node = self.labyrinth[self.current_location]
            if not current_node.visited or (current_node.puzzle and not current_node.puzzle.get("solved", False)):
                current_node.stuck_count += 1

    def apply_hint(self, state, hint):
        """Apply a hint to current state"""
        new_state = state.copy()
        new_state["last_hint"] = hint

        if "past_hints" not in new_state:
            new_state["past_hints"] = []
        if hint not in new_state["past_hints"]:
            new_state["past_hints"].append(hint)

        return new_state

    def calculate_heuristic(self, state):
        location = state.get("location", self.current_location)
        inventory = state.get("inventory", self.inventory)
        last_hint = state.get("last_hint", "")
        past_hints = state.get("past_hints", [])
        solved_puzzles = state.get("solved_puzzles", self.solved_puzzles)
        total_puzzles = self.total_puzzles
        player_turns = state.get("player_turns", self.player_turns)
        player_health = state.get("player_health", self.health)

        node = self.labyrinth[location]

        # Weights for heuristic factors (adjustable)
        puzzle_weight = 5
        urgency_weight = 15
        stuck_weight = 2
        time_weight = 1
        inventory_weight = 3
        redundancy_weight = 5
        health_weight = 10

        # Progress factors
        progress_percentage = (solved_puzzles / total_puzzles) * 100 if total_puzzles > 0 else 0
        game_stage = 1 + int(progress_percentage / 20)  # 1-5 stages based on progress

        # Puzzle-specific value - more complex puzzles need better hints
        puzzle_value = 0
        if node.puzzle and not node.puzzle.get("solved", False):
            complexity = node.puzzle.get("complexity", 1)
            attempts = node.puzzle_attempts

            # Scale based on attempts and complexity
            puzzle_value = complexity * puzzle_weight * (1 + attempts * 0.5)

        # Stuck factor - higher priority for locations where player is stuck
        stuck_penalty = node.stuck_count * stuck_weight * game_stage  # Scales with game stage

        # Inventory progress value - having more items means better progress
        inventory_progress = len(inventory) * inventory_weight

        # Redundancy penalty - avoid repeating the same hints
        redundancy_factor = 0
        if last_hint in past_hints[:-1]:
            repetition_count = past_hints.count(last_hint)
            redundancy_factor = redundancy_weight * repetition_count

        # Urgency factor - prioritize hints for immediate obstacles
        urgency = 0
        if node.locked and any(item not in inventory for item in node.required_items):
            urgency += urgency_weight
        if node.boss and not node.boss.get("defeated", False):
            urgency += 2 * urgency_weight * game_stage  # Higher priority in later stages

        # Time factor - prioritize helpful hints as player spends more turns
        time_factor = min(20, player_turns / time_weight)

        # Health factor - prioritize health hints when low
        health_factor = 0
        if player_health < 30:
            health_factor = health_weight * (30 - player_health)

        # Final calculation
        return (
            puzzle_value
            + urgency
            + stuck_penalty
            + time_factor
            + health_factor
        ) - inventory_progress + redundancy_factor

    def a_star_search(self, initial_state, goal_test, heuristic):
        frontier = []
        explored = set()
        max_depth = 50  # Limit search depth
        node_count = 0 # limit node count

        # Initialize with starting node
        initial_node = HintNode(state=initial_state, path_cost=0, heuristic=heuristic(initial_state))
        heapq.heappush(frontier, initial_node)

        while frontier:
            node = heapq.heappop(frontier)
            node_count += 1

            if goal_test(node.state):
                # Reconstruct path
                path = []
                while node.parent:
                    path.append(node.action)
                    node = node.parent
                return list(reversed(path))

            # Add to explored set
            state_hash = str(sorted(node.state.items()))
            if state_hash in explored:
                continue
            explored.add(state_hash)

            # Expand node
            if len(node.path()) >= max_depth or node_count > 1000: # add depth and node count check
                return ["Consider the puzzle carefully..."] #return fallback

            for hint, cost in self.generate_hints(node.state):
                new_state = self.apply_hint(node.state.copy(), hint)
                child = HintNode(
                    state=new_state,
                    parent=node,
                    action=hint,
                    path_cost=node.path_cost + cost,
                    heuristic=heuristic(new_state)
                )
                heapq.heappush(frontier, child)

        return ["Consider the puzzle carefully..."]  # Fallback

    def get_optimal_hint(self):
        """Use A* to find the optimal hint"""
        # Define current state
        current_state = {
            "location": self.current_location,
            "inventory": self.inventory.copy(),
            "past_hints": self.hint_history.copy(),
            "solved_puzzles": self.solved_puzzles,
            "player_turns": self.player_turns,
            "visited_locations": [{"location": loc, "count": count}
                                 for loc, count in self.location_visits.items()]
        }

        # Goal test function (always False for hint-finding)
        def is_goal(state):
            return False

        # Get best hint using A*
        hints = self.a_star_search(
            initial_state=current_state,
            goal_test=is_goal,
            heuristic=self.calculate_heuristic
        )

        if hints:
            best_hint = hints[0]
            self.hint_history.append(best_hint)
            return best_hint
        else:
            return "Trust your intuition..."

    def solve_puzzle(self, option_index):
        """Attempt to solve the current puzzle"""
        node = self.labyrinth[self.current_location]
        puzzle = node.puzzle

        if not puzzle or puzzle.get("solved", False):
            return True

        node.puzzle_attempts += 1

        if option_index == puzzle['correct_option']:
            self.current_message = "✅ Correct!"
            self.score += 50
            puzzle["solved"] = True
            self.solved_puzzles += 1

            # Track hint effectiveness
            if puzzle.get("hint", "") in self.hint_history[-1:]:
                self.hint_effectiveness[self.hint_history[-1]] = True

            return True
        else:
            self.current_message = "❌ Incorrect. Try again."
            self.score -= 10

            # Track hint ineffectiveness
            if puzzle.get("hint", "") in self.hint_history[-1:]:
                self.hint_effectiveness[self.hint_history[-1]] = False

            return False

    def fight_boss(self, action):
        node = self.labyrinth[self.current_location]
        boss = node.boss

        if not boss or boss.get("defeated", False):
            return True

        boss_health = self.boss_battle_state["boss_health"]
        player_health = self.boss_battle_state["player_health"]

        # Check if player has weakness item
        has_weakness = boss.get("weakness", "") in self.inventory

        # Scale boss attack and damage based on game stage
        progress_percentage = (self.solved_puzzles / self.total_puzzles) * 100 if self.total_puzzles > 0 else 0
        game_stage = 1 + int(progress_percentage / 20)  # 1-5 stages based on progress
        boss_attack_multiplier = 1 + (game_stage - 1) * 0.2  # Increase attack with game stage
        boss_damage_multiplier = 1 + (game_stage - 1) * 0.15 # Increase damage with game stage

        # Handle action
        if action == "Attack":
            damage = random.randint(10, 20)
            if has_weakness:
                damage += 5
            boss_health -= damage
            self.message_queue.append(f"You attack for {damage} damage!")

            # Boss attacks back
            boss_attack = random.choice(boss["attacks"])
            player_damage = int(random.randint(15, 25) * boss_damage_multiplier) #damage is now scaled
            player_health -= player_damage
            self.message_queue.append(f"The {boss['name']} uses {boss_attack} for {player_damage} damage!")

        elif action == "Defend":
            # Defend reduces damage
            boss_attack = random.choice(boss["attacks"])
            player_damage = int(random.randint(5, 15) * boss_damage_multiplier) #damage is now scaled
            player_health -= player_damage
            self.message_queue.append(f"You defend!")
            self.message_queue.append(f"The {boss['name']} uses {boss_attack} for {player_damage} damage!")

        elif action == f"Use {boss['weakness']}" and has_weakness:
            # Use weakness
            damage = random.randint(30, 50)
            boss_health -= damage
            self.message_queue.append(f"You use the {boss['weakness']} for {damage} damage!")
            self.message_queue.append(f"The {boss['name']} is weakened!")

        elif action == "Run away":
            # Run attempt
            if random.random() < 0.3:
                self.current_message = "You escaped!"
                self.current_screen = "game"
                self._init_game_buttons()
                return False
            else:
                self.message_queue.append("Couldn't escape!")
                boss_attack = random.choice(boss["attacks"])
                player_damage = int(random.randint(20, 30) * boss_damage_multiplier) #damage is now scaled
                player_health -= player_damage
                self.message_queue.append(f"The {boss['name']} uses {boss_attack} for {player_damage} damage!")

        # Update battle state
        self.boss_battle_state["boss_health"] = boss_health
        self.boss_battle_state["player_health"] = player_health

        # Check battle outcome
        if boss_health <= 0:
            self.current_message = f"🎉 You defeated the {boss['name']}!"
            boss["defeated"] = True
            self.score += 100
            self.health = player_health
            self.current_screen = "result"
            self._init_result_buttons()
            return True
        elif player_health <= 0:
            self.current_message = f"💀 You were defeated by the {boss['name']}!"
            self.health = 0
            self.current_screen = "game_over"
            self._init_game_over_buttons()
            return False

        # Continue battle
        return "continue"

    def handle_encounter_choice(self, choice_index):
        """Handle the player's choice in an encounter"""
        if not self.current_encounter:
            return

        action, result, points = self.current_encounter['options'][choice_index]
        self.encounter_result = result
        self.score += points

        self.current_message = f"{result}\nScore change: {points:+d}"
        self.current_screen = "result"
        self._init_result_buttons()

    def check_node_first_visit(self):
        current = self.labyrinth[self.current_location]

        if not current.visited:
            # Scale random encounter chance based on game stage
            progress_percentage = (self.solved_puzzles / self.total_puzzles) * 100 if self.total_puzzles > 0 else 0
            game_stage = 1 + int(progress_percentage / 20)  # 1-5 stages based on progress
            encounter_chance = 0.1  # Base chance
            encounter_chance += (game_stage - 1) * 0.05  # Increase with game stage
            encounter_chance = min(0.3, encounter_chance) #cap the chance

            # Handle random encounter (will change screen if encounter happens)
            if random.random() < encounter_chance: #use the scaled chance
                if self.handle_random_encounter():
                    return

            # Check for puzzle
            if current.puzzle and not current.puzzle.get("solved", False):
                self.current_screen = "puzzle"
                self._init_puzzle_buttons()
                return

            # Check for boss
            if current.boss and not current.boss.get("defeated", False):
                self.current_screen = "boss"
                self.boss_battle_state = {
                    "boss_health": current.boss.get("health", 100),
                    "player_health": self.health
                }
                self._init_boss_buttons()
                return

            # Collect items
            if current.items:
                items_text = ", ".join(current.items)
                self.current_message = f"Found items: {items_text}"
                for item in current.items:
                    if item not in self.inventory:
                        self.inventory.append(item)
                self.current_screen = "result"
                self._init_result_buttons()

                current.visited = True

        # Update location visit counter
        self.location_visits[self.current_location] = self.location_visits.get(self.current_location, 0) + 1

    def draw_main_menu(self):
        # """Draw the main menu screen"""
       background_image = pygame.image.load("castle.png").convert()  # Replace "main_menu_bg.png" with your image file name
       background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)) #resizes the image to the screen size.
       self.screen.blit(background_image, (0, 0))  

        # Draw title
       title_text = self.fonts['large'].render("LUMOS LABYRINTH", True, CRYSTAL_BLUE)
       title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
       self.screen.blit(title_text, title_rect)

       subtitle_text = self.fonts['medium'].render("A Magical Adventure", True, WHITE)
       subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + 60))
       self.screen.blit(subtitle_text, subtitle_rect)

       # Draw buttons
       for button in self.buttons["main_menu"]:
           button.draw(self.screen)




    def draw_game(self):
          """Draw the main game screen"""
          # Load the background image
          background_image = pygame.image.load("gra.png").convert()  # Replace "game_bg.png" with your image file name
          background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)) #resizes the image to the screen size.
          self.screen.blit(background_image, (0, 0))  # Draw the image at the top-left corner

          # Draw location info
          current = self.labyrinth[self.current_location]

          # Header
          location_text = self.fonts['medium'].render(self.current_location, True, current.color)
          location_rect = location_text.get_rect(center=(SCREEN_WIDTH//2, 50))
          self.screen.blit(location_text, location_rect)

          description_text = self.fonts['small'].render(current.description, True, WHITE)
          description_rect = description_text.get_rect(center=(SCREEN_WIDTH//2, 90))
          self.screen.blit(description_text, description_rect)

          # Status bar
          status_rect = pygame.Rect(20, 20, 200, 100)
          pygame.draw.rect(self.screen, GRAY, status_rect, border_radius=5)
          pygame.draw.rect(self.screen, WHITE, status_rect, 2, border_radius=5)

          health_text = self.fonts['small'].render(f"Health: {self.health}", True, WHITE)
          self.screen.blit(health_text, (30, 30))

          score_text = self.fonts['small'].render(f"Score: {self.score}", True, WHITE)
          self.screen.blit(score_text, (30, 60))

          level_text = self.fonts['small'].render(f"Level: {self.current_level}", True, WHITE)
          self.screen.blit(level_text, (30, 90))

          # LUMOS message and image
          lumos_rect = pygame.Rect(20, 130, SCREEN_WIDTH - 40, 80)
          pygame.draw.rect(self.screen, SHADOW_PURPLE, lumos_rect, border_radius=5)
          pygame.draw.rect(self.screen, CRYSTAL_BLUE, lumos_rect, 2, border_radius=5)

          # Load LUMOS image
          lumos_image = pygame.image.load("mew.gif").convert_alpha()  # Replace lumos_icon.png
          lumos_image = pygame.transform.scale(lumos_image, (64, 64))  # Adjust size as needed

          # Blit LUMOS image
          self.screen.blit(lumos_image, (30, 138))  # Adjust position as needed

          # Blit LUMOS text
          lumos_text = self.fonts['small'].render(f"LUMOS: {self.lumos_message}", True, WHITE)
          lumos_text_rect = lumos_text.get_rect(center=(SCREEN_WIDTH//2 + 32, 170))  # offset the text
          self.screen.blit(lumos_text, lumos_text_rect)

          # Draw mini map
          self.draw_map()

    # Draw buttons
          for button in self.buttons["game"]:
                button.draw(self.screen)


    def draw_map(self):
        """Draw a simple mini-map of the labyrinth using images"""
        map_rect = pygame.Rect(SCREEN_WIDTH - 220, 20, 200, 200)
        pygame.draw.rect(self.screen, GRAY, map_rect, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, map_rect, 2, border_radius=5)

        map_text = self.fonts['small'].render("Map", True, WHITE)
        self.screen.blit(map_text, (SCREEN_WIDTH - 200, 30))

        # Scale factor for the map
        scale_x = 180 / 1000
        scale_y = 160 / 700
        offset_x = SCREEN_WIDTH - 210
        offset_y = 50

        # Draw connections between nodes
        for node_name, node in self.labyrinth.items():
            node_x = offset_x + node.position[0] * scale_x
            node_y = offset_y + node.position[1] * scale_y

            for neighbor, _ in node.neighbors:
                if neighbor in self.labyrinth:
                    neighbor_node = self.labyrinth[neighbor]
                    neighbor_x = offset_x + neighbor_node.position[0] * scale_x
                    neighbor_y = offset_y + neighbor_node.position[1] * scale_y

                    line_color = LIGHT_GRAY
                    if node.visited and neighbor_node.visited:
                        line_color = WHITE

                    pygame.draw.line(
                        self.screen, line_color,
                        (node_x, node_y),
                        (neighbor_x, neighbor_y),
                        2 if node.visited and neighbor_node.visited else 1
                    )

        # Draw nodes with images
        for node_name, node in self.labyrinth.items():
            node_x = offset_x + node.position[0] * scale_x
            node_y = offset_y + node.position[1] * scale_y

            # Load node image
            if node.visited:
                node_image = pygame.image.load(f"{node_name.lower().replace(' ', '_')}_nodeg.jpg").convert_alpha() #example file naming
                node_image = pygame.transform.scale(node_image, (20, 20))  # Adjust size as needed
            else:
                node_image = pygame.image.load("nodeg.jpg").convert_alpha() #unvisited node image
                node_image = pygame.transform.scale(node_image, (20, 20))

            # Blit node image
            node_rect = node_image.get_rect(center=(node_x, node_y))
            self.screen.blit(node_image, node_rect)

            # Highlight current location
            if node_name == self.current_location:
                pygame.draw.circle(self.screen, WHITE, (node_x, node_y), 13, 2) #draws a circle around the node.

    def draw_puzzle(self):
        """Draw the puzzle screen"""
  
        # Load the background image
        background_image = pygame.image.load("gra.png").convert()  # Replace "puzzle_bg.png" with your image file name
        background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)) #resizes the image to the screen size.
        self.screen.blit(background_image, (0, 0))  # Draw the image at the top-left corner

        node = self.labyrinth[self.current_location]
        puzzle = node.puzzle

        # Header
        title_text = self.fonts['medium'].render(f"Puzzle: {node.name}", True, node.color)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title_text, title_rect)

        # Question
        question_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, 100, 600, 100)
        pygame.draw.rect(self.screen, GRAY, question_rect, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, question_rect, 2, border_radius=5)

        question_text = self.fonts['medium'].render(puzzle['question'], True, WHITE)
        question_rect = question_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(question_text, question_rect)

        # Instructions
        inst_text = self.fonts['small'].render("Select the correct answer:", True, LIGHT_GRAY)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, 230))
        self.screen.blit(inst_text, inst_rect)

        # Draw current message
        if self.current_message:
            message_text = self.fonts['small'].render(self.current_message, True,
                                                    GREEN if "Correct" in self.current_message else RED)
            message_rect = message_text.get_rect(center=(SCREEN_WIDTH//2, 280))
            self.screen.blit(message_text, message_rect)

        # Draw buttons
        for button in self.buttons["puzzle"]:
            button.draw(self.screen)

    def draw_boss(self):
    # """Draw the boss battle screen"""
     # Load the background image
        background_image = pygame.image.load("golem.gif").convert()  # Replace "boss_bg.png" with your image file name
        background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)) #resizes the image to the screen size.
        self.screen.blit(background_image, (0, 0))  # Draw the image at the top-left corner


        node = self.labyrinth[self.current_location]
        boss = node.boss

        # Header
        title_text = self.fonts['medium'].render(f"BOSS: {boss['name']}", True, RED)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title_text, title_rect)

        # Description
        desc_text = self.fonts['small'].render(f"The guardian of the {node.name}", True, WHITE)
        desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH//2, 90))
        self.screen.blit(desc_text, desc_rect)

        # Health bars
        player_health = self.boss_battle_state["player_health"]
        boss_health = self.boss_battle_state["boss_health"]

        # Player health
        health_rect = pygame.Rect(50, 150, 300, 30)
        health_fill = pygame.Rect(50, 150, 300 * (player_health / 100), 30)
        pygame.draw.rect(self.screen, GRAY, health_rect)
        pygame.draw.rect(self.screen, GREEN, health_fill)
        pygame.draw.rect(self.screen, WHITE, health_rect, 2)

        player_text = self.fonts['small'].render(f"You: {player_health}/100", True, WHITE)
        self.screen.blit(player_text, (50, 120))

        # Boss health
        health_rect = pygame.Rect(50, 230, 300, 30)
        health_fill = pygame.Rect(50, 230, 300 * (boss_health / 100), 30)
        pygame.draw.rect(self.screen, GRAY, health_rect)
        pygame.draw.rect(self.screen, RED, health_fill)
        pygame.draw.rect(self.screen, WHITE, health_rect, 2)

        boss_text = self.fonts['small'].render(f"{boss['name']}: {boss_health}/100", True, WHITE)
        self.screen.blit(boss_text, (50, 200))

        # Draw message queue
        y_pos = 280
        for message in self.message_queue[-3:]:
            message_text = self.fonts['small'].render(message, True, WHITE)
            self.screen.blit(message_text, (50, y_pos))
            y_pos += 30

        # Draw buttons
        for button in self.buttons["boss"]:
            button.draw(self.screen)

    def draw_encounter(self):
        # Step 1: Fill the screen with a background color (or load a background image)
        self.screen.fill((0, 0, 0))  # Black background (change color if needed)

        # Alternatively, load a background image
        bg_image = pygame.image.load("fbackground.jpg").convert()  # Replace with your background image
        bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(bg_image, (0, 0))  # Draw it covering the whole screen

        # Step 2: Load the encounter image
        encounter_image = pygame.image.load("encounter1.gif").convert()
        encounter_image = pygame.transform.scale(encounter_image, (500,500))  # Resize if needed

        # Step 3: Get screen size and calculate center position
        screen_width, screen_height = self.screen.get_size()
        image_width, image_height = encounter_image.get_size()
        x = (screen_width - image_width) // 2
        y = (screen_height - image_height) // 2

        # Step 4: Draw the encounter image at the center of the screen
        self.screen.blit(encounter_image, (x, y))

        # Step 5: Draw the text elements
        title_text = self.fonts['medium'].render("Random Encounter!", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title_text, title_rect)

        desc_text = self.fonts['small'].render(self.current_encounter['description'], True, WHITE)
        desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH//2, 120))
        self.screen.blit(desc_text, desc_rect)

        inst_text = self.fonts['small'].render("Choose your action:", True, LIGHT_GRAY)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, 180))
        self.screen.blit(inst_text, inst_rect)

        hint = self.lumos.give_hint(self.current_location, "combat")
        hint_text = self.fonts['small'].render(f"LUMOS: {hint}", True, CRYSTAL_BLUE)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH//2, 230))
        self.screen.blit(hint_text, hint_rect)

        # Step 6: Draw buttons
        for button in self.buttons["encounter"]:
            button.draw(self.screen)



    def draw_result(self):
        # Load the background image
        background_image = pygame.image.load("castle.png").convert()  # Replace "result_bg.png" with your image file name
        background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))  # resizes the image to the screen size.
        self.screen.blit(background_image, (0, 0))  # Draw the image at the top-left corner

        # Message
        message_lines = self.current_message.split("\n")
        y_pos = SCREEN_HEIGHT // 3

        for line in message_lines:
            line_text = self.fonts['medium'].render(line, True, WHITE)
            line_rect = line_text.get_rect(center=(SCREEN_WIDTH//2, y_pos))
            self.screen.blit(line_text, line_rect)
            y_pos += 50

        # Draw buttons
        for button in self.buttons["result"]:
            button.draw(self.screen)
            
    def draw_inventory(self):
        # Load the background image
        background_image = pygame.image.load("inventory.jpg").convert()  # Replace "inventory_bg.png" with your image file name
        background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))  # resizes the image to the screen size.
        self.screen.blit(background_image, (0, 0))  # Draw the image at the top-left corner

        # Header
        title_text = self.fonts['medium'].render("Inventory", True, GREEN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title_text, title_rect)

        # Draw items
        if not self.inventory:
            empty_text = self.fonts['small'].render("Your inventory is empty", True, LIGHT_GRAY)
            empty_rect = empty_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
            self.screen.blit(empty_text, empty_rect)
        else:
            y_pos = 150
            for item in self.inventory:
                # Item box
                item_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, y_pos, 300, 60)
                pygame.draw.rect(self.screen, GRAY, item_rect, border_radius=5)
                pygame.draw.rect(self.screen, WHITE, item_rect, 2, border_radius=5)

                # Item text
                item_text = self.fonts['medium'].render(item, True, WHITE)
                item_text_rect = item_text.get_rect(center=(SCREEN_WIDTH//2, y_pos + 30))
                self.screen.blit(item_text, item_text_rect)

                y_pos += 80

        # Draw buttons
        for button in self.buttons["inventory"]:
            button.draw(self.screen)

    def draw_game_over(self):
    # """Draw the game over screen"""
    # Load the background image
        background_image = pygame.image.load("gameover.gif").convert()  # Replace "game_over_bg.png" with your image file name
        background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)) #resizes the image to the screen size.
        self.screen.blit(background_image, (0, 0))  # Draw the image at the top-left corner


        # Game Over text
        gameover_text = self.fonts['large'].render("GAME OVER", True, RED)
        gameover_rect = gameover_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        self.screen.blit(gameover_text, gameover_rect)

            # Score
        score_text = self.fonts['medium'].render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(score_text, score_rect)

            # Draw buttons
        for button in self.buttons["game_over"]:
                button.draw(self.screen)

    def draw_win(self):
    # """Draw the win screen"""
    # Load the background image
        background_image = pygame.image.load("win.gif").convert()  # Replace "win_bg.png" with your image file name
        background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)) #resizes the image to the screen size.
        self.screen.blit(background_image, (0, 0))  # Draw the image at the top-left corner

        # Win text
        win_text = self.fonts['large'].render("YOU ESCAPED THE LABYRINTH!", True, CRYSTAL_BLUE)
        win_rect = win_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        self.screen.blit(win_text, win_rect)

            # Score
        score_text = self.fonts['medium'].render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(score_text, score_rect)

            # Draw buttons
        for button in self.buttons["win"]:
                button.draw(self.screen)

    def navigate_to(self, destination):
        """Navigate to a new location"""
        if destination not in self.labyrinth:
            return False

        # Check if destination is locked
        node = self.labyrinth[destination]
        if node.locked:
            has_all_items = all(item in self.inventory for item in node.required_items)
            if not has_all_items:
                required = ", ".join(node.required_items)
                self.current_message = f"You need: {required} to enter."
                self.current_screen = "result"
                self._init_result_buttons()
                self.lumos_message = f"Find the required items: {required}"
                return False

        # Move to new location
        self.current_location = destination
        self.current_level = list(self.levels.keys())[list(self.levels.values()).index(destination)]
        self._init_game_buttons()

        # Check if this is a win condition
        if self.current_location == "Time-Lost Library" and self.labyrinth["Time-Lost Library"].boss.get("defeated", False):
            self.current_screen = "win"
            self._init_win_buttons()
            self.score += 200  # Bonus for completing the game
            return True

        # Check if we should handle a first visit
        self.check_node_first_visit()

        # Update LUMOS message
        self.lumos_message = self.lumos.give_hint(self.current_location, "general")

        return True

    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.QUIT:
            return False

        # Get mouse position
        pos = pygame.mouse.get_pos()

        # Handle different screens
        if self.current_screen == "main_menu":
            for i, button in enumerate(self.buttons["main_menu"]):
                button.check_hover(pos)
                if button.is_clicked(pos, event):
                    if i == 0:  # Start Game
                        self.current_screen = "game"
                        self._init_game_buttons()
                        self.check_node_first_visit()
                    elif i == 1:  # Quit
                        return False

        elif self.current_screen == "game":
            for i, button in enumerate(self.buttons["game"]):
                button.check_hover(pos)
                if button.is_clicked(pos, event):
                    if i < len(self.labyrinth[self.current_location].neighbors):
                        # Navigation buttons
                        dest, _ = self.labyrinth[self.current_location].neighbors[i]
                        self.navigate_to(dest)
                    elif i == len(self.labyrinth[self.current_location].neighbors):
                        # View Inventory
                        self.current_screen = "inventory"
                        self._init_inventory_buttons()
                    elif i == len(self.labyrinth[self.current_location].neighbors) + 1:
                        # Ask LUMOS
                        self.lumos_message = self.get_optimal_hint()
                        self.player_turns += 1

        elif self.current_screen == "puzzle":
            for i, button in enumerate(self.buttons["puzzle"]):
                button.check_hover(pos)
                if button.is_clicked(pos, event):
                    if i < len(self.labyrinth[self.current_location].puzzle['options']):
                        # Puzzle option selected
                        self.selected_puzzle_option = i
                        result = self.solve_puzzle(i)
                        if result:  # Puzzle solved
                            self.current_screen = "result"
                            self._init_result_buttons()
                    elif i == len(self.labyrinth[self.current_location].puzzle['options']):
                        # Back button
                        self.current_screen = "game"
                        self._init_game_buttons()

        elif self.current_screen == "boss":
            for i, button in enumerate(self.buttons["boss"]):
                button.check_hover(pos)
                if button.is_clicked(pos, event):
                    result = self.fight_boss(button.text)
                    if result == True:  # Boss defeated
                        pass  # Logic already handled in fight_boss
                    elif result == False:  # Player defeated or ran away
                        pass  # Logic already handled in fight_boss
                    # If "continue", battle continues

        elif self.current_screen == "encounter":
            for i, button in enumerate(self.buttons["encounter"]):
                button.check_hover(pos)
                if button.is_clicked(pos, event):
                    self.handle_encounter_choice(i)

        elif self.current_screen == "result":
            for button in self.buttons["result"]:
                button.check_hover(pos)
                if button.is_clicked(pos, event):
                    self.current_screen = "game"
                    self.message_queue = []
                    self._init_game_buttons()

        elif self.current_screen == "inventory":
            for button in self.buttons["inventory"]:
                button.check_hover(pos)
                if button.is_clicked(pos, event):
                    self.current_screen = "game"
                    self._init_game_buttons()

        elif self.current_screen == "game_over" or self.current_screen == "win":
            for button in self.buttons["game_over" if self.current_screen == "game_over" else "win"]:
                button.check_hover(pos)
                if button.is_clicked(pos, event):
                    # Reset game to main menu
                    self.__init__()

        return True

    def run(self):
        """Main game loop"""
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                running = self.handle_event(event)
                if not running:
                    break

            # Draw current screen
            if self.current_screen == "main_menu":
                self.draw_main_menu()
            elif self.current_screen == "game":
                self.draw_game()
            elif self.current_screen == "puzzle":
                self.draw_puzzle()
            elif self.current_screen == "boss":
                self.draw_boss()
            elif self.current_screen == "encounter":
                self.draw_encounter()
            elif self.current_screen == "result":
                self.draw_result()
            elif self.current_screen == "inventory":
                self.draw_inventory()
            elif self.current_screen == "game_over":
                self.draw_game_over()
            elif self.current_screen == "win":
                self.draw_win()

            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = LabyrinthGame()
    game.run()