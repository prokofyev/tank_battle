import pygame
import os
import math
from pygame.math import Vector2

class Projectile:
    SHELL_SCALE = 0.1
    MAX_DISTANCE = 500

    def __init__(self, x, y, angle, tank_speed, body_angle, speed=5):
        self.position = Vector2(x, y)
        self.angle = angle
        self.distance_traveled = 0
        self.velocity = self._calculate_velocity(angle, speed, body_angle, tank_speed)
        self.image = self._load_shell_image()

    def _calculate_velocity(self, angle, speed, body_angle, tank_speed):
        # Calculate shell velocity
        radians = math.radians(-angle)
        shell_velocity = Vector2(
            speed * math.cos(radians),
            speed * math.sin(radians)
        )
        
        # Add tank velocity
        tank_radians = math.radians(-body_angle)
        tank_velocity = Vector2(
            tank_speed * math.cos(tank_radians),
            tank_speed * math.sin(tank_radians)
        )
        
        return shell_velocity + tank_velocity

    def _load_shell_image(self):
        image = pygame.image.load(os.path.join('img', 'shell.png'))
        image = pygame.transform.flip(image, flip_x=False, flip_y=True)
        width = int(image.get_width() * self.SHELL_SCALE)
        height = int(image.get_height() * self.SHELL_SCALE)
        return pygame.transform.scale(image, (width, height))

    def update(self):
        self.position += self.velocity
        self.distance_traveled += self.velocity.length()
        return self.distance_traveled <= self.MAX_DISTANCE

    def draw(self, screen):
        rotated_shell = pygame.transform.rotate(self.image, self.angle + 90)
        shell_rect = rotated_shell.get_rect(center=self.position)
        screen.blit(rotated_shell, shell_rect)
