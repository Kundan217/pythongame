import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 60

# Colors
BACKGROUND = (15, 20, 30)
GRID_COLOR = (30, 40, 60)
SNAKE_COLOR = (0, 200, 100)
FOOD_COLOR = (220, 60, 60)
TEXT_COLOR = (220, 220, 220)
UI_BG = (40, 50, 70, 200)  # Semi-transparent

# Difficulty settings (speed in frames per move)
DIFFICULTIES = {
    "slow": 10,
    "fast": 6,
    "very fast": 3
}

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.grow_pending = 2  # Start with 3 segments
        
    def update_direction(self):
        self.direction = self.next_direction
    
    def move(self):
        head_x, head_y = self.positions[0]
        dx, dy = self.direction
        new_x = (head_x + dx) % GRID_WIDTH
        new_y = (head_y + dy) % GRID_HEIGHT
        new_head = (new_x, new_y)
        
        # Check for collision with self
        if new_head in self.positions:
            return False
        
        self.positions.insert(0, new_head)
        
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.positions.pop()
            
        return True
    
    def grow(self):
        self.grow_pending += 1
        self.length += 1
    
    def change_direction(self, direction):
        # Prevent 180-degree turns
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.next_direction = direction
    
    def draw(self, screen):
        for i, (x, y) in enumerate(self.positions):
            # Create a gradient effect from head to tail
            color_factor = max(0.3, 1.0 - (i / self.length) * 0.7)
            color = (
                int(SNAKE_COLOR[0] * color_factor),
                int(SNAKE_COLOR[1] * color_factor),
                int(SNAKE_COLOR[2] * color_factor)
            )
            
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 150, 70), rect, 1)  # Border
            
            # Draw eyes on the head
            if i == 0:
                # Determine eye positions based on direction
                eye_size = GRID_SIZE // 5
                if self.direction == RIGHT:
                    left_eye = (rect.right - eye_size - 2, rect.top + eye_size * 2)
                    right_eye = (rect.right - eye_size - 2, rect.bottom - eye_size * 3)
                elif self.direction == LEFT:
                    left_eye = (rect.left + 2, rect.top + eye_size * 2)
                    right_eye = (rect.left + 2, rect.bottom - eye_size * 3)
                elif self.direction == UP:
                    left_eye = (rect.left + eye_size * 2, rect.top + 2)
                    right_eye = (rect.right - eye_size * 3, rect.top + 2)
                else:  # DOWN
                    left_eye = (rect.left + eye_size * 2, rect.bottom - 2 - eye_size)
                    right_eye = (rect.right - eye_size * 3, rect.bottom - 2 - eye_size)
                
                pygame.draw.circle(screen, (255, 255, 255), left_eye, eye_size)
                pygame.draw.circle(screen, (255, 255, 255), right_eye, eye_size)
                pygame.draw.circle(screen, (0, 0, 0), left_eye, eye_size // 2)
                pygame.draw.circle(screen, (0, 0, 0), right_eye, eye_size // 2)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position([])
    
    def randomize_position(self, snake_positions):
        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if self.position not in snake_positions:
                break
    
    def draw(self, screen):
        x, y = self.position
        rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, FOOD_COLOR, rect)
        pygame.draw.rect(screen, (180, 40, 40), rect, 1)  # Border
        
        # Draw a little shine effect
        shine_rect = pygame.Rect(
            x * GRID_SIZE + GRID_SIZE // 4,
            y * GRID_SIZE + GRID_SIZE // 4,
            GRID_SIZE // 4,
            GRID_SIZE // 4
        )
        pygame.draw.ellipse(screen, (255, 200, 200), shine_rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Simple Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 20)
        self.large_font = pygame.font.SysFont('Arial', 48, bold=True)
        
        self.snake = Snake()
        self.food = Food()
        self.food.randomize_position(self.snake.positions)
        
        self.score = 0
        self.game_over = False
        self.difficulty = "slow"
        self.speed_counter = 0
        self.menu_mode = True
    
    def draw_grid(self):
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WIDTH, y), 1)
    
    def draw_ui(self):
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))
        
        # Draw difficulty
        diff_text = self.font.render(f"Difficulty: {self.difficulty}", True, TEXT_COLOR)
        self.screen.blit(diff_text, (10, 40))
        
        # Draw length
        length_text = self.font.render(f"Length: {self.snake.length}", True, TEXT_COLOR)
        self.screen.blit(length_text, (10, 70))
        
        # Draw controls info
        controls = [
            "CONTROLS:",
            "Arrow Keys - Move Snake",
            "R - Restart Game",
            "ESC - Return to Menu",
            "1, 2, 3 - Change Difficulty"
        ]
        
        # Draw semi-transparent background for controls
        controls_bg = pygame.Rect(WIDTH - 210, 10, 200, 140)
        pygame.draw.rect(self.screen, UI_BG, controls_bg)
        pygame.draw.rect(self.screen, (80, 100, 140), controls_bg, 2)
        
        for i, text in enumerate(controls):
            control_text = self.small_font.render(text, True, TEXT_COLOR)
            self.screen.blit(control_text, (WIDTH - 200, 15 + i * 25))
    
    def draw_menu(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Draw title
        title = self.large_font.render("SNAKE GAME", True, (0, 220, 120))
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4))
        self.screen.blit(title, title_rect)
        
        # Draw difficulty options
        difficulties = ["SLOW", "FAST", "VERY FAST"]
        colors = [(0, 180, 80), (220, 160, 0), (220, 60, 60)]
        
        for i, (diff, color) in enumerate(zip(difficulties, colors)):
            button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 50 + i*80, 200, 60)
            
            # Highlight selected difficulty
            if diff.lower() == self.difficulty:
                pygame.draw.rect(self.screen, color, button_rect)
                pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 3)
            else:
                pygame.draw.rect(self.screen, (40, 50, 70), button_rect)
                pygame.draw.rect(self.screen, color, button_rect, 3)
            
            diff_text = self.font.render(diff, True, TEXT_COLOR)
            text_rect = diff_text.get_rect(center=button_rect.center)
            self.screen.blit(diff_text, text_rect)
        
        # Draw start instruction
        start_text = self.font.render("Press SPACE to Start", True, TEXT_COLOR)
        start_rect = start_text.get_rect(center=(WIDTH//2, HEIGHT - 100))
        self.screen.blit(start_text, start_rect)
        
        # Draw controls hint
        hint_text = self.small_font.render("Or press 1, 2, 3 to select difficulty and start", True, TEXT_COLOR)
        hint_rect = hint_text.get_rect(center=(WIDTH//2, HEIGHT - 60))
        self.screen.blit(hint_text, hint_rect)
    
    def draw_game_over(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over_text = self.large_font.render("GAME OVER", True, (220, 60, 60))
        game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//3))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Draw score
        score_text = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(score_text, score_rect)
        
        # Draw restart instruction
        restart_text = self.font.render("Press R to Restart or ESC for Menu", True, TEXT_COLOR)
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT - 100))
        self.screen.blit(restart_text, restart_rect)
    
    def reset_game(self):
        self.snake.reset()
        self.food.randomize_position(self.snake.positions)
        self.score = 0
        self.game_over = False
        self.speed_counter = 0
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if self.menu_mode:
                    if event.key == pygame.K_SPACE:
                        self.menu_mode = False
                    elif event.key in (pygame.K_1, pygame.K_KP1):
                        self.difficulty = "slow"
                        self.menu_mode = False
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        self.difficulty = "fast"
                        self.menu_mode = False
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        self.difficulty = "very fast"
                        self.menu_mode = False
                
                elif self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.menu_mode = True
                        self.game_over = False
                
                else:  # Game is running
                    if event.key == pygame.K_UP:
                        self.snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction(RIGHT)
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.menu_mode = True
                    elif event.key in (pygame.K_1, pygame.K_KP1):
                        self.difficulty = "slow"
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        self.difficulty = "fast"
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        self.difficulty = "very fast"
    
    def update(self):
        if self.menu_mode or self.game_over:
            return
        
        # Update snake direction
        self.snake.update_direction()
        
        # Move snake based on difficulty speed
        self.speed_counter += 1
        if self.speed_counter >= DIFFICULTIES[self.difficulty]:
            self.speed_counter = 0
            if not self.snake.move():
                self.game_over = True
                return
            
            # Check if snake ate food
            if self.snake.positions[0] == self.food.position:
                self.snake.grow()
                self.score += 10
                self.food.randomize_position(self.snake.positions)
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            
            # Draw everything
            self.screen.fill(BACKGROUND)
            self.draw_grid()
            
            if not self.menu_mode and not self.game_over:
                self.snake.draw(self.screen)
                self.food.draw(self.screen)
                self.draw_ui()
            elif self.game_over:
                self.snake.draw(self.screen)
                self.food.draw(self.screen)
                self.draw_ui()
                self.draw_game_over()
            else:
                self.draw_menu()
            
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()