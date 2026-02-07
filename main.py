import pygame
import numpy as np
import time

# Constants
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 5
COLS, ROWS = WIDTH // TILE_SIZE, HEIGHT // TILE_SIZE
FILL_PROB = 0.45

# Colors
WALL_COLOR = (40, 40, 40)
FLOOR_COLOR = (200, 200, 200)
REGION_COLOR = (100, 100, 200) # Debug color for regions

class CaveGenerator:
    def __init__(self, cols, rows, fill_prob=0.45):
        self.cols = cols
        self.rows = rows
        self.fill_prob = fill_prob
        self.grid = np.zeros((cols, rows), dtype=int)
        self.reset()
        
    def reset(self):
        """Initialize the grid with random noise."""
        self.grid = np.random.choice(
            [1, 0], 
            size=(self.cols, self.rows), 
            p=[self.fill_prob, 1 - self.fill_prob]
        )
        # Ensure borders are walls
        self.grid[0, :] = 1
        self.grid[-1, :] = 1
        self.grid[:, 0] = 1
        self.grid[:, -1] = 1
        
    def smooth(self):
        """Apply one step of 4-5 Cellular Automata smoothing."""
        new_grid = self.grid.copy()
        for x in range(1, self.cols - 1):
            for y in range(1, self.rows - 1):
                # Count wall neighbors (including self)
                # 3x3 window around x,y
                window = self.grid[x-1:x+2, y-1:y+2]
                walls = np.sum(window)
                
                # Rule: 
                # If a cell is a wall (1), it stays a wall if it has >= 4 wall neighbors (including itself)
                # If a cell is a floor (0), it becomes a wall if it has >= 5 wall neighbors
                
                # Standard 4-5 rule simulation often doesn't count self for the birth rule, 
                # but let's stick to a variation that works well.
                # Common variation: if neighbors > 4 -> wall, else floor.
                
                if walls > 4:
                    new_grid[x, y] = 1
                elif walls < 4:
                    new_grid[x, y] = 0
                
        self.grid = new_grid
        
    def get_regions(self, cell_type=0):
        """Find strictly connected regions of a specific cell type (0 for floor, 1 for wall)."""
        visited = np.zeros_like(self.grid, dtype=bool)
        regions = []
        
        for x in range(self.cols):
            for y in range(self.rows):
                if self.grid[x, y] == cell_type and not visited[x, y]:
                    # Start a new region
                    region = []
                    queue = [(x, y)]
                    visited[x, y] = True
                    
                    while queue:
                        cx, cy = queue.pop(0)
                        region.append((cx, cy))
                        
                        # Check 4 neighbors
                        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < self.cols and 0 <= ny < self.rows:
                                if self.grid[nx, ny] == cell_type and not visited[nx, ny]:
                                    visited[nx, ny] = True
                                    queue.append((nx, ny))
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


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Procedural Cave Generator (Space: Smooth, A: Auto-smooth, R: Reset, F: Filter)")
    
    generator = CaveGenerator(COLS, ROWS, FILL_PROB)
    
    # Pre-generate a surface for drawing to optimize performance
    # Only redraw when grid changes
    surface = pygame.Surface((WIDTH, HEIGHT))
    
    def draw_grid():
        surface.fill(FLOOR_COLOR)
        # Using numpy advanced indexing or iterating efficiently would be better,
        # but for Pygame drawing rectangles is standard.
        # Let's use pixel array for simpler faster rendering if tiles are small,
        # otherwise rects. With TILE_SIZE=5, rects are fine but might be slow if map is huge.
        # Let's stick to rects for clarity unless optimization is requested strictly.
        
        # Optimization: only draw walls
        walls = np.argwhere(generator.grid == 1)
        for x, y in walls:
            pygame.draw.rect(surface, WALL_COLOR, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        
        screen.blit(surface, (0, 0))
    
    dirty = True
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    generator.smooth()
                    dirty = True
                elif event.key == pygame.K_r:
                    generator.reset()
                    dirty = True
                elif event.key == pygame.K_f:
                    generator.prune_small_regions()
                    dirty = True
                elif event.key == pygame.K_a:
                    for _ in range(5):
                        generator.smooth()
                    dirty = True
        
        if dirty:
            draw_grid()
            pygame.display.flip()
            dirty = False
            
    pygame.quit()

if __name__ == "__main__":
    main()