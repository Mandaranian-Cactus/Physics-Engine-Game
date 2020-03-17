import pygame
import sys
import math

def find_dx_dy(dx1, dy1, L):  # Should scale the dx and dy down to a cover a given "L" or length

    # dx1 = 0
    try:
        dy2 = math.sqrt((L **2) / (dx1 ** 2 / dy1 ** 2 + 1))
        dx2 = dy2 * dx1 / dy1
    except ZeroDivisionError: # In case of horizontal case, we re-write the equation
        dx2 = math.sqrt((L **2) / (dy1 ** 2 / dx1 ** 2 + 1))
        dy2 = dx2 * dy1 / dx1

    if dx1 < 0:
        dx2 = abs(dx2) * -1
    elif dx1 > 0:
        dx2 = abs(dx2)

    if dy1 < 0:
        dy2 = abs(dy2) * -1
    elif dy1 > 0:
        dy2 = abs(dy2)

    return dx2, dy2

class Window:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.screen = pygame.display.set_mode((self.w, self.h))

    def fill(self):
        self.screen.fill((255, 255, 255))


class Player:
    def __init__(self, x_idx, y_idx, w, h, grav, dx, dy, frame_cnt, block_w):
        self.x_idx = x_idx
        self.y_idx = y_idx
        self.x_pos = x_idx * block_w
        self.y_pos = y_idx * block_w
        self.w = w
        self.h = h
        self.grav = grav / frame_cnt # Acceleration variable (acceleration/sec converted into acceleration/frame)
        self.ax = 0  # Might just remove this later
        self.ay = self.grav  # Acceleration in the y-axis
        self.dx = dx
        self.dy = dy
        self.dead = False  # States whether the object is moving or not (Used to optimize and ignore updating position)
        self.block_w = block_w


    def draw(self, screen):
        pygame.draw.rect(screen, (0,0,0), (self.x_pos - self.w/2, self.y_pos - self.h/2, self.w, self.h))

    def update(self, screen):

        if self.dead: return  # Object is dead a.k.a not moving and therefore no movement checks are needed

        self.dy += self.ay
        self.y_pos += self.dy
        self.dx += self.ax
        self.x_pos += self.dx
        self.border_check(screen.h, screen.w)

    def border_check(self, screen_h, screen_w):

        if self.y_pos > screen_h:
            self.y_pos = screen_h
            self.dy = -1 * self.dy * 0.6

            if self.dx > 0: self.dx -= 0.007
            elif self.dx < 0: self.dx += 0.007

            # Special case for friction and dragging on floor
            if abs(self.dx) < 0.05: self.dx = 0  # If the object is join slow enough, we simply stop it
                                                # (Do this to prevent from accelerating in negative direction
                                                # instead of stopping)

            if abs(self.dy) < 0.05: self.dy = 0  # If the object is join slow enough, we simply stop it
                                                # (Do this to prevent from accelerating in negative direction
                                                # instead of stopping)

            if abs(self.dy) < 0.05 and abs(self.dx) < 0.05:
                self.dead = True


        elif self.y_pos < 0:
            self.y_pos = 0
            self.dy = -1 * self.dy * 0.6
        if self.x_pos > screen_w:
            self.x_pos = screen_w
            self.dx = -1 * self.dx * 0.6
        elif self.x_pos < 0:
            self.x_pos = 0
            self.dx = -1 * self.dx * 0.6

class Grid():
    def __init__(self, grid, w):
        self.grid = grid
        self.w = w
        self.width = len(grid[0]) * w
        self.height = len(grid) * w

    def draw(self, screen):
        y_pos = 0
        for y in range(len(self.grid)):
            x_pos = 0
            for x in range(len(self.grid[0])):
                sqr = self.grid[y][x]
                if sqr:
                    pygame.draw.rect(screen, (150, 150, 150), (x_pos, y_pos, self.w, self.w))
                x_pos += self.w
            y_pos += self.w


screen = Window(700, 500)
pygame.init()
clock = pygame.time.Clock()
players = []

while True:
    screen.fill()

    # Check inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            dx, dy = mx - 4 * 50, my - 4 * 50 # Really iffy code here (Very fragile)
            dx, dy = find_dx_dy(dx, dy, 10)
            players.append(Player(4, 4, 10, 10, 4, dx, dy, 70, 50))

    # pygame.draw.rect(screen.screen, (0,0,0), (screen.w/2, screen.h/2, 5, 5))
    for player in players:
        player.update(screen)
        player.draw(screen.screen)

    pygame.display.update()
    clock.tick(70)  # Fps (Don't know why/how it does it)