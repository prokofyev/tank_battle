import pygame
import os
import math


class Projectile:
    def __init__(self, x, y, angle, tank_speed, body_angle, speed=5):
        self.position = pygame.math.Vector2(x, y)
        self.angle = angle
        self.speed = speed
        
        # Add tank's velocity to projectile
        radians = math.radians(-angle) 
        tank_radians = math.radians(-body_angle) 
        self.velocity = pygame.math.Vector2(
            speed  * math.cos(radians),
            speed  * math.sin(radians)
        ) + pygame.math.Vector2(
            tank_speed * math.cos(tank_radians),
            tank_speed * math.sin(tank_radians)
        )
        
        self.distance_traveled = 0
        self.max_distance = 500

        self.image = pygame.image.load(os.path.join('img', 'shell.png'))
        self.image = pygame.transform.flip(self.image, flip_x=False, flip_y=True)
        self.image = pygame.transform.scale(self.image, 
            (int(self.image.get_width() * 0.1), int(self.image.get_height() * 0.1)))

    def update(self):
        self.position += self.velocity
        self.distance_traveled += self.velocity.length()
        return self.distance_traveled <= self.max_distance

    def draw(self, screen):
        rotated_shell = pygame.transform.rotate(self.image, self.angle + 90)
        shell_rect = rotated_shell.get_rect(center=self.position)
        screen.blit(rotated_shell, shell_rect)
