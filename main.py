import pygame
import numpy as np
import random
import math

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 700 # Increased height for UI
MAP_WIDTH, MAP_HEIGHT = 100, 80
TILE_SIZE = 32 # Visual size of a tile in pixels
FILL_PROB = 0.45
FOV_RADIUS = 8

# Computed
MAP_PIXEL_WIDTH = MAP_WIDTH * TILE_SIZE
MAP_PIXEL_HEIGHT = MAP_HEIGHT * TILE_SIZE

# Colors
WALL_COLOR = (40, 40, 40)
FLOOR_COLOR = (200, 200, 200)
WALL_COLOR_DARK = (20, 20, 20)
FLOOR_COLOR_DARK = (50, 50, 50)
PLAYER_COLOR = (255, 0, 0) # Red player
PLAYER_COLOR = (255, 0, 0) # Red player
GOBLIN_COLOR = (0, 255, 0) # Green goblin
STAIRS_DOWN_COLOR = (255, 255, 0) # Yellow
STAIRS_UP_COLOR = (0, 100, 255) # Blue
UI_BG_COLOR = (30, 30, 30)
UI_HEIGHT = 150
UI_BORDER_COLOR = (100, 100, 100)
TEXT_COLOR = (240, 240, 240)
HP_BAR_RED = (200, 0, 0)
HP_BAR_GREEN = (0, 200, 0)

# Gameplay Settings
# Gameplay Settings
MOVE_DELAY = 150 # Player move cooldown
ENEMY_MOVE_DELAY = 500 # Enemy move speed (slower than player)

# Game States
STATE_START = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2


class Entity:
    def __init__(self, x, y, color, name="Entity", hp=10, ac=10, strength=0):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.ac = ac
        self.strength = strength
        
    def try_move(self, dx, dy, grid, entities):
        """
        Attempt to move. 
        If blocked by wall -> Return False.
        if blocked by entity -> Return Entity (collision).
        if stairs -> Return "stairs".
        If free -> Move and Return True.
        """
        new_x = self.x + dx
        new_y = self.y + dy
        
        # 1. Check Map Boundaries
        if not (0 <= new_x < grid.shape[0] and 0 <= new_y < grid.shape[1]):
            return False
            
        # 2. Check Walls
        if grid[new_x, new_y] == 1:
            return False
            
        if grid[new_x, new_y] == 1:
            return False
            
        # Check Stairs
        if grid[new_x, new_y] == 2:
            return "stairs_down"
        if grid[new_x, new_y] == 3:
            return "stairs_up"
            
        # 3. Check Entities (Collision/Combat)
        for entity in entities:
             if entity is not self and entity.x == new_x and entity.y == new_y:
                 return entity # Return collision entity
        
        # 4. Move
        self.x = new_x
        self.y = new_y
        return True # Return True for successful move

    def attack(self, target, message_log):
        # D&D 5e Style Combat
        # Roll d20 + Str Mod vs AC
        roll = random.randint(1, 20)
        hit_roll = roll + self.strength
        
        # Determine colors
        attacker_color = (255, 100, 100) if self.name == "Goblin" else (100, 255, 100)
        
        log_msg = f"{self.name} attacks {target.name} (AC {target.ac})... Roll: {roll}+{self.strength}={hit_roll}."
        
        if hit_roll >= target.ac:
            # Hit!
            damage = max(1, random.randint(1, 6) + self.strength) # 1d6 + Str
            target.hp -= damage
            message_log.add_message(log_msg + f" HIT for {damage} dmg!", (255, 255, 255))
            if target.hp <= 0:
                 message_log.add_message(f"{target.name} dies!", (200, 50, 50))
        else:
            message_log.add_message(log_msg + " MISS!", (150, 150, 150))

    def draw(self, surface, tile_size, camera):
        # Calculate screen position
        screen_x = self.x * tile_size + camera.x
        screen_y = self.y * tile_size + camera.y
        
        # Only draw if on screen (basic culling)
        if -tile_size <= screen_x < SCREEN_WIDTH and -tile_size <= screen_y < SCREEN_HEIGHT:
            rect = (screen_x, screen_y, tile_size, tile_size)
            pygame.draw.rect(surface, self.color, rect)


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_COLOR, "Player", hp=30, ac=14, strength=3)

class Goblin(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, GOBLIN_COLOR, "Goblin", hp=10, ac=12, strength=1)

    def update(self, player, grid, visible_tiles, entities, message_log):
        # Simple AI:
        # If player is visible to the goblin (in FOV), chase
        # Else wander randomly
        
        dx, dy = 0, 0
        
        # Check if dead
        if self.hp <= 0: return

        if (self.x, self.y) in visible_tiles:
            # Chase player
            if self.x < player.x: dx = 1
            elif self.x > player.x: dx = -1
            
            if self.y < player.y: dy = 1
            elif self.y > player.y: dy = -1
        else:
            # Wander randomly
            direction = random.choice([(0,1), (0,-1), (1,0), (-1,0), (0,0)])
            dx, dy = direction
            
        if dx != 0 or dy != 0:
            result = self.try_move(dx, dy, grid, entities)
            if isinstance(result, Entity): # Collision = Attack
                self.attack(result, message_log)
            # Else moved successfully or blocked by wall




class MessageLog:
    def __init__(self, x, y, width, height, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.messages = [] # List of (text, color)
        
    def add_message(self, text, color=(255, 255, 255)):
        self.messages.append((text, color))
        if len(self.messages) > 10: # Keep last 10 messages
            self.messages.pop(0)
            
    def draw(self, surface):
        # Draw Background
        pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
        pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 2)
        
        # Draw Messages
        line_height = 18
        max_lines = (self.rect.height - 10) // line_height # -10 for padding
        
        # Slice to get only the messages that fit
        visible_messages = self.messages[-max_lines:]
        
        y_offset = 5
        for text, color in visible_messages:
            msg_surf = self.font.render(text, True, color)
            surface.blit(msg_surf, (self.rect.x + 10, self.rect.y + y_offset))
            y_offset += line_height

def draw_health_bar(surface, x, y, current, maximum):
    bar_width = 200
    bar_height = 20
    fill = (current / maximum) * bar_width
    outline_rect = pygame.Rect(x, y, bar_width, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    
    pygame.draw.rect(surface, (60, 60, 60), outline_rect)
    pygame.draw.rect(surface, HP_BAR_GREEN, fill_rect)
    pygame.draw.rect(surface, (255, 255, 255), outline_rect, 2)
    

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        
    def update(self, target):
        # Center camera on target
        # Target position in pixels
        x = -target.x * TILE_SIZE + int(SCREEN_WIDTH / 2)
        y = -target.y * TILE_SIZE + int((SCREEN_HEIGHT - UI_HEIGHT) / 2) # Center in PLAY area (exclude UI)
        
        # Limit scrolling to map size
        # camera_x should be between -(MAP_WIDTH - SCREEN_WIDTH) and 0
        
        x = min(0, x) # Left side
        y = min(0, y) # Top side
        x = max(-(self.width - SCREEN_WIDTH), x) # Right side
        y = max(-(self.height - (SCREEN_HEIGHT - UI_HEIGHT)), y) # Bottom side (Exclude UI)
        
        self.camera = pygame.Rect(x, y, self.width, self.height)
        self.x = x
        self.y = y


class CaveGenerator:
    def __init__(self, cols, rows, fill_prob=0.45):
        self.cols = cols
        self.rows = rows
        self.fill_prob = fill_prob
        self.fill_prob = fill_prob
        self.grid = np.zeros((cols, rows), dtype=int)
        
    def generate(self, level_depth):
        """Initialize the grid with random noise and smooth it automatically."""
        # 1. Random noise
        self.grid = np.random.choice(
            [1, 0], 
            size=(self.cols, self.rows), 
            p=[self.fill_prob, 1 - self.fill_prob]
        )
        
        # 2. Border enforcement
        self.grid[0, :] = 1
        self.grid[-1, :] = 1
        self.grid[:, 0] = 1
        self.grid[:, -1] = 1
        
        # 3. Auto-smooth (5 iterations usually sufficient)
        for _ in range(5):
             self.smooth()
             
        # 4. Prune small disconnected regions to ensure playability
        self.prune_small_regions()

        # 5. Place Stairs
        # Down stairs (2) - Always present efficiently
        down_x, down_y = self.get_random_floor_point()
        self.grid[down_x, down_y] = 2 
        
        # Up stairs (3) - Present if level > 1
        up_x, up_y = None, None
        if level_depth > 1:
            up_x, up_y = self.get_random_floor_point()
            while up_x == down_x and up_y == down_y: # ensure distinct
                 up_x, up_y = self.get_random_floor_point()
            self.grid[up_x, up_y] = 3
        else:
             # Level 1 spawn point logic handled externally or just pick random floor
             up_x, up_y = self.get_random_floor_point() # Just use as spawn
             
        return self.grid.copy(), (up_x, up_y), (down_x, down_y)


        
    def smooth(self):
        """Apply one step of Cellular Automata smoothing using vectorized NumPy operations."""
        # Calculate neighbor counts by shifting the grid
        # Directions: N, S, W, E, NW, NE, SW, SE
        shifts = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        neighbors = np.zeros_like(self.grid, dtype=int)
        for dx, dy in shifts:
            # Shift grid using roll
            shifted = np.roll(self.grid, (dx, dy), axis=(0, 1))
            neighbors += shifted
            
        # Apply rules:
        # Wall (1) stays wall if neighbors >= 4
        # Floor (0) becomes wall if neighbors >= 5
        new_walls = (self.grid == 1) & (neighbors >= 4)
        new_walls |= (self.grid == 0) & (neighbors >= 5)
        
        self.grid[:] = 0
        self.grid[new_walls] = 1
        
        # Enforce borders
        self.grid[0, :] = 1
        self.grid[-1, :] = 1
        self.grid[:, 0] = 1
        self.grid[:, -1] = 1

    def get_random_floor_point(self):
        """Find a random coordinate that is a floor tile."""
        # Get all indices where grid is 0 (floor)
        floor_indices = np.argwhere(self.grid == 0)
        if len(floor_indices) > 0:
            # Randomly select one
            idx = random.randint(0, len(floor_indices) - 1)
            return floor_indices[idx][0], floor_indices[idx][1]
        return self.cols // 2, self.rows // 2 # Fallback
        
    def get_regions(self, cell_type=0):
        """Find strictly connected regions of a specific cell type."""
        visited = np.zeros_like(self.grid, dtype=bool)
        regions = []
        
        for x in range(self.cols):
            for y in range(self.rows):
                if self.grid[x, y] == cell_type and not visited[x, y]:
                    region = []
                    queue = [(x, y)]
                    visited[x, y] = True
                    region.append((x, y))
                    
                    idx = 0
                    while idx < len(queue):
                        cx, cy = queue[idx]
                        idx += 1
                        
                        # Check 4 direct neighbors
                        neighbors = [
                            (cx - 1, cy), (cx + 1, cy), 
                            (cx, cy - 1), (cx, cy + 1)
                        ]
                        
                        for nx, ny in neighbors:
                            if 0 <= nx < self.cols and 0 <= ny < self.rows:
                                if self.grid[nx, ny] == cell_type and not visited[nx, ny]:
                                    visited[nx, ny] = True
                                    queue.append((nx, ny))
                                    region.append((nx, ny))
                    regions.append(region)
        return regions

    def prune_small_regions(self):
        """Remove all floor regions except the largest one."""
        regions = self.get_regions(0)
        if not regions:
            return
            
        # Sort regions by size (largest first)
        regions.sort(key=len, reverse=True)
        
        # Keep the largest, fill others with walls
        for region in regions[1:]:
            for x, y in region:
                self.grid[x, y] = 1

def compute_fov(origin_x, origin_y, radius, grid):
    """Compute visible tiles from origin using basic raycasting."""
    visible = set()
    visible.add((origin_x, origin_y))
    
    # Cast rays to the perimeter of the circle
    for angle in range(0, 360, 3): # Step 3 degrees for coverage
        rad = math.radians(angle)
        dx = math.cos(rad)
        dy = math.sin(rad)
        
        x, y = float(origin_x), float(origin_y)
        
        for _ in range(radius * 2): # Little extra distance to ensure coverage
            x += dx
            y += dy
            
            ix, iy = int(round(x)), int(round(y))
            
            # Bounds check
            if not (0 <= ix < MAP_WIDTH and 0 <= iy < MAP_HEIGHT):
                break
                
            visible.add((ix, iy))
            
            # Stop at wall (blocks sight), but include the wall itself
            if grid[ix, iy] == 1:
                break
                
    return visible




class LevelState:
    def __init__(self, grid, explored_tiles, enemies, up_pos, down_pos):
        self.grid = grid
        self.explored_tiles = explored_tiles
        self.enemies = enemies
        self.up_pos = up_pos
        self.down_pos = down_pos


def draw_text_centered(surface, text, font, color, center_x, center_y):
    render = font.render(text, True, color)
    rect = render.get_rect(center= (center_x, center_y))
    surface.blit(render, rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Cave Explorer")
    
    # UI Fonts
    font = pygame.font.SysFont(None, 24)
    title_font = pygame.font.SysFont(None, 64)
    
    game_state = STATE_START
    show_controls = False
    dungeon_level = 1

    
    generator = CaveGenerator(MAP_WIDTH, MAP_HEIGHT, FILL_PROB)
    
    # Game State Persistence
    levels = {} # depth -> LevelState
    
    # Initialize Level 1
    # Generate new
    grid, spawn_pos, down_pos = generator.generate(1)
    
    player = Player(spawn_pos[0], spawn_pos[1])
    
    enemies = []
    start_x, start_y = spawn_pos
    for _ in range(10): 
        ex, ey = generator.get_random_floor_point()
        while ex == start_x and ey == start_y:
            ex, ey = generator.get_random_floor_point()
        enemies.append(Goblin(ex, ey))
        
    visible_tiles = compute_fov(player.x, player.y, FOV_RADIUS, grid)
    explored_tiles = set(visible_tiles)
    
    # Save Level 1
    levels[1] = LevelState(grid, explored_tiles, enemies, spawn_pos, down_pos)

    
    camera = Camera(MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT)
    
    # UI Setup
    ui_font = pygame.font.SysFont("consolas", 14)
    message_log = MessageLog(10, SCREEN_HEIGHT - 110, SCREEN_WIDTH - 20, 100, ui_font)
    message_log.add_message("Welcome to the Cave! Find the stairs to descend...", (255, 255, 0))

    clock = pygame.time.Clock()
    
    # Exploration tracking
    visible_tiles = set()
    explored_tiles = set()
    
    # Initial FOV
    visible_tiles = compute_fov(player.x, player.y, FOV_RADIUS, generator.grid)
    explored_tiles.update(visible_tiles)

    # Minimap Settings
    show_minimap = True
    MINIMAP_SIZE = (200, 160) # 200x160 pixels (maintains 100:80 ratio)
    minimap_surface = pygame.Surface(MINIMAP_SIZE)
    # Scale factors for minimap
    MM_SCALE_X = MINIMAP_SIZE[0] / MAP_WIDTH
    MM_SCALE_Y = MINIMAP_SIZE[1] / MAP_HEIGHT

    
    last_move_time = 0
    last_enemy_move_time = 0
    
    def render_view(screen, camera, grid, visible, explored, entities):
        # Determine accessible range based on camera
        # Camera X is negative offset. 
        # Screen x=0 corresponds to Map x= -camera.x
        start_col = max(0, int(-camera.x // TILE_SIZE))
        end_col = min(MAP_WIDTH, int((-camera.x + SCREEN_WIDTH) // TILE_SIZE) + 1)
        
        start_row = max(0, int(-camera.y // TILE_SIZE))
        end_row = min(MAP_HEIGHT, int((-camera.y + (SCREEN_HEIGHT - UI_HEIGHT)) // TILE_SIZE) + 1)
        
        screen.fill((0, 0, 0)) # Base black (unexplored)
        
        # We only really need to draw tiles that are Explored
        # Iterating strictly over the view area
        for x in range(start_col, end_col):
            for y in range(start_row, end_row):
                if (x, y) in visible:
                    # Draw Full Color
                    color = WALL_COLOR if grid[x, y] == 1 else FLOOR_COLOR
                    if grid[x, y] == 2: # Stairs Down
                        color = STAIRS_DOWN_COLOR
                    elif grid[x, y] == 3: # Stairs Up
                        color = STAIRS_UP_COLOR
                        
                    rect = (x * TILE_SIZE + camera.x, y * TILE_SIZE + camera.y, TILE_SIZE, TILE_SIZE)
                    # Optimization: draw.rect is fast, but we could batch. This is fine for <500 tiles.
                    pygame.draw.rect(screen, color, rect)
                elif (x, y) in explored:
                    # Draw Dark Color (Fog of War)
                    color = WALL_COLOR_DARK if grid[x, y] == 1 else FLOOR_COLOR_DARK
                    if grid[x, y] == 2: # Stairs seen before
                         color = (100, 100, 0)
                    elif grid[x, y] == 3:
                         color = (0, 50, 100)
                         
                    rect = (x * TILE_SIZE + camera.x, y * TILE_SIZE + camera.y, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, color, rect)
        
        # Draw visible entities
        for entity in entities:
             # Basic visibility check: is entity on a visible tile?
             if (entity.x, entity.y) in visible:
                 entity.draw(screen, TILE_SIZE, camera)

                    
    def update_minimap():
        minimap_surface.fill((0,0,0))
        # Draw all explored tiles
        for (x, y) in explored_tiles:
            color = WALL_COLOR if levels[dungeon_level].grid[x, y] == 1 else FLOOR_COLOR
            # Simple pixel set
            # Rect size
            rect = (x * MM_SCALE_X, y * MM_SCALE_Y, max(1, MM_SCALE_X), max(1, MM_SCALE_Y))
            pygame.draw.rect(minimap_surface, color, rect)
            
    # Initial minimap render
    update_minimap()

    running = True
    
    while running:
        clock.tick(60)
        
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if game_state == STATE_START:
                    if event.key == pygame.K_SPACE:
                        game_state = STATE_PLAYING
                        show_controls = False # Auto hide on start
                
                elif game_state == STATE_GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        # Restart Game
                        # Reset everything
                        dungeon_level = 1
                        levels.clear()
                        
                        grid, spawn_pos, down_pos = generator.generate(1)
                        player.x, player.y = spawn_pos
                        player.hp = player.max_hp
                        
                        enemies = []
                        start_x, start_y = spawn_pos
                        for _ in range(10): 
                            ex, ey = generator.get_random_floor_point()
                            while ex == start_x and ey == start_y:
                                ex, ey = generator.get_random_floor_point()
                            enemies.append(Goblin(ex, ey))
                            
                        visible_tiles = compute_fov(player.x, player.y, FOV_RADIUS, grid)
                        explored_tiles = set(visible_tiles)
                        
                        levels[1] = LevelState(grid, explored_tiles, enemies, spawn_pos, down_pos)
                        
                        update_minimap()
                        
                        game_state = STATE_PLAYING
                
                elif game_state == STATE_PLAYING:
                    if event.key == pygame.K_m:
                        show_minimap = not show_minimap
                    elif event.key == pygame.K_h:
                        show_controls = not show_controls

        
        if game_state == STATE_START:
            screen.fill((0, 0, 0))
            draw_text_centered(screen, "CAVE EXPLORER", title_font, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
            
            controls = [
                "Controls:",
                "Arrow Keys: Move & Attack",
                "M: Toggle Minimap",
                "H: Toggle Controls Popup",
                "",
                "Press SPACE to Start"
            ]
            
            for i, line in enumerate(controls):
                draw_text_centered(screen, line, font, (200, 200, 200), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 30)
                
            pygame.display.flip()
            continue
            
        elif game_state == STATE_GAME_OVER:
            screen.fill((50, 0, 0))
            draw_text_centered(screen, "GAME OVER", title_font, (255, 0, 0), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
            
            draw_text_centered(screen, "You have fallen in the dark...", font, (200, 200, 200), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            draw_text_centered(screen, "Press SPACE to Restart", font, (255, 255, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            
            pygame.display.flip()
            continue

        # --- GAMEPLAY LOGIC (STATE_PLAYING) ---
        
        # Check Player Death
        if player.hp <= 0:
            game_state = STATE_GAME_OVER
        
        # Continuous Input Handling
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        if keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_DOWN]: dy += 1
        if keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_RIGHT]: dx += 1
        
        if dx != 0 or dy != 0:
            current_time = pygame.time.get_ticks()
            if current_time - last_move_time > MOVE_DELAY:
                # Handle diagonal speed? 
                # For now, uniform speed logic
                
                # Pass all entities (enemies + player) to check collision
                all_entities = enemies + [player]
                
                result = player.try_move(dx, dy, levels[dungeon_level].grid, all_entities)
                
                action_taken = False
                if result is True: # Moved
                    action_taken = True
                elif isinstance(result, Entity): # Attacked
                    player.attack(result, message_log)
                    action_taken = True
                
                elif result == "stairs_down":
                    # Save current level state
                    levels[dungeon_level].explored_tiles = explored_tiles.copy()
                    
                    dungeon_level += 1
                    message_log.add_message(f"You descend to level {dungeon_level}...", (255, 255, 0))
                    
                    if dungeon_level in levels:
                        # Load existing level
                        lvl = levels[dungeon_level]
                        grid = lvl.grid
                        explored_tiles = lvl.explored_tiles
                        enemies = lvl.enemies
                        player.x, player.y = lvl.up_pos # Spawn at Up stairs
                    else:
                        # Generate New Level
                        grid, up_pos, down_pos = generator.generate(dungeon_level)
                        
                        # Generate Enemies
                        enemies = []
                        num_enemies = 10 + (dungeon_level * 2)
                        for _ in range(num_enemies): 
                            ex, ey = generator.get_random_floor_point()
                            # Avoid stairs
                            while (ex, ey) == up_pos or (ex, ey) == down_pos:
                                ex, ey = generator.get_random_floor_point()
                                
                            hp = 10 + dungeon_level
                            strength = 1 + (dungeon_level // 3)
                            goblin = Goblin(ex, ey)
                            goblin.hp = hp
                            goblin.max_hp = hp
                            goblin.strength = strength
                            enemies.append(goblin)
                            
                        # Init visited
                        explored_tiles = set()
                        
                        # Save
                        levels[dungeon_level] = LevelState(grid, explored_tiles, enemies, up_pos, down_pos)
                        player.x, player.y = up_pos

                    # Common transition updates
                    visible_tiles = compute_fov(player.x, player.y, FOV_RADIUS, grid)
                    explored_tiles.update(visible_tiles)
                    update_minimap()
                    action_taken = False 

                elif result == "stairs_up":
                    if dungeon_level > 1:
                        # Save current state
                        levels[dungeon_level].explored_tiles = explored_tiles.copy()
                        
                        dungeon_level -= 1
                        message_log.add_message(f"You ascend to level {dungeon_level}...", (0, 100, 255))
                        
                        # Load previous level
                        lvl = levels[dungeon_level]
                        grid = lvl.grid
                        explored_tiles = lvl.explored_tiles
                        enemies = lvl.enemies
                        player.x, player.y = lvl.down_pos # Spawn at Down stairs
                        
                         # Common transition updates
                        visible_tiles = compute_fov(player.x, player.y, FOV_RADIUS, grid)
                        explored_tiles.update(visible_tiles)
                        update_minimap()
                        action_taken = False
                    else:
                        message_log.add_message("You cannot leave the cave yet!", (150, 150, 150))

                
                if action_taken:
                    last_move_time = current_time
                    # Update FOV
                    visible_tiles = compute_fov(player.x, player.y, FOV_RADIUS, grid)
                    explored_tiles.update(visible_tiles)
                    # Update minimap
                    update_minimap()

        # Update Enemies independent of player input
        current_time = pygame.time.get_ticks()
        if current_time - last_enemy_move_time > ENEMY_MOVE_DELAY:
            # Clean up dead enemies (on current level)
            active_enemies = [e for e in enemies if e.hp > 0]
            enemies = active_enemies # Update local ref
            levels[dungeon_level].enemies = active_enemies # Update persistent ref
            
            all_entities = enemies + [player]
            
            for enemy in enemies:
                enemy.update(player, grid, visible_tiles, all_entities, message_log)
            last_enemy_move_time = current_time

        # Update Camera
        camera.update(player)
        
        # Drawing
        render_view(screen, camera, grid, visible_tiles, explored_tiles, enemies + [player])
        
        # Draw UI
        pygame.draw.rect(screen, (10, 10, 10), (0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 150)) # Sidebar BG
        message_log.draw(screen)
        
        # Health Bar
        draw_health_bar(screen, 10, SCREEN_HEIGHT - 140, player.hp, player.max_hp)
        hp_text = font.render(f"HP: {player.hp}/{player.max_hp} | Lvl: {dungeon_level}", True, (255, 255, 255))
        screen.blit(hp_text, (220, SCREEN_HEIGHT - 140))


        
        if show_minimap:
            # Draw border
            border_rect = (SCREEN_WIDTH - MINIMAP_SIZE[0] - 10, 10, MINIMAP_SIZE[0] + 2, MINIMAP_SIZE[1] + 2)
            pygame.draw.rect(screen, (255, 255, 255), border_rect, 1)
            
            # Blit minimap
            minimap_pos = (SCREEN_WIDTH - MINIMAP_SIZE[0] - 9, 11)
            screen.blit(minimap_surface, minimap_pos)
            
            # Draw player on minimap
            mx = int(player.x / MAP_WIDTH * MINIMAP_SIZE[0])
            my = int(player.y / MAP_HEIGHT * MINIMAP_SIZE[1])
            pygame.draw.rect(screen, PLAYER_COLOR, (minimap_pos[0] + mx, minimap_pos[1] + my, 3, 3))
            
        # Draw Controls Popup
        if show_controls:
            popup_lines = [
                "Controls:",
                "Arrows: Move/Attack",
                "M: Minimap",
                "H: Toggle this menu"
            ]
            
            # Calculate size
            popup_width = 200
            popup_height = len(popup_lines) * 25 + 20
            popup_x = SCREEN_WIDTH // 2 - popup_width // 2
            popup_y = SCREEN_HEIGHT // 2 - popup_height // 2
            
            # Draw Popup Background
            pygame.draw.rect(screen, (0, 0, 0), (popup_x, popup_y, popup_width, popup_height))
            pygame.draw.rect(screen, (255, 255, 255), (popup_x, popup_y, popup_width, popup_height), 2)
            
            for i, line in enumerate(popup_lines):
                 line_surf = font.render(line, True, (255, 255, 255))
                 screen.blit(line_surf, (popup_x + 10, popup_y + 10 + i * 25))
        
        pygame.display.flip()
            
    pygame.quit()

if __name__ == "__main__":
    main()