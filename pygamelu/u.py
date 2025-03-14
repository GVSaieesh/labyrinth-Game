import pygame
import sys
import heapq
import random
from typing import Dict, List, Tuple, Set, Optional

# Initialize pygame
pygame.init()
pygame.font.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)
DARK_BLUE = (0, 0, 128)
BROWN = (165, 42, 42)

class LUMOS:
    """LUMOS - Labyrinth Unity Master Operating System with cost-based hint system"""
    def __init__(self):
        self.greetings = ["Greetings, brave adventurer! I am LUMOS, your magical guide."]
        self.encouragements = ["Your progress is remarkable!", "You're on the right path!",
                             "Trust in your abilities!", "The way forward becomes clearer!"]
        # Hint levels with costs
        self.hint_costs = {
            "vague": 1,     # Very cryptic hint
            "moderate": 3,  # Somewhat helpful hint
            "specific": 5,  # Very direct hint
            "explicit": 10  # Almost gives the answer away
        }

    def greet(self) -> str:
        return self.greetings[0]

    def encourage(self) -> str:
        return random.choice(self.encouragements)

    def give_hint(self, location: str, context: str = None, hint_level: str = "vague") -> Tuple[str, int]:
        """Returns a hint based on location, context, and hint level with its cost."""
        # Enhanced hint database with multiple detail levels
        hints = {
            "Ancient Entrance": {
                "general": {
                    "vague": "Ancient wisdom lies dormant in these halls...",
                    "moderate": "The symbols here hold ancient wisdom...",
                    "specific": "Look carefully at the arrangement of the symbols.",
                    "explicit": "Match the symbols in order of size, smallest to largest."
                },
                "puzzle": {
                    "vague": "Patterns reveal themselves to the patient observer...",
                    "moderate": "Symbols can have multiple meanings.",
                    "specific": "The order matters as much as the symbols themselves.",
                    "explicit": "Arrange the stone tiles to match the ceiling pattern."
                }
            },
            "Crystal Caverns": {
                "general": {
                    "vague": "Light and crystal dance together in harmony...",
                    "moderate": "The crystals react to your presence in subtle ways.",
                    "specific": "Your light source affects how the crystals behave.",
                    "explicit": "Use the torch to activate the central crystal formation."
                },
                "puzzle": {
                    "vague": "Reflections hold more than meets the eye...",
                    "moderate": "The angle of light reveals hidden truths.",
                    "specific": "Direct your torch at the largest crystal to reveal a path.",
                    "explicit": "Shine your torch at the northwest crystal to open the secret passage."
                }
            },
            "Shadow Corridor": {
                "general": {
                    "vague": "Darkness hides both danger and opportunity...",
                    "moderate": "The shadows move in peculiar ways here.",
                    "specific": "Some shadows are more solid than they appear.",
                    "explicit": "Avoid the moving shadows, they will drain your health."
                },
                "puzzle": {
                    "vague": "Light creates shadow, but shadow can also create light...",
                    "moderate": "The pattern of shadows tells a story.",
                    "specific": "Project shadows onto the wall markings to reveal the code.",
                    "explicit": "Use your torch to cast specific shadow shapes on the three wall symbols."
                }
            }
        }

        # Default hints if location or context not found
        default_hints = {
            "vague": "Trust your instincts, brave one...",
            "moderate": "The path forward is not always clear, but it exists.",
            "specific": "Your current situation demands careful observation.",
            "explicit": "Look for the unusual pattern - that's your next step."
        }

        # Use default hint level if invalid level provided
        if hint_level not in self.hint_costs:
            hint_level = "vague"

        # Get the appropriate hint
        if location in hints and context in hints[location]:
            hint = hints[location][context].get(hint_level, hints[location][context]["vague"])
        else:
            hint = default_hints.get(hint_level, default_hints["vague"])

        return hint, self.hint_costs[hint_level]

class Node:
    def __init__(self, name: str, description: str, neighbors: List[Tuple[str, int]],
                 items: List[str] = None, required_items: List[str] = None,
                 hazards: Dict[str, int] = None, puzzles: Dict[str, int] = None,
                 position: Tuple[int, int] = (0, 0)):
        self.name = name
        self.description = description
        self.neighbors = neighbors
        self.items = items or []
        self.required_items = required_items or []
        self.visited = False
        self.locked = True if required_items else False
        self.hazards = hazards or {}  # Dict of hazard_name: damage_value
        self.puzzles = puzzles or {}  # Dict of puzzle_name: reward_value
        self.puzzle_solved = set()    # Track which puzzles have been solved
        self.position = position      # For map rendering (x, y) coordinates

class PathNode:
    """Node class for UCS pathfinding"""
    def __init__(self, state: str, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost

    def __lt__(self, other):
        return self.path_cost < other.path_cost

class Button:
    def __init__(self, x, y, width, height, text, color=LIGHT_BLUE, hover_color=BLUE, text_color=BLACK, font_size=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.SysFont(None, font_size)
        self.is_hovered = False
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # Border
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class MessageBox:
    def __init__(self, x, y, width, height, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.SysFont(None, font_size)
        self.messages = []
        self.max_messages = 12  # Maximum number of messages to display
        self.scroll_position = 0
        
    def add_message(self, message, color=WHITE):
        # Word wrap long messages
        words = message.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if self.font.size(test_line)[0] < self.rect.width - 20:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        for line in lines:
            self.messages.append((line, color))
        
        # Auto-scroll to bottom when new messages are added
        if len(self.messages) > self.max_messages:
            self.scroll_position = len(self.messages) - self.max_messages
            
    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Display messages with scroll
        display_messages = self.messages[self.scroll_position:self.scroll_position + self.max_messages]
        
        y_offset = 10
        for message, color in display_messages:
            text_surface = self.font.render(message, True, color)
            screen.blit(text_surface, (self.rect.x + 10, self.rect.y + y_offset))
            y_offset += self.font.get_height() + 5
            
        # Draw scroll indicators if needed
        if self.scroll_position > 0:
            pygame.draw.polygon(screen, WHITE, [
                (self.rect.x + self.rect.width - 20, self.rect.y + 15),
                (self.rect.x + self.rect.width - 10, self.rect.y + 15),
                (self.rect.x + self.rect.width - 15, self.rect.y + 5)
            ])
            
        if self.scroll_position + self.max_messages < len(self.messages):
            pygame.draw.polygon(screen, WHITE, [
                (self.rect.x + self.rect.width - 20, self.rect.y + self.rect.height - 15),
                (self.rect.x + self.rect.width - 10, self.rect.y + self.rect.height - 15),
                (self.rect.x + self.rect.width - 15, self.rect.y + self.rect.height - 5)
            ])
            
    def handle_scroll(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_position = max(0, self.scroll_position - 1)
            elif event.button == 5:  # Scroll down
                self.scroll_position = min(len(self.messages) - self.max_messages, self.scroll_position + 1)
                if self.scroll_position < 0:
                    self.scroll_position = 0

class MiniMap:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.node_radius = 15
        self.current_location = None
        self.labyrinth = None
        
    def set_data(self, labyrinth, current_location):
        self.labyrinth = labyrinth
        self.current_location = current_location
        
    def draw(self, screen, discovered_locations):
        if not self.labyrinth:
            return
            
        pygame.draw.rect(screen, BLACK, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Draw connections first
        for location_name, node in self.labyrinth.items():
            if location_name in discovered_locations:
                for neighbor_name, _ in node.neighbors:
                    if neighbor_name in discovered_locations:
                        neighbor = self.labyrinth[neighbor_name]
                        # Calculate scaled positions
                        x1 = self.rect.x + ((node.position[0] / 100) * self.rect.width)
                        y1 = self.rect.y + ((node.position[1] / 100) * self.rect.height)
                        x2 = self.rect.x + ((neighbor.position[0] / 100) * self.rect.width)
                        y2 = self.rect.y + ((neighbor.position[1] / 100) * self.rect.height)
                        
                        pygame.draw.line(screen, GRAY, (x1, y1), (x2, y2), 2)
        
        # Draw nodes
        font = pygame.font.SysFont(None, 20)
        for location_name, node in self.labyrinth.items():
            if location_name in discovered_locations:
                # Calculate scaled position
                x = self.rect.x + ((node.position[0] / 100) * self.rect.width)
                y = self.rect.y + ((node.position[1] / 100) * self.rect.height)
                
                # Different colors for different location types
                color = LIGHT_BLUE
                if "Crystal" in location_name:
                    color = LIGHT_BLUE
                elif "Shadow" in location_name:
                    color = PURPLE
                elif "Ancient" in location_name:
                    color = BROWN
                
                # Highlight current location
                if location_name == self.current_location:
                    pygame.draw.circle(screen, GOLD, (int(x), int(y)), self.node_radius + 3)
                
                pygame.draw.circle(screen, color, (int(x), int(y)), self.node_radius)
                pygame.draw.circle(screen, BLACK, (int(x), int(y)), self.node_radius, 2)
                
                # Draw location name
                label = font.render(location_name.split()[0], True, BLACK)
                label_rect = label.get_rect(center=(x, y))
                screen.blit(label, label_rect)

class InventoryDisplay:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.SysFont(None, 24)
        self.inventory = []
        self.buttons = []
        
    def update_inventory(self, inventory):
        self.inventory = inventory.copy()
        self.buttons = []
        
        # Create buttons for each inventory item
        for i, item in enumerate(self.inventory):
            btn_y = self.rect.y + 40 + (i * 45)
            btn = Button(
                self.rect.x + 10, 
                btn_y, 
                self.rect.width - 20, 
                40, 
                f"Use {item}", 
                LIGHT_GRAY, 
                GREEN
            )
            self.buttons.append(btn)
        
    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Draw title
        title = self.font.render("Inventory", True, WHITE)
        screen.blit(title, (self.rect.x + 10, self.rect.y + 10))
        
        # Draw buttons for items
        for button in self.buttons:
            button.draw(screen)
            
        # If inventory is empty
        if not self.inventory:
            empty_text = self.font.render("Empty", True, WHITE)
            text_rect = empty_text.get_rect(center=(self.rect.centerx, self.rect.y + 60))
            screen.blit(empty_text, text_rect)

class StatusBar:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.SysFont(None, 24)
        self.health = 100
        self.score = 0
        self.hint_tokens = 3
        
    def update(self, health, score, hint_tokens):
        self.health = health
        self.score = score
        self.hint_tokens = hint_tokens
        
    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Health bar
        health_text = self.font.render(f"Health: {self.health}", True, WHITE)
        screen.blit(health_text, (self.rect.x + 10, self.rect.y + 10))
        
        health_bar_rect = pygame.Rect(self.rect.x + 120, self.rect.y + 10, 150, 20)
        pygame.draw.rect(screen, BLACK, health_bar_rect)
        pygame.draw.rect(screen, WHITE, health_bar_rect, 1)
        health_width = int((self.health / 100) * health_bar_rect.width)
        health_color = GREEN
        if self.health < 50:
            health_color = GOLD
        if self.health < 25:
            health_color = RED
        pygame.draw.rect(screen, health_color, (health_bar_rect.x, health_bar_rect.y, health_width, health_bar_rect.height))
        
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (self.rect.x + 300, self.rect.y + 10))
        
        # Hint tokens
        tokens_text = self.font.render(f"Hint Tokens: {self.hint_tokens}", True, WHITE)
        screen.blit(tokens_text, (self.rect.x + 500, self.rect.y + 10))

class LabyrinthGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("LUMOS Labyrinth")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.levels = {1: "Ancient Entrance", 2: "Crystal Caverns", 3: "Shadow Corridor"}
        self.current_location = self.levels[1]
        self.inventory = []
        self.health = 100
        self.score = 0
        self.labyrinth = self._create_labyrinth()
        self.hint_history = []
        self.lumos = LUMOS()
        self.game_state = "intro"  # intro, game, hint_selection, puzzle
        
        # Hint system mechanics
        self.hint_tokens = 3  # Player starts with 3 free hint tokens
        self.hint_requests = {}  # Track how many hints requested per location
        self.hint_penalty_threshold = 3  # After this many hints, penalties apply
        self.consecutive_hint_count = 0  # Track consecutive hint requests
        self.hint_context = "general"  # Default hint context
        
        # Combat & health mechanics
        self.healing_items = {"Health Potion": 20, "Magic Elixir": 50}
        self.protection_items = {"Shield": 50, "Magic Amulet": 75}
        
        # Score mechanics - track progress
        self.discovered_locations = set()
        self.completed_puzzles = set()
        
        # UI Elements - Adjusted positions to prevent overlap
        self.message_box = MessageBox(20, 270, 600, 300)
        self.inventory_display = InventoryDisplay(660, 270, 340, 300)
        self.status_bar = StatusBar(20, 600, 980, 40)
        self.mini_map = MiniMap(660, 100, 340, 150)
        self.mini_map.set_data(self.labyrinth, self.current_location)
        
        # Navigation buttons
        self.navigation_buttons = []
        self.action_buttons = []
        self.hint_buttons = []
        
        # Initialize game
        self._initialize_ui()
        
    def _create_labyrinth(self):
        """Create a labyrinth structure with hazards, puzzles, and rewards"""
        return {
            "Ancient Entrance": Node(
                name="Ancient Entrance",
                description="A mysterious entrance with ancient symbols carved into the walls.",
                neighbors=[("Crystal Caverns", 5), ("Shadow Corridor", 8)],
                items=["Torch"],
                puzzles={"Symbol Alignment": 15},  # Solving gives 15 points
                position=(20, 50)  # Position for map display
            ),
            "Crystal Caverns": Node(
                name="Crystal Caverns",
                description="Glowing crystals illuminate this beautiful cavern.",
                neighbors=[("Ancient Entrance", 5), ("Shadow Corridor", 3)],
                items=["Light Crystal"],
                required_items=["Torch"],
                hazards={"Crystal Shards": 5},  # 5 health damage if not careful
                puzzles={"Crystal Alignment": 20},  # Solving gives 20 points
                position=(60, 20)  # Position for map display
            ),
            "Shadow Corridor": Node(
                name="Shadow Corridor",
                description="A dark corridor where shadows seem to move on their own.",
                neighbors=[("Ancient Entrance", 8), ("Crystal Caverns", 3)],
                items=["Health Potion", "Shield"],
                hazards={"Living Shadows": 15},  # 15 health damage per turn if not solved
                puzzles={"Shadow Projection": 25},  # Solving gives 25 points
                position=(80, 70)  # Position for map display
            )
        }
        
    def _initialize_ui(self):
        # Add intro message
        self.message_box.add_message("🎮 Welcome to the Labyrinth!", GOLD)
        self.message_box.add_message(self.lumos.greet(), LIGHT_BLUE)
        self.message_box.add_message(f"You start with {self.hint_tokens} hint tokens for free hints.", WHITE)
        self.message_box.add_message("- Explore locations to earn score points", WHITE)
        self.message_box.add_message("- Solve puzzles for rewards", WHITE)
        self.message_box.add_message("- Use hints wisely - they have costs", WHITE)
        self.message_box.add_message("- Watch your health in dangerous areas", WHITE)
        self.message_box.add_message("\nClick 'Start Game' to begin your adventure!", GREEN)
        
        # Create intro screen button
        self.intro_button = Button(
            SCREEN_WIDTH // 2 - 200,  # Modify this X position 
            SCREEN_HEIGHT // 2 + 200,  # Modify this Y position
            200, 
            60, 
            "Start Game", 
            GREEN, 
            LIGHT_BLUE, 
            BLACK, 
            30
        )
        
    def _update_navigation_buttons(self):
        """Update navigation buttons based on current location"""
        self.navigation_buttons = []
        current = self.labyrinth[self.current_location]
        
        # Add navigation buttons - Fixed positioning to prevent overlap
        y_pos = 100
        for i, (location, difficulty) in enumerate(current.neighbors):
            next_room = self.labyrinth[location]
            button_text = f"To {location} (Difficulty: {difficulty})"
            
            # Show lock if room requires items
            if next_room.required_items and not all(item in self.inventory for item in next_room.required_items):
                button_text += f" 🔒 Requires: {', '.join(next_room.required_items)}"
                button_color = GRAY  # Grayed out
            else:
                button_color = LIGHT_BLUE
                
            btn = Button(20, y_pos, 560, 40, button_text, button_color)
            self.navigation_buttons.append((btn, location))
            y_pos += 50
            
        # Update action buttons with correct vertical position
        self._update_action_buttons(y_pos)
        
    def _update_action_buttons(self, start_y=200):  # Changed default vertical starting position
        """Update action buttons based on game state"""
        self.action_buttons = []
        y_pos = start_y
        
        # Use Item button
        use_item_btn = Button(20, y_pos, 260, 40, "Use Item", LIGHT_GRAY)
        self.action_buttons.append((use_item_btn, "use_item"))
        
        # Puzzle button
        current = self.labyrinth[self.current_location]
        if current.puzzles and (set(current.puzzles.keys()) - current.puzzle_solved):
            puzzle_btn = Button(320, y_pos, 260, 40, "Solve Puzzle", LIGHT_GRAY)
            self.action_buttons.append((puzzle_btn, "solve_puzzle"))
        
        y_pos += 50
        
        # Hint button
        hint_btn = Button(20, y_pos, 260, 40, "Ask LUMOS for Hint", GOLD)
        self.action_buttons.append((hint_btn, "request_hint"))
        
        # Quit button
        quit_btn = Button(320, y_pos, 260, 40, "Quit Game", RED)
        self.action_buttons.append((quit_btn, "quit"))
        
    def _update_hint_buttons(self):
        """Create buttons for hint selection"""
        self.hint_buttons = []
        y_pos = 200
        
        hint_options = self.get_hint_options()
        for i, option_text in enumerate(hint_options):
            btn = Button(150, y_pos, 600, 40, option_text, LIGHT_BLUE)
            self.hint_buttons.append((btn, i+1))  # Store button and hint level choice
            y_pos += 60
            
        # Add cancel button
        cancel_btn = Button(350, y_pos, 200, 40, "Cancel", RED)
        self.hint_buttons.append((cancel_btn, "cancel"))
        
    def uniform_cost_search(self, start: str, goal: str) -> List[str]:
        """Implement UCS to find the optimal path through the labyrinth"""
        frontier = []
        explored = set()
        start_node = PathNode(state=start)
        heapq.heappush(frontier, start_node)

        while frontier:
            node = heapq.heappop(frontier)
            if node.state == goal:
                path = []
                while node.parent:
                    path.append(node.action)
                    node = node.parent
                return list(reversed(path))

            if node.state in explored:
                continue
            explored.add(node.state)

            current_room = self.labyrinth[node.state]
            for next_location, cost in current_room.neighbors:
                if next_location not in explored:
                    # Consider inventory requirements in pathfinding
                    next_room = self.labyrinth[next_location]
                    if next_room.required_items and not all(item in self.inventory for item in next_room.required_items):
                        # Increase cost for locked rooms
                        adjusted_cost = cost * 3
                    else:
                        adjusted_cost = cost

                    # Consider hazards in pathfinding
                    if next_room.hazards and not any(item in self.protection_items for item in self.inventory):
                        # Increase cost for dangerous rooms without protection
                        hazard_penalty = sum(damage for damage in next_room.hazards.values())
                        adjusted_cost += hazard_penalty / 2

                    child = PathNode(
                        state=next_location,
                        parent=node,
                        action=f"Move to {next_location}",
                        path_cost=node.path_cost + adjusted_cost
                    )
                    heapq.heappush(frontier, child)
        return []

    def get_hint_options(self) -> List[str]:
        """Get available hint options based on current tokens and costs"""
        hint_options = []

        # Add free hint if player has tokens
        if self.hint_tokens > 0:
            hint_options.append(f"1. Vague hint (Free - {self.hint_tokens} tokens left)")
        else:
            hint_options.append(f"1. Vague hint (Cost: {self.lumos.hint_costs['vague']} points)")

        # Add paid hint options
        hint_options.append(f"2. Moderate hint (Cost: {self.lumos.hint_costs['moderate']} points)")
        hint_options.append(f"3. Specific hint (Cost: {self.lumos.hint_costs['specific']} points)")
        hint_options.append(f"4. Explicit hint (Cost: {self.lumos.hint_costs['explicit']} points)")

        return hint_options

    def request_hint(self, choice: int) -> None:
        """Handle player hint requests with cost system and consequences"""
        # Track hint requests for this location
        self.hint_requests[self.current_location] = self.hint_requests.get(self.current_location, 0) + 1
        self.consecutive_hint_count += 1

        if 1 <= choice <= 4:
            hint_levels = ["vague", "moderate", "specific", "explicit"]
            selected_level = hint_levels[choice-1]

            # Calculate cost with penalties
            base_cost = self.lumos.hint_costs[selected_level]
            penalty_multiplier = 1.0

            # Apply penalties for excessive hints at this location
            if self.hint_requests[self.current_location] > self.hint_penalty_threshold:
                penalty_multiplier = 1.5
                self.message_box.add_message("\n💫 LUMOS: The magic here grows weaker with repeated questions...", LIGHT_BLUE)

            # Apply penalty for consecutive hints anywhere
            if self.consecutive_hint_count > 2:
                penalty_multiplier += 0.5
                self.message_box.add_message("\n💫 LUMOS: My energy drains with so many questions in succession...", LIGHT_BLUE)

            final_cost = round(base_cost * penalty_multiplier)

            # Check if player has tokens for vague hints
            if choice == 1 and self.hint_tokens > 0:
                self.hint_tokens -= 1
                self.message_box.add_message(f"\n💫 LUMOS is using one of your hint tokens. {self.hint_tokens} tokens remaining.", GOLD)
                cost_applied = 0
            else:
                # Apply the cost
                if self.score >= final_cost:
                    self.score -= final_cost
                    cost_applied = final_cost
                    if penalty_multiplier > 1.0:
                        self.message_box.add_message("\n💫 LUMOS: The magic requires more energy due to repeated inquiries...", LIGHT_BLUE)
                else:
                    self.message_box.add_message("\n💫 LUMOS: You do not have enough points for this level of insight.", RED)
                    self.message_box.add_message(f"Cost: {final_cost} points. Your score: {self.score} points.", RED)
                    return

            # Add health penalty for explicit hints - Conversation has consequences!
            if selected_level == "explicit" and choice != 1:
                health_cost = 5
                self.health -= health_cost
                self.message_box.add_message(f"\n💫 LUMOS: Warning - such direct knowledge taxes your life force! (-{health_cost} health)", RED)

            # Deliver the hint
# Deliver the hint
            hint, _ = self.lumos.give_hint(self.current_location, self.hint_context, selected_level)
            
            # Add hint to history
            self.hint_history.append({
                "location": self.current_location,
                "level": selected_level,
                "text": hint,
                "cost": cost_applied
            })
            
            self.message_box.add_message(f"\n💫 LUMOS: {hint}", LIGHT_BLUE)
            if cost_applied > 0:
                self.message_box.add_message(f"Cost: {cost_applied} points deducted.", GOLD)
            
            # Small chance (20%) for bonus encouragement from LUMOS
            if random.random() < 0.2:
                self.message_box.add_message(f"\n💫 LUMOS: {self.lumos.encourage()}", LIGHT_BLUE)
                
        elif choice == "cancel":
            self.message_box.add_message("\nHint request canceled.", WHITE)
            self.consecutive_hint_count -= 1  # Don't count canceled requests
            
        # Reset game state
        self.game_state = "game"
        self._update_navigation_buttons()
            
    def process_location(self) -> None:
        """Process arrival at a new location"""
        current = self.labyrinth[self.current_location]
        
        # Add location to discovered locations
        if self.current_location not in self.discovered_locations:
            self.discovered_locations.add(self.current_location)
            self.score += 10  # Points for discovering new location
            self.message_box.add_message(f"\n🏆 +10 points for discovering {self.current_location}!", GREEN)
            
        # Apply hazards if present
        for hazard, damage in current.hazards.items():
            # Check for protection items
            protected = False
            for item in self.inventory:
                if item in self.protection_items:
                    protected = True
                    protection_value = self.protection_items[item]
                    reduced_damage = max(0, damage - (damage * protection_value / 100))
                    if reduced_damage > 0:
                        self.health -= reduced_damage
                        self.message_box.add_message(f"\n⚠️ {hazard} causes {reduced_damage:.1f} damage (reduced by {item})!", GOLD)
                    else:
                        self.message_box.add_message(f"\n🛡️ Your {item} completely protects you from {hazard}!", GREEN)
                    break
                    
            if not protected:
                self.health -= damage
                self.message_box.add_message(f"\n⚠️ {hazard} causes {damage} damage!", RED)
                
        # Handle death
        if self.health <= 0:
            self.health = 0
            self.message_box.add_message("\n💀 You have fallen in the labyrinth! Game over.", RED)
            self.game_state = "game_over"
            return
            
        # Check for items to collect
        if current.items:
            self.message_box.add_message("\nYou find the following items:", WHITE)
            for item in current.items[:]:  # Create a copy to iterate while removing
                self.message_box.add_message(f"- {item}", GREEN)
                self.inventory.append(item)
                current.items.remove(item)
                
            self.inventory_display.update_inventory(self.inventory)
            
        # Reset consecutive hint count when moving
        self.consecutive_hint_count = 0
            
    def solve_puzzle(self) -> None:
        """Handle puzzle solving"""
        current = self.labyrinth[self.current_location]
        unsolved_puzzles = set(current.puzzles.keys()) - current.puzzle_solved
        
        if not unsolved_puzzles:
            self.message_box.add_message("\nThere are no puzzles to solve here.", WHITE)
            return
            
        puzzle = next(iter(unsolved_puzzles))
        reward = current.puzzles[puzzle]
        
        # Set hint context to puzzle for more relevant hints
        self.hint_context = "puzzle"
        
        self.message_box.add_message(f"\nYou attempt to solve the {puzzle} puzzle...", WHITE)
        
        # Simulate puzzle solving with higher chance of success if player has received hints
        received_hints = sum(1 for h in self.hint_history if h["location"] == self.current_location and h["level"] in ["specific", "explicit"])
        
        success_chance = 0.3 + (received_hints * 0.2)  # Base 30% + 20% per relevant hint
        
        if random.random() < success_chance:
            self.message_box.add_message("\n🎮 Success! You solved the puzzle!", GREEN)
            self.message_box.add_message(f"🏆 +{reward} points awarded!", GREEN)
            self.score += reward
            current.puzzle_solved.add(puzzle)
            self.completed_puzzles.add(f"{self.current_location}: {puzzle}")
            
            # Bonus reward: hint token for puzzle completion
            if random.random() < 0.5:
                self.hint_tokens += 1
                self.message_box.add_message("💫 You've earned a hint token as a bonus reward!", GOLD)
                
            # Check if room was locked and now can be unlocked
            if current.locked and not current.required_items:
                current.locked = False
                self.message_box.add_message("\n🔓 This room is now fully accessible!", GREEN)
        else:
            self.message_box.add_message("\n❌ You failed to solve the puzzle. Try again or use a hint.", RED)
            
            # Small health penalty for failed puzzle attempts
            damage = 5
            self.health -= damage
            self.message_box.add_message(f"😵 The failed attempt cost you {damage} health!", RED)
            
        # Reset hint context
        self.hint_context = "general"
        
    def use_item(self, item: str) -> None:
        """Handle item usage"""
        if item in self.healing_items:
            # Apply healing effect
            heal_amount = self.healing_items[item]
            self.health = min(100, self.health + heal_amount)
            self.message_box.add_message(f"\n💊 You used {item} and recovered {heal_amount} health!", GREEN)
            self.inventory.remove(item)
            self.inventory_display.update_inventory(self.inventory)
        elif "Torch" in item and "Crystal" in self.current_location:
            # Special interaction in crystal caverns
            self.message_box.add_message("\n✨ Your torch causes the crystals to glow brightly!", LIGHT_BLUE)
            self.message_box.add_message("The path becomes clearer, and you feel energized.", LIGHT_BLUE)
            self.score += 5
            self.message_box.add_message("🏆 +5 points for clever item usage!", GREEN)
        else:
            self.message_box.add_message(f"\nYou cannot use {item} here effectively.", GOLD)
            
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                # Handle mouse hover
                if self.game_state == "intro":
                    self.intro_button.check_hover(mouse_pos)
                    
                    # Check if intro button clicked
                    if self.intro_button.is_clicked(mouse_pos, event):
                        self.game_state = "game"
                        self.message_box.add_message("\n🚪 Your adventure begins! Where would you like to go?", WHITE)
                        self._update_navigation_buttons()
                        
                elif self.game_state == "game":
                    # Handle navigation buttons
                    for button, destination in self.navigation_buttons:
                        button.check_hover(mouse_pos)
                        if button.is_clicked(mouse_pos, event):
                            next_room = self.labyrinth[destination]
                            if next_room.required_items and not all(item in self.inventory for item in next_room.required_items):
                                self.message_box.add_message(f"\n🔒 You need {', '.join(next_room.required_items)} to enter {destination}.", RED)
                            else:
                                self.current_location = destination
                                self.message_box.add_message(f"\n🚶 You move to {destination}.", WHITE)
                                self.message_box.add_message(next_room.description, WHITE)
                                self._update_navigation_buttons()
                                self.mini_map.set_data(self.labyrinth, self.current_location)
                                self.process_location()
                    
                    # Handle action buttons
                    for button, action in self.action_buttons:
                        button.check_hover(mouse_pos)
                        if button.is_clicked(mouse_pos, event):
                            if action == "request_hint":
                                self.game_state = "hint_selection"
                                self._update_hint_buttons()
                                self.message_box.add_message("\n💫 LUMOS: What level of guidance do you seek?", LIGHT_BLUE)
                            elif action == "solve_puzzle":
                                self.solve_puzzle()
                            elif action == "use_item":
                                if not self.inventory:
                                    self.message_box.add_message("\nYour inventory is empty.", RED)
                                # Items are handled by inventory display
                            elif action == "quit":
                                running = False
                    
                    # Handle inventory item buttons
                    for i, button in enumerate(self.inventory_display.buttons):
                        button.check_hover(mouse_pos)
                        if button.is_clicked(mouse_pos, event):
                            item = self.inventory[i]
                            self.use_item(item)
                    
                elif self.game_state == "hint_selection":
                    # Handle hint buttons
                    for button, choice in self.hint_buttons:
                        button.check_hover(mouse_pos)
                        if button.is_clicked(mouse_pos, event):
                            self.request_hint(choice)
                
                # Handle message box scrolling
                self.message_box.handle_scroll(event)
                    
            # Update status
            self.status_bar.update(self.health, self.score, self.hint_tokens)
            
            # Draw background
            self.screen.fill(BLACK)
            
            # Draw title
            font = pygame.font.SysFont(None, 48)
            title = font.render("LUMOS Labyrinth", True, GOLD)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
            
            # Draw current location
            if self.game_state != "intro":
                loc_font = pygame.font.SysFont(None, 36)
                location_text = loc_font.render(f"Location: {self.current_location}", True, WHITE)
                self.screen.blit(location_text, (20, 80))
            
            # Draw UI elements
            if self.game_state == "intro":
                intro_font = pygame.font.SysFont(None, 32)
                intro_text = intro_font.render("A mysterious labyrinth awaits exploration...", True, WHITE)
                self.screen.blit(intro_text, (SCREEN_WIDTH // 2 - intro_text.get_width() // 2, 150))
                
                self.intro_button.draw(self.screen)
            
            elif self.game_state == "game":
                # Draw navigation and action buttons
                for button, _ in self.navigation_buttons:
                    button.draw(self.screen)
                    
                for button, _ in self.action_buttons:
                    button.draw(self.screen)
                    
            elif self.game_state == "hint_selection":
                # Draw hint prompt
                hint_font = pygame.font.SysFont(None, 32)
                hint_text = hint_font.render("Select a hint level:", True, WHITE)
                self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, 150))
                
                for button, _ in self.hint_buttons:
                    button.draw(self.screen)
                    
            elif self.game_state == "game_over":
                game_over_font = pygame.font.SysFont(None, 64)
                game_over_text = game_over_font.render("GAME OVER", True, RED)
                self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 150))
                
                score_text = pygame.font.SysFont(None, 32).render(f"Final Score: {self.score}", True, WHITE)
                self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))
                
                # Show restart button
                restart_button = Button(
                    SCREEN_WIDTH // 2 - 100, 
                    350, 
                    200, 
                    60, 
                    "Exit Game", 
                    RED, 
                    BLUE, 
                    WHITE, 
                    30
                )
                restart_button.draw(self.screen)
                restart_button.check_hover(mouse_pos)
                if restart_button.is_clicked(mouse_pos, event):
                    running = False
            
            # Draw message box and other UI components
            self.message_box.draw(self.screen)
            self.inventory_display.draw(self.screen)
            self.status_bar.draw(self.screen)
            self.mini_map.draw(self.screen, self.discovered_locations)
            
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    game = LabyrinthGame()
    game.run()