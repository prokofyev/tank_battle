import pygame
import os
import math

def init_game():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()
    pygame.display.set_caption("Tank Battle")
    return screen, WINDOW_WIDTH, WINDOW_HEIGHT

class TankMovement:
    def __init__(self):
        self.current_speed = 0
        self.max_speed = 3
        self.acceleration = 0.1
        self.deceleration = 0.05
        self.x = 0.0  # Float position X
        self.y = 0.0  # Float position Y

def load_tank():
    tank_image = pygame.image.load(os.path.join('img', 'tank.png'))
    tank_image = pygame.transform.scale(tank_image, 
        (int(tank_image.get_width() * 0.4), int(tank_image.get_height() * 0.4)))
    tank_rect = tank_image.get_rect()
    return tank_image, tank_rect

def handle_input(keys, angle, tank_rect, tank_movement):
    if keys[pygame.K_ESCAPE]:
        return False, angle
    
    if keys[pygame.K_LEFT]:
        angle += 1.5
    if keys[pygame.K_RIGHT]:
        angle -= 1.5
    
    # Acceleration and movement using float positions
    if keys[pygame.K_UP]:
        tank_movement.current_speed = min(tank_movement.current_speed + tank_movement.acceleration, 
                                        tank_movement.max_speed)
    elif keys[pygame.K_DOWN]:
        tank_movement.current_speed = max(tank_movement.current_speed - tank_movement.acceleration, 
                                        -tank_movement.max_speed)
    else:
        if tank_movement.current_speed > 0:
            tank_movement.current_speed = max(0, tank_movement.current_speed - tank_movement.deceleration)
        elif tank_movement.current_speed < 0:
            tank_movement.current_speed = min(0, tank_movement.current_speed + tank_movement.deceleration)

    if tank_movement.current_speed != 0:
        radians = math.radians(-angle)
        tank_movement.x += tank_movement.current_speed * math.cos(radians)
        tank_movement.y += tank_movement.current_speed * math.sin(radians)
        tank_rect.center = (round(tank_movement.x), round(tank_movement.y))
    
    return True, angle

def handle_screen_wrap(tank_rect, WINDOW_WIDTH, WINDOW_HEIGHT, tank_movement):
    if tank_movement.x > WINDOW_WIDTH:
        tank_movement.x = 0
    elif tank_movement.x < 0:
        tank_movement.x = WINDOW_WIDTH
    if tank_movement.y > WINDOW_HEIGHT:
        tank_movement.y = 0
    elif tank_movement.y < 0:
        tank_movement.y = WINDOW_HEIGHT
    tank_rect.center = (round(tank_movement.x), round(tank_movement.y))

def draw_tank(screen, tank_image, tank_rect, angle):
    screen.fill((0, 0, 0))
    rotated_tank = pygame.transform.rotate(tank_image, angle)
    rotated_rect = rotated_tank.get_rect(center=tank_rect.center)
    screen.blit(rotated_tank, rotated_rect)
    pygame.display.flip()

def main():
    screen, WINDOW_WIDTH, WINDOW_HEIGHT = init_game()
    tank_image, tank_rect = load_tank()
    tank_movement = TankMovement()
    # Initialize float positions to screen center
    tank_movement.x = WINDOW_WIDTH // 2
    tank_movement.y = WINDOW_HEIGHT // 2
    tank_rect.center = (round(tank_movement.x), round(tank_movement.y))
    angle = 0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        running, angle = handle_input(keys, angle, tank_rect, tank_movement)
        handle_screen_wrap(tank_rect, WINDOW_WIDTH, WINDOW_HEIGHT, tank_movement)
        draw_tank(screen, tank_image, tank_rect, angle)
    
    pygame.quit()

if __name__ == "__main__":
    main()