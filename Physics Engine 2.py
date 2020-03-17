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


class Bullet:
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
        self.bounce_mag = 0.35


    def draw(self, screen):
        pygame.draw.rect(screen, (0,0,0), (self.x_pos - self.w/2, self.y_pos - self.h/2, self.w, self.h))

    def update(self, screen, grid):
        if self.dead: return  # Object is dead a.k.a not moving and therefore no movement checks are needed

        self.dy += self.ay
        self.dx += self.ax
        self.collision_detect(grid)

    def collision_detect(self, grid):

        # NOTE THAT PREV AND NEW X ARE INDEXES ON THE GRID AND NOT THE COORDINATES OF VARIABLES X AND Y
        new_x = int((self.x_pos + self.dx) // self.block_w)
        new_y = int((self.y_pos + self.dy) // self.block_w)
        prev_x = int(self.x_pos // self.block_w)
        prev_y = int(self.y_pos // self.block_w)

        x_flag, y_flag = True, True

        if grid[prev_y][new_x]:
            # Collision with wall (x component)
            if new_x > prev_x:
                x_flag = False
                self.x_pos = new_x * self.block_w - 0.0001  # Needs to be slightly adjusted due to errors raised using "//" or integer division
            elif prev_x > new_x:
                x_flag = False
                self.x_pos = prev_x * self.block_w

            self.dx = -1 * self.dx * self.bounce_mag

        if grid[new_y][prev_x]:
            # Collision with wall (y component)
            if new_y > prev_y:
                y_flag = False

                if self.dx > 0:
                    self.dx -= 0.09
                elif self.dx < 0:
                    self.dx += 0.09

                # Special case for friction and dragging on floor
                if abs(self.dx) < 0.05: self.dx = 0  # If the object is join slow enough, we simply stop it
                # (Do this to prevent from accelerating in negative direction
                # instead of stopping)

                if abs(self.dy) < 0.05: self.dy = 0  # If the object is join slow enough, we simply stop it
                # (Do this to prevent from accelerating in negative direction
                # instead of stopping)

                if abs(self.dy) == 0 and abs(self.dx) == 0:
                    self.dead = True

            elif prev_y > new_y:
                y_flag = False
                self.y_pos = prev_y * self.block_w

            self.dy = -1 * self.dy * self.bounce_mag

        if x_flag: self.x_pos += self.dx
        if y_flag: self.y_pos += self.dy


class Window():
    def __init__(self, grid, block_w):
        self.grid = grid
        self.block_w = block_w
        self.w = len(grid[0] * block_w)
        self.h = len(grid) * block_w
        self.width = len(grid[0]) * block_w
        self.height = len(grid) * block_w
        self.screen = pygame.display.set_mode((self.w, self.h))

    def draw(self):
        self.screen.fill((255, 255, 255))

        y_pos = 0
        for y in range(len(self.grid)):
            x_pos = 0
            for x in range(len(self.grid[0])):
                sqr = self.grid[y][x]
                if sqr:
                    pygame.draw.rect(self.screen, (150, 150, 150), (x_pos, y_pos, self.block_w, self.block_w))
                x_pos += self.block_w
            y_pos += self.block_w



class Player:

    def __init__(self, x_idx, y_idx, w, h, block_w):
        self.x_idx = x_idx
        self.y_idx = y_idx
        self.w = w
        self.h = h
        self.block_w = block_w


    def draw(self, screen):
        pygame.draw.rect(screen, (255,192,180), (self.x_idx * self.block_w - self.w/2, self.y_idx * self.block_w - self.h/2, self.w, self.h))


screen = Window([[1,1,1,1,1,1,1,1,1,1,1],
                 [1,0,0,0,0,0,0,0,1,0,1],
                 [1,0,0,0,0,0,0,0,0,0,1],
                 [1,0,0,0,0,1,1,0,1,0,1],
                 [1,0,0,0,1,1,0,1,0,0,1],
                 [1,0,0,0,0,0,0,0,0,0,1],
                 [1,1,1,1,1,1,1,1,1,1,1]], 75)
pygame.init()
clock = pygame.time.Clock()
bullets = []
p = Player(2, 2, 11, 11, screen.block_w)

while True:
    screen.draw()
    p.draw(screen.screen)

    # Check inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            dx, dy = mx - p.x_idx * screen.block_w, my - p.y_idx * screen.block_w
            dx, dy = find_dx_dy(dx, dy, 7)  # Adjust the integer to adjust magnitude of shot
            bullets.append(Bullet(p.x_idx, p.y_idx, 10, 10, 5, dx, dy, 70, screen.block_w))

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                mx, my = pygame.mouse.get_pos()
                p.x_idx = mx / screen.block_w
                p.y_idx = my / screen.block_w


    for bullet in bullets:
        bullet.update(screen, screen.grid)
        bullet.draw(screen.screen)

    pygame.display.update()
    clock.tick(70)  # Fps (Don't know why/how it does it)