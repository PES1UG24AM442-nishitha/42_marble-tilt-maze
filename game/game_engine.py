import pygame
from .marble import Marble
from .wall import Wall

# Game Engine

WHITE = (255, 255, 255)
DARK = (40, 40, 50)
WALL_COLOR = (90, 90, 110)
GOAL_COLOR = (60, 200, 120)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.marble = Marble(50, 50)
        self.tilt_strength = 0.6
        self.friction = 0.02
        self.max_speed = 9

        self.walls = self._build_maze()
        self.goal_x, self.goal_y, self.goal_radius = width - 60, height - 60, 22

        self.time_limit_ms = 45000
        self.start_ticks = pygame.time.get_ticks()

        self.font = pygame.font.SysFont("Arial", 26)
        self.game_over = False
        self.result = None  # "solved" or "timeout"
        self.finish_time_ms = None

    def _build_maze(self):
        walls = []
        t = 16  # wall thickness

        # outer boundary
        walls.append(Wall(0, 0, self.width, t))
        walls.append(Wall(0, self.height - t, self.width, t))
        walls.append(Wall(0, 0, t, self.height))
        walls.append(Wall(self.width - t, 0, t, self.height))

        # a few internal walls forming a simple winding path
        walls.append(Wall(0, 140, self.width - 140, t))
        walls.append(Wall(140, 260, self.width - 140, t))
        walls.append(Wall(0, 380, self.width - 140, t))

        return walls

    def handle_event(self, event):
        if self.game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.reset(easy=True)
            elif event.key == pygame.K_2:
                self.reset(med=True)
            elif event.key == pygame.K_3:
                self.reset(hard=True)

    def reset(self, easy=False, med=False, hard=False):
        self.marble.x, self.marble.y = 50, 50
        self.marble.vx, self.marble.vy = 0, 0
        self.game_over = False
        self.result = None
        self.start_ticks = pygame.time.get_ticks()
        
        if easy:
            self.tilt_strength, self.friction, self.time_limit_ms = 0.8, 0.04, 60000
        elif med:
            self.tilt_strength, self.friction, self.time_limit_ms = 0.6, 0.02, 45000
        elif hard:
            self.tilt_strength, self.friction, self.time_limit_ms = 0.4, 0.01, 30000

    def handle_input(self):
        if self.game_over:
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - self.width // 2
        dy = mouse_y - self.height // 2
        dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        ax = (dx / dist) * self.tilt_strength
        ay = (dy / dist) * self.tilt_strength
        self.marble.vx += ax
        self.marble.vy += ay

    def update(self):
        if self.game_over:
            return

        elapsed = pygame.time.get_ticks() - self.start_ticks
        if elapsed >= self.time_limit_ms:
            self.game_over = True
            self.result = "timeout"
            return

        self.marble.vx *= (1 - self.friction)
        self.marble.vy *= (1 - self.friction)

        speed = (self.marble.vx ** 2 + self.marble.vy ** 2) ** 0.5
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.marble.vx *= scale
            self.marble.vy *= scale

        self.marble.x += self.marble.vx
        self.marble.y += self.marble.vy

        self._resolve_wall_collisions()

        gx = self.goal_x - self.marble.x
        gy = self.goal_y - self.marble.y
        if (gx ** 2 + gy ** 2) ** 0.5 <= self.goal_radius:
            self.game_over = True
            self.result = "solved"
            self.finish_time_ms = elapsed

def _resolve_wall_collisions(self):
        for wall in self.walls:
            wall_rect = wall.rect()
            
            # Find the closest point on the rectangle to the circle's center
            closest_x = max(wall_rect.left, min(self.marble.x, wall_rect.right))
            closest_y = max(wall_rect.top, min(self.marble.y, wall_rect.bottom))
            
            # Calculate distance between center and the closest point
            dx = self.marble.x - closest_x
            dy = self.marble.y - closest_y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            if distance < self.marble.radius:
                if distance == 0: # Prevent division by zero
                    dx, dy, distance = 1, 0, 1
                    
                overlap = self.marble.radius - distance
                self.marble.x += (dx / distance) * overlap
                self.marble.y += (dy / distance) * overlap
                
                # Reflect velocity
                if closest_x == wall_rect.left or closest_x == wall_rect.right:
                    self.marble.vx *= -0.3
                else:
                    self.marble.vy *= -0.3

    def render(self, screen):
        screen.fill(DARK)

        for wall in self.walls:
            pygame.draw.rect(screen, WALL_COLOR, wall.rect())

        pygame.draw.circle(screen, GOAL_COLOR, (self.goal_x, self.goal_y), self.goal_radius)
        pygame.draw.circle(screen, WHITE, (int(self.marble.x), int(self.marble.y)), self.marble.radius)

        elapsed = pygame.time.get_ticks() - self.start_ticks
        seconds_left = max(0, (self.time_limit_ms - elapsed) // 1000)
        timer_text = self.font.render(f"Time: {seconds_left}s", True, WHITE)
        screen.blit(timer_text, (10, 10))

        # NEW GAME OVER BLOCK
        if self.game_over:
            # 1. Semi-transparent overlay
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # 2. Main Game Over Message
            if self.result == "solved":
                msg = f"Solved in {self.finish_time_ms / 1000:.1f}s!"
                color = GOAL_COLOR
            else:
                msg = "Time's up!"
                color = (255, 100, 100)
                
            text = self.font.render(msg, True, color)
            screen.blit(text, (self.width // 2 - text.get_width() // 2, self.height // 2 - 20))
            
            # 3. Replay instructions
            replay_text = self.font.render("Press 1 (Easy), 2 (Med), 3 (Hard) to Replay", True, WHITE)
            screen.blit(replay_text, (self.width // 2 - replay_text.get_width() // 2, self.height // 2 + 20))