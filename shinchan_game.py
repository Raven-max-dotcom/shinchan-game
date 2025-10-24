import pygame
import sys
import math
import random
from enum import Enum

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shin-chan Universe: Modern 3D")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
SKIN_COLOR = (255, 218, 185)
DARK_GREEN = (0, 100, 0)
LIGHT_BLUE = (173, 216, 230)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Game states
class GameState(Enum):
    CHARACTER_SELECT = 1
    PLAYING = 2
    PAUSED = 3

# Character class with 3D-like rendering
class Character:
    def __init__(self, name, x, y, z, color, speed, special_ability, ability_effect):
        self.name = name
        self.x = x
        self.y = y
        self.z = z  # Height for 3D effect
        self.color = color
        self.speed = speed
        self.special_ability = special_ability
        self.ability_effect = ability_effect
        self.ability_cooldown = 0
        self.ability_active = False
        self.ability_timer = 0
        self.score = 0
        self.direction = 0  # Direction character is facing
        self.animation_frame = 0
        self.animation_speed = 0.2
        
    def update(self):
        # Handle ability cooldown and timer
        if self.ability_cooldown > 0:
            self.ability_cooldown -= 1
        
        if self.ability_active:
            self.ability_timer -= 1
            if self.ability_timer <= 0:
                self.ability_active = False
                self.deactivate_ability()
        
        # Update animation
        self.animation_frame += self.animation_speed
        if self.animation_frame >= 4:
            self.animation_frame = 0
    
    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed
        
        # Keep character on screen
        self.x = max(50, min(self.x, SCREEN_WIDTH - 50))
        self.y = max(50, min(self.y, SCREEN_HEIGHT - 100))
    
    def use_ability(self):
        if self.ability_cooldown == 0:
            self.ability_active = True
            self.ability_timer = 300  # 5 seconds at 60 FPS
            self.ability_cooldown = 600  # 10 seconds cooldown
            self.activate_ability()
            return True
        return False
    
    def activate_ability(self):
        # Override in subclasses
        pass
    
    def deactivate_ability(self):
        # Override in subclasses
        pass
    
    def draw_3d(self, surface):
        # Calculate screen position with pseudo-3D effect
        screen_x = int(self.x)
        screen_y = int(self.y - self.z)
        
        # Draw shadow
        shadow_offset = 5
        pygame.draw.ellipse(surface, (50, 50, 50, 100), 
                           (screen_x - 20, screen_y + 40 + shadow_offset, 40, 10))
        
        # Draw character body with 3D effect
        body_height = 60
        body_width = 30
        
        # Body
        body_rect = pygame.Rect(screen_x - body_width//2, screen_y, body_width, body_height)
        pygame.draw.rect(surface, self.color, body_rect)
        
        # Head
        head_radius = 15
        pygame.draw.circle(surface, SKIN_COLOR, (screen_x, screen_y - 10), head_radius)
        
        # Eyes
        eye_offset = 5
        pygame.draw.circle(surface, BLACK, (screen_x - eye_offset, screen_y - 12), 3)
        pygame.draw.circle(surface, BLACK, (screen_x + eye_offset, screen_y - 12), 3)
        
        # Mouth (simple smile)
        pygame.draw.arc(surface, BLACK, (screen_x - 8, screen_y - 8, 16, 10), 0, math.pi, 2)
        
        # Arms
        arm_length = 20
        arm_y = screen_y + 10
        
        # Left arm
        pygame.draw.line(surface, self.color, 
                        (screen_x - body_width//2, arm_y),
                        (screen_x - body_width//2 - 10, arm_y + arm_length), 3)
        
        # Right arm
        pygame.draw.line(surface, self.color, 
                        (screen_x + body_width//2, arm_y),
                        (screen_x + body_width//2 + 10, arm_y + arm_length), 3)
        
        # Legs
        leg_length = 25
        leg_y = screen_y + body_height
        
        # Left leg
        pygame.draw.line(surface, self.color, 
                        (screen_x - 5, leg_y),
                        (screen_x - 10, leg_y + leg_length), 3)
        
        # Right leg
        pygame.draw.line(surface, self.color, 
                        (screen_x + 5, leg_y),
                        (screen_x + 10, leg_y + leg_length), 3)
        
        # Draw ability effect if active
        if self.ability_active:
            self.draw_ability_effect(surface, screen_x, screen_y)
        
        # Draw name
        font = pygame.font.SysFont(None, 20)
        text = font.render(self.name, True, BLACK)
        text_rect = text.get_rect(center=(screen_x, screen_y - 40))
        surface.blit(text, text_rect)
        
        # Draw ability cooldown bar
        self.draw_ability_bar(surface, screen_x, screen_y)
    
    def draw_ability_effect(self, surface, x, y):
        # Override in subclasses
        pass
    
    def draw_ability_bar(self, surface, x, y):
        bar_width = 60
        bar_height = 6
        bar_x = x - bar_width // 2
        bar_y = y + 80
        
        # Background
        pygame.draw.rect(surface, GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # Cooldown progress
        if self.ability_cooldown > 0:
            progress = 1 - (self.ability_cooldown / 600)
            pygame.draw.rect(surface, GREEN, (bar_x, bar_y, bar_width * progress, bar_height))
        else:
            pygame.draw.rect(surface, YELLOW, (bar_x, bar_y, bar_width, bar_height))

# Shin character
class Shin(Character):
    def __init__(self, x, y):
        super().__init__("Shin", x, y, 0, RED, 5, "Mischief Mode", "Causes chaos around him")
        self.mischief_particles = []
    
    def activate_ability(self):
        # Create mischief particles
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            self.mischief_particles.append({
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 100
            })
    
    def draw_ability_effect(self, surface, x, y):
        # Draw mischief particles
        for particle in self.mischief_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            if particle['life'] > 0:
                pygame.draw.circle(surface, YELLOW, 
                                 (int(particle['x']), int(particle['y'])), 
                                 int(particle['life'] / 10))
            else:
                self.mischief_particles.remove(particle)
        
        # Draw aura
        pygame.draw.circle(surface, (255, 255, 0, 50), (x, y), 50, 2)

# Misae character
class Misae(Character):
    def __init__(self, x, y):
        super().__init__("Misae", x, y, 0, BLUE, 4, "Mother's Wrath", "Moves faster and stronger")
        self.original_speed = self.speed
    
    def activate_ability(self):
        self.speed = 8  # Speed boost
    
    def deactivate_ability(self):
        self.speed = self.original_speed
    
    def draw_ability_effect(self, surface, x, y):
        # Draw speed lines
        for i in range(5):
            angle = random.uniform(0, 2 * math.pi)
            length = random.uniform(20, 40)
            end_x = x + math.cos(angle) * length
            end_y = y + math.sin(angle) * length
            pygame.draw.line(surface, BLUE, (x, y), (end_x, end_y), 2)

# Hiroshi character
class Hiroshi(Character):
    def __init__(self, x, y):
        super().__init__("Hiroshi", x, y, 0, GREEN, 3, "Salaryman Power", "Temporary invincibility")
        self.invincible = False
    
    def activate_ability(self):
        self.invincible = True
    
    def deactivate_ability(self):
        self.invincible = False
    
    def draw_ability_effect(self, surface, x, y):
        # Draw invincibility shield
        pygame.draw.circle(surface, (0, 255, 0, 100), (x, y), 40, 3)
        # Draw Z's for sleeping effect
        font = pygame.font.SysFont(None, 30)
        z_text = font.render("Z", True, GREEN)
        surface.blit(z_text, (x - 10, y - 60))

# Kazama character
class Kazama(Character):
    def __init__(self, x, y):
        super().__init__("Kazama", x, y, 0, PURPLE, 4, "Perfect Etiquette", "Charms nearby NPCs")
        self.charm_radius = 100
    
    def draw_ability_effect(self, surface, x, y):
        # Draw charm radius
        pygame.draw.circle(surface, (128, 0, 128, 50), (x, y), self.charm_radius, 2)
        # Draw hearts
        for i in range(3):
            heart_x = x + random.randint(-30, 30)
            heart_y = y - random.randint(20, 50)
            self.draw_heart(surface, heart_x, heart_y, 10)
    
    def draw_heart(self, surface, x, y, size):
        # Simple heart shape
        pygame.draw.polygon(surface, RED, [
            (x, y + size//2),
            (x - size//2, y - size//2),
            (x - size, y),
            (x, y + size),
            (x + size, y),
            (x + size//2, y - size//2)
        ])

# NPC class
class NPC(Character):
    def __init__(self, name, x, y, color, speed, dialogue):
        super().__init__(name, x, y, 0, color, speed, "Talk", "Interact with player")
        self.dialogue = dialogue
        self.talking = False
        self.dialogue_timer = 0
        self.charmed = False
    
    def interact(self, player):
        self.talking = True
        self.dialogue_timer = 180  # 3 seconds at 60 FPS
        
        # Check if player is charming
        if isinstance(player, Kazama) and player.ability_active:
            distance = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
            if distance < player.charm_radius:
                self.charmed = True
                return f"Oh {player.name}, you're so well-mannered!"
        
        # Different reactions based on character
        if player.name == "Shin":
            if self.name == "Misae":
                return "Shin! Stop causing trouble!"
            elif self.name == "Kazama":
                return "Shin, you're so childish!"
            else:
                return f"Hello, {player.name}!"
        else:
            return f"Hello, {player.name}!"
    
    def update(self):
        super.update()
        
        # Handle dialogue timer
        if self.dialogue_timer > 0:
            self.dialogue_timer -= 1
        else:
            self.talking = False
        
        # Simple AI movement
        if random.randint(0, 100) < 2:
            dx = random.randint(-1, 1)
            dy = random.randint(-1, 1)
            self.move(dx, dy)
    
    def draw_3d(self, surface):
        super().draw_3d(surface)
        
        # Draw dialogue bubble if talking
        if self.talking:
            bubble_x = int(self.x)
            bubble_y = int(self.y - 80)
            
            # Draw bubble
            bubble_rect = pygame.Rect(bubble_x - 60, bubble_y, 120, 40)
            pygame.draw.rect(surface, WHITE, bubble_rect)
            pygame.draw.rect(surface, BLACK, bubble_rect, 2)
            
            # Draw tail
            pygame.draw.polygon(surface, WHITE, [
                (bubble_x, bubble_y + 40),
                (bubble_x - 10, bubble_y + 50),
                (bubble_x + 10, bubble_y + 50)
            ])
            
            # Draw dialogue text
            font = pygame.font.SysFont(None, 18)
            text = font.render("Hello!", True, BLACK)
            text_rect = text.get_rect(center=(bubble_x, bubble_y + 20))
            surface.blit(text, text_rect)

# Environment class with 3D-like objects
class Environment:
    def __init__(self):
        self.objects = []
        self.particles = []
        
        # Create environment objects
        self.create_world()
    
    def create_world(self):
        # Nohara House
        self.objects.append({
            "type": "house",
            "x": 200,
            "y": 300,
            "width": 150,
            "height": 120,
            "color": BROWN,
            "name": "Nohara House"
        })
        
        # Futaba Kindergarten
        self.objects.append({
            "type": "building",
            "x": 600,
            "y": 200,
            "width": 200,
            "height": 150,
            "color": YELLOW,
            "name": "Futaba Kindergarten"
        })
        
        # Kasukabe Park
        self.objects.append({
            "type": "park",
            "x": 400,
            "y": 500,
            "width": 250,
            "height": 180,
            "color": DARK_GREEN,
            "name": "Kasukabe Park"
        })
        
        # Trees
        for _ in range(15):
            self.objects.append({
                "type": "tree",
                "x": random.randint(50, SCREEN_WIDTH - 50),
                "y": random.randint(50, SCREEN_HEIGHT - 100),
                "width": 40,
                "height": 60,
                "color": (0, 100, 0),
                "name": "Tree"
            })
        
        # Saitama District (separated by river)
        self.objects.append({
            "type": "district",
            "x": 900,
            "y": 100,
            "width": 250,
            "height": 600,
            "color": GRAY,
            "name": "Saitama District"
        })
    
    def draw_3d(self, surface):
        # Sort objects by y position for proper depth rendering
        sorted_objects = sorted(self.objects, key=lambda obj: obj["y"])
        
        for obj in sorted_objects:
            if obj["type"] == "house":
                self.draw_house_3d(surface, obj)
            elif obj["type"] == "building":
                self.draw_building_3d(surface, obj)
            elif obj["type"] == "park":
                self.draw_park_3d(surface, obj)
            elif obj["type"] == "tree":
                self.draw_tree_3d(surface, obj)
            elif obj["type"] == "district":
                self.draw_district_3d(surface, obj)
    
    def draw_house_3d(self, surface, obj):
        # Draw house shadow
        shadow_offset = 10
        pygame.draw.rect(surface, (50, 50, 50, 50), 
                        (obj["x"] - shadow_offset, obj["y"] + obj["height"] - shadow_offset, 
                         obj["width"], 10))
        
        # Draw house base
        pygame.draw.rect(surface, obj["color"], 
                        (obj["x"], obj["y"], obj["width"], obj["height"]))
        
        # Draw roof
        roof_points = [
            (obj["x"], obj["y"]),
            (obj["x"] + obj["width"] // 2, obj["y"] - 40),
            (obj["x"] + obj["width"], obj["y"])
        ]
        pygame.draw.polygon(surface, RED, roof_points)
        
        # Draw door
        door_width = 30
        door_height = 50
        pygame.draw.rect(surface, BLACK, 
                        (obj["x"] + obj["width"]//2 - door_width//2, 
                         obj["y"] + obj["height"] - door_height, 
                         door_width, door_height))
        
        # Draw windows
        window_size = 25
        pygame.draw.rect(surface, LIGHT_BLUE, 
                        (obj["x"] + 20, obj["y"] + 30, window_size, window_size))
        pygame.draw.rect(surface, LIGHT_BLUE, 
                        (obj["x"] + obj["width"] - 45, obj["y"] + 30, window_size, window_size))
    
    def draw_building_3d(self, surface, obj):
        # Draw building shadow
        shadow_offset = 15
        pygame.draw.rect(surface, (50, 50, 50, 50), 
                        (obj["x"] - shadow_offset, obj["y"] + obj["height"] - shadow_offset, 
                         obj["width"], 15))
        
        # Draw building base
        pygame.draw.rect(surface, obj["color"], 
                        (obj["x"], obj["y"], obj["width"], obj["height"]))
        
        # Draw windows in grid
        window_rows = 3
        window_cols = 4
        window_size = 30
        window_spacing = 15
        
        for row in range(window_rows):
            for col in range(window_cols):
                x = obj["x"] + 20 + col * (window_size + window_spacing)
                y = obj["y"] + 30 + row * (window_size + window_spacing)
                pygame.draw.rect(surface, LIGHT_BLUE, (x, y, window_size, window_size))
        
        # Draw school sign
        sign_width = 80
        sign_height = 20
        pygame.draw.rect(surface, WHITE, 
                        (obj["x"] + obj["width"]//2 - sign_width//2, 
                         obj["y"] - 20, sign_width, sign_height))
        font = pygame.font.SysFont(None, 16)
        text = font.render("Futaba", True, BLACK)
        text_rect = text.get_rect(center=(obj["x"] + obj["width"]//2, obj["y"] - 10))
        surface.blit(text, text_rect)
    
    def draw_park_3d(self, surface, obj):
        # Draw park shadow
        shadow_offset = 20
        pygame.draw.ellipse(surface, (50, 50, 50, 50), 
                           (obj["x"] - shadow_offset, obj["y"] + obj["height"] - shadow_offset, 
                            obj["width"], 30))
        
        # Draw park base
        pygame.draw.ellipse(surface, obj["color"], 
                           (obj["x"], obj["y"], obj["width"], obj["height"]))
        
        # Draw playground equipment
        # Slide
        slide_x = obj["x"] + 30
        slide_y = obj["y"] + 40
        pygame.draw.rect(surface, BLUE, (slide_x, slide_y, 60, 5))
        pygame.draw.polygon(surface, BLUE, [
            (slide_x, slide_y),
            (slide_x + 60, slide_y - 30),
            (slide_x + 60, slide_y - 25),
            (slide_x, slide_y + 5)
        ])
        
        # Swing set
        swing_x = obj["x"] + 120
        swing_y = obj["y"] + 30
        pygame.draw.line(surface, BLACK, (swing_x, swing_y), (swing_x, swing_y + 40), 3)
        pygame.draw.line(surface, BLACK, (swing_x + 30, swing_y), (swing_x + 30, swing_y + 40), 3)
        pygame.draw.line(surface, BLACK, (swing_x, swing_y), (swing_x + 30, swing_y), 3)
        
        # Draw park name
        font = pygame.font.SysFont(None, 24)
        text = font.render("Kasukabe Park", True, WHITE)
        text_rect = text.get_rect(center=(obj["x"] + obj["width"]//2, obj["y"] + 20))
        surface.blit(text, text_rect)
    
    def draw_tree_3d(self, surface, obj):
        # Draw tree shadow
        shadow_offset = 8
        pygame.draw.ellipse(surface, (50, 50, 50, 50), 
                           (obj["x"] - shadow_offset, obj["y"] + obj["height"] - shadow_offset, 
                            obj["width"], 10))
        
        # Draw trunk
        trunk_width = 10
        trunk_height = 30
        pygame.draw.rect(surface, BROWN, 
                        (obj["x"] + obj["width"]//2 - trunk_width//2, 
                         obj["y"] + obj["height"] - trunk_height, 
                         trunk_width, trunk_height))
        
        # Draw leaves
        leaf_radius = obj["width"] // 2
        pygame.draw.circle(surface, obj["color"], 
                          (obj["x"] + obj["width"]//2, obj["y"] + obj["height"]//2), 
                          leaf_radius)
    
    def draw_district_3d(self, surface, obj):
        # Draw district shadow
        shadow_offset = 25
        pygame.draw.rect(surface, (50, 50, 50, 50), 
                        (obj["x"] - shadow_offset, obj["y"] + obj["height"] - shadow_offset, 
                         obj["width"], 20))
        
        # Draw district base
        pygame.draw.rect(surface, obj["color"], 
                        (obj["x"], obj["y"], obj["width"], obj["height"]))
        
        # Draw district name
        font = pygame.font.SysFont(None, 28)
        text = font.render("Saitama", True, WHITE)
        text_rect = text.get_rect(center=(obj["x"] + obj["width"]//2, obj["y"] + 30))
        surface.blit(text, text_rect)
        
        # Draw some buildings in district
        for i in range(3):
            building_x = obj["x"] + 30 + i * 70
            building_y = obj["y"] + 80
            building_width = 50
            building_height = 100 - i * 20
            
            pygame.draw.rect(surface, (100, 100, 100), 
                            (building_x, building_y, building_width, building_height))
            
            # Draw windows
            for j in range(3):
                window_y = building_y + 10 + j * 25
                pygame.draw.rect(surface, YELLOW, 
                                (building_x + 10, window_y, 15, 15))
                pygame.draw.rect(surface, YELLOW, 
                                (building_x + 25, window_y, 15, 15))

# Game class
class Game:
    def __init__(self):
        self.state = GameState.CHARACTER_SELECT
        self.player = None
        self.npcs = []
        self.environment = Environment()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.large_font = pygame.font.SysFont(None, 72)
        self.camera_x = 0
        self.camera_y = 0
        
        # Define characters
        self.characters = [
            {"name": "Shin", "class": Shin, "color": RED, "description": "Mischief Mode: Causes chaos around him"},
            {"name": "Misae", "class": Misae, "color": BLUE, "description": "Mother's Wrath: Moves faster and stronger"},
            {"name": "Hiroshi", "class": Hiroshi, "color": GREEN, "description": "Salaryman Power: Temporary invincibility"},
            {"name": "Kazama", "class": Kazama, "color": PURPLE, "description": "Perfect Etiquette: Charms nearby NPCs"}
        ]
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.CHARACTER_SELECT:
                    # Number keys 1-4 to select character
                    if pygame.K_1 <= event.key <= pygame.K_4:
                        index = event.key - pygame.K_1
                        if index < len(self.characters):
                            char_data = self.characters[index]
                            self.player = char_data["class"](SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                            self.create_npcs()
                            self.state = GameState.PLAYING
                
                elif self.state == GameState.PLAYING:
                    # Space to use special ability
                    if event.key == pygame.K_SPACE:
                        if self.player.use_ability():
                            self.player.score += 10
                    
                    # E key to interact with NPCs
                    if event.key == pygame.K_e:
                        for npc in self.npcs:
                            distance = math.sqrt((npc.x - self.player.x)**2 + (npc.y - self.player.y)**2)
                            if distance < 100:
                                dialogue = npc.interact(self.player)
                                print(dialogue)  # In a real game, show this on screen
                    
                    # P key to pause
                    if event.key == pygame.K_p:
                        self.state = GameState.PAUSED
                    
                    # R key to return to character select
                    if event.key == pygame.K_r:
                        self.state = GameState.CHARACTER_SELECT
                        self.player = None
                        self.npcs = []
                
                elif self.state == GameState.PAUSED:
                    # P key to unpause
                    if event.key == pygame.K_p:
                        self.state = GameState.PLAYING
        
        return True
    
    def create_npcs(self):
        # Create NPCs that aren't the player character
        for char_data in self.characters:
            if char_data["name"] != self.player.name:
                npc = char_data["class"](
                    random.randint(100, SCREEN_WIDTH - 100),
                    random.randint(100, SCREEN_HEIGHT - 100)
                )
                self.npcs.append(npc)
    
    def update(self):
        if self.state == GameState.PLAYING:
            # Handle player movement
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1
            
            # Normalize diagonal movement
            if dx != 0 and dy != 0:
                dx *= 0.707
                dy *= 0.707
            
            self.player.move(dx, dy)
            self.player.update()
            
            # Update NPCs
            for npc in self.npcs:
                npc.update()
            
            # Update camera to follow player
            self.camera_x = self.player.x - SCREEN_WIDTH // 2
            self.camera_y = self.player.y - SCREEN_HEIGHT // 2
    
    def draw_character_select(self):
        screen.fill(LIGHT_BLUE)
        
        # Draw title
        title = self.large_font.render("SHIN-CHAN UNIVERSE", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)
        
        subtitle = self.font.render("Choose Your Character", True, BLACK)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 180))
        screen.blit(subtitle, subtitle_rect)
        
        # Draw character options
        for i, char_data in enumerate(self.characters):
            x = 200 + (i % 2) * 400
            y = 250 + (i // 2) * 250
            
            # Draw character card background
            card_rect = pygame.Rect(x - 150, y - 50, 300, 200)
            pygame.draw.rect(screen, WHITE, card_rect)
            pygame.draw.rect(screen, char_data["color"], card_rect, 5)
            
            # Draw character preview
            preview = char_data["class"](x, y)
            preview.draw_3d(screen)
            
            # Draw character info
            name_text = self.font.render(f"{i+1}. {char_data['name']}", True, BLACK)
            name_rect = name_text.get_rect(center=(x, y - 80))
            screen.blit(name_text, name_rect)
            
            # Draw ability description
            ability_text = self.small_font.render(char_data['description'], True, BLACK)
            ability_rect = ability_text.get_rect(center=(x, y + 80))
            screen.blit(ability_text, ability_rect)
        
        # Draw instructions
        inst_text = self.small_font.render("Press 1-4 to select a character", True, BLACK)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(inst_text, inst_rect)
    
    def draw_game(self):
        # Draw sky gradient
        for y in range(SCREEN_HEIGHT):
            color_value = int(173 + (255 - 173) * (y / SCREEN_HEIGHT))
            color = (color_value, color_value, 255)
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Draw environment
        self.environment.draw_3d(screen)
        
        # Draw NPCs
        for npc in self.npcs:
            npc.draw_3d(screen)
        
        # Draw player
        self.player.draw_3d(screen)
        
        # Draw UI
        self.draw_ui()
    
    def draw_ui(self):
        # Draw score
        score_text = self.font.render(f"Score: {self.player.score}", True, BLACK)
        screen.blit(score_text, (20, 20))
        
        # Draw ability info
        ability_text = self.small_font.render(f"Ability: {self.player.special_ability}", True, BLACK)
        screen.blit(ability_text, (20, 60))
        
        # Draw instructions
        inst_text = self.small_font.render("Arrow/WASD: Move | Space: Use Ability | E: Interact | P: Pause | R: Select", True, BLACK)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(inst_text, inst_rect)
    
    def draw_pause(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Draw pause text
        pause_text = self.large_font.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(pause_text, pause_rect)
        
        # Draw instructions
        inst_text = self.small_font.render("Press P to Resume", True, WHITE)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        screen.blit(inst_text, inst_rect)
    
    def draw(self):
        if self.state == GameState.CHARACTER_SELECT:
            self.draw_character_select()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.PAUSED:
            self.draw_game()
            self.draw_pause()
        
        pygame.display.flip()

# Main game loop
def main():
    game = Game()
    running = True
    
    while running:
        running = game.handle_events()
        game.update()
        game.draw()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
