import pygame
import sys
import math
import Cellular_Automata_Project

# Note that there may be an error where the circle is not fully centered around the player

def find_dx_dy(dx1, dy1, L):  # Should scale the dx and dy down to a cover a given "L" or length

    try:
        dy2 = math.sqrt((L ** 2) / (dx1 ** 2 / dy1 ** 2 + 1))
        dx2 = dy2 * dx1 / dy1
    except ZeroDivisionError:  # In case of horizontal case, we re-write the equation
        dx2 = math.sqrt((L ** 2) / (dy1 ** 2 / dx1 ** 2 + 1))
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


class Window():
    def __init__(self, grid, block_w):
        self.grid = grid
        self.block_w = block_w
        self.w = len(grid[0]) * block_w
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

    def __init__(self, x_idx, y_idx, w, h, block_w, radius, grav, frame_cnt, cur_stamina, max_stamina, stamina_cost, stamina_refill_rate):
        self.w = w
        self.h = h
        self.block_w = block_w
        self.radius = radius
        self.bullet_power_lines = 0
        self.x_pos = x_idx * block_w  # Position on the screen (position not index)
        self.y_pos = y_idx * block_w  # Position on the screen (position not index)
        self.grav = grav / frame_cnt  # Acceleration variable (acceleration/sec converted into acceleration/frame)
        self.ax = 0  # Might just remove this later
        self.ay = self.grav  # Acceleration in the y-axis
        self.dx = 0
        self.dy = 0
        self.block_w = block_w
        self.bounce_mag = 0.5  # Interval of how much of the speed is going to be reflected by the wall
        self.stick = False

        self.cur_stamina = cur_stamina
        self.max_stamina = max_stamina
        self.stamina_bar_w = 5
        self.stamina_bar_h = 15
        self.stamina_refill_rate = stamina_refill_rate / frame_cnt
        self.stamina_cost = stamina_cost

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 192, 180), (
        self.x_pos - self.w / 2, self.y_pos - self.h / 2, self.w, self.h))

    def stamina_bar(self, screen):
        if self.stick:
            self.cur_stamina = min(self.max_stamina, self.cur_stamina + self.stamina_refill_rate) # Only regen when still/sticking onto wall

        pygame.draw.rect(screen, (50,150,200), (self.x_pos - 10 - self.stamina_bar_w / 2, self.y_pos - self.stamina_bar_h * self.cur_stamina / self.max_stamina, self.stamina_bar_w, self.stamina_bar_h * self.cur_stamina / self.max_stamina))

    def cursor(self, screen):
        # The idea here is to sorta cheese the system
        # We find the dx and dy and alongside (0,0) as the y_intercept, we get a line formula
        # Note that the line passes the origin which in this case is not the center of the screen but instead the top left
        # We sub the line formula into a x^2 + y^2 = r^2 circle formula which is centered on the origin (Top-left)
        # The 2 variables 2 equations should return the intersection between the circle and line
        # We take this intersection and find its normal (Perpendicular bisector) in the form of a new dx and dy
        # We alter the magnitude of dx and dy to have it cover a given length
        # The end
        mx, my = pygame.mouse.get_pos()
        dx, dy = mx - self.x_pos, my - self.y_pos

        dist = math.sqrt(dx ** 2 + dy ** 2)
        self.bullet_power_lines = min(3, max(1, int(dist // 100))) # Higher the strength_mag, higher the # of lines to show magnitude

        m, y_int = line_formula(dx, dy, 0, 0)
        if [m, y_int] == ["On", "Point"]:  # Handles case where player's position have just recently been altered
            return

        int_1, int_2 = circle_intercept(self.radius, m, y_int)
        dist_1 = math.sqrt(
            (int_1[0] + self.x_pos - mx) ** 2 + (int_1[1] + self.y_pos - my) ** 2)
        dist_2 = math.sqrt(
            (int_2[0] + self.x_pos - mx) ** 2 + (int_2[1] + self.y_pos - my) ** 2)

        # Choose intercept with the shortest length to the mouse
        if dist_1 < dist_2:
            int_x, int_y = int_1
        elif dist_2 < dist_1:
            int_x, int_y = int_2
        else:
            # This case should literally be impossible (Unless radius is 0)
            print("Distance Error")

        dy2, dx2 = -dx, dy

        dx3, dy3 = find_dx_dy(dx2, dy2, 5)

        increment_x, increment_y = find_dx_dy(dx, dy, 10)  # Length can be adjusted
        for i in range(self.bullet_power_lines):
            pygame.draw.aaline(screen, (0, 0, 0), (int_x + self.x_pos - dx3 + increment_x * i,
                                                          int_y + self.y_pos - dy3 + increment_y * i),
                               (int_x + self.x_pos + dx3 + increment_x * i,
                                int_y + self.y_pos + dy3 + increment_y * i))

    def update(self, grid, screen):
        self.cursor(screen)
        if self.stick:
            self.stamina_bar(screen)
            return

        # Basically gr11 physics
        # Velocity will be adjusted "x" amount every second by gravity / x
        self.dy += self.ay
        self.dx += self.ax
        self.collision_detect(grid)
        self.stamina_bar(screen)


    def collision_detect(self, grid):

        # NOTE THAT PREV AND NEW X ARE INDEXES ON THE GRID AND NOT THE COORDINATES OF VARIABLES X AND Y
        # Index of the new position
        new_x = int((self.x_pos + self.dx) // self.block_w)
        new_y = int((self.y_pos + self.dy) // self.block_w)
        # Index of the old/current position
        prev_x = int(self.x_pos // self.block_w)
        prev_y = int(self.y_pos // self.block_w)

        x_flag, y_flag = True, True  # Keeps track if the object has hit a wall (True for no collision)

        if grid[prev_y][new_x]:
            # Collision with wall (x component)
            if new_x > prev_x:
                self.x_pos = new_x * self.block_w - 0.0001  # Needs to be slightly adjusted due to errors raised using "//" or integer division
            elif prev_x > new_x:
                self.x_pos = prev_x * self.block_w

            x_flag = False
            self.stick = True

        if grid[new_y][prev_x]:
            # Collision with wall (y component)
            if new_y > prev_y:
                self.y_pos = new_y * self.block_w - 0.0001
            elif prev_y > new_y:
                self.y_pos = prev_y * self.block_w

            y_flag = False
            self.stick = True

        # If the object has not hit a wall, we simply adjust the position
        if x_flag and y_flag:
            self.x_pos += self.dx
            self.y_pos += self.dy
        else:
            self.dx = 0
            self.dy = 0


def find_angle(dx, dy):  # Converts a dx and dy input into an angle
    dx, dy = dx, dy
    if dx == 0 and dy == 0:
        return 0  # Error since it seems that the line is actually a point
    elif dx == 0:
        if dy > 0:
            return 180
        else:
            return 0
    elif dy == 0:
        if dx > 0:
            return 90
        else:
            return 270
    else:
        if dx > 0:
            if dy > 0:
                agl = 90 + math.degrees(math.atan(abs(dy / dx)))
            elif dy < 0:
                agl = 90 - math.degrees(math.atan(abs(dy / dx)))
        elif dx < 0:
            if dy > 0:
                agl = 270 - math.degrees(math.atan(abs(dy / dx)))
            elif dy < 0:
                agl = 270 + math.degrees(math.atan(abs(dy / dx)))

    return agl


def line_formula(dx, dy, x, y):  # Develops a line equation given slope and a point

    if dx == 0:
        # To avoid ZeroDivisionError, we basically cheese the system by making dx negligible
        if dy < 0:
            m = -10000000000000000
        if dy > 0:
            m = 10000000000000000
        elif dy == 0:
            # Special case where we have just changes the player's position to be on the mouse's position
            # The result is dx = 0 and dy = 0
            # There are infinite normal lines possible so we don't draw anything
            return "On", "Point"
    elif dy == 0:
        m = 0
    else:
        m = dy / dx

    # y = mx + b
    b = y - m * x

    return m, b


def circle_intercept(r, m, y_int):  # Given a line equation and circle equation, find intercepts
    # Combines the formula
    # y = mx + b
    # x^2 + y^2 = r^2

    a = 1 + m ** 2
    b = 2 * m * y_int
    c = b ** 2 - r ** 2

    try:
        # Use quadratic formula to get 2 solutions
        x1 = (-1 * b + math.sqrt(b ** 2 - 4 * a * c)) / (2 * a)
        x2 = (-1 * b - math.sqrt(b ** 2 - 4 * a * c)) / (2 * a)
    except ValueError:
        print("Answer DNE")
        return "Answer", "DNE"

    y1 = m * x1 + y_int
    y2 = m * x2 + y_int

    return [x1, y1], [x2, y2]

screen_block_w = 20
generated_map = Cellular_Automata_Project.Gen_map(screen_block_w, 50, 50, 4, 4, 0.457)
generated_map.construct_everything()
screen = Window(generated_map.map, screen_block_w)
pygame.init()
clock = pygame.time.Clock()
bullets = []
frame_cnt = 70
p_x, p_y = generated_map.find_opening()
p = Player(p_x, p_y, 11, 11, screen.block_w, 20, 4, frame_cnt, 150, 150, 20, 100)

while True:

    screen.draw()
    p.update(screen.grid, screen.screen)
    p.draw(screen.screen)  # Draw player

    # Update objects/bullets
    for bullet in bullets:
        bullet.update(screen.grid)
        bullet.draw(screen.screen)

    # Check inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if p.cur_stamina >= p.stamina_cost * p.bullet_power_lines:  # The player needs to have enough stamina for the jump

                # Sub stamina relative to bullet power lines count
                p.cur_stamina -= p.stamina_cost * p.bullet_power_lines

                mx, my = pygame.mouse.get_pos()
                dx, dy = mx - p.x_pos, my - p.y_pos
                dx, dy = find_dx_dy(dx, dy, p.bullet_power_lines * 2)  # Adjust the integer to adjust magnitude of shot

                p.dx = dx
                p.dy = dy
                p.stick = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                # Adjust player position
                mx, my = pygame.mouse.get_pos()
                p.x_pos = mx
                p.y_pos = my

    pygame.display.update()
    clock.tick(frame_cnt)  # Fps (Don't know why/how it does it)