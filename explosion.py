import pygame
import os

class Explosion:
    def __init__(self, x, y):
        self.position = pygame.math.Vector2(x, y)
        self.creation_time = pygame.time.get_ticks()
        self.duration = 300  # 2 seconds
        self.growth_duration = 200  # 0.2 seconds for growth animation
        
        # Load and store original image
        self.original_image = pygame.image.load(os.path.join('img', 'explosion.png'))
        self.target_size = (
            int(self.original_image.get_width() * 0.4),
            int(self.original_image.get_height() * 0.4)
        )

    def should_remove(self):
        return pygame.time.get_ticks() - self.creation_time > self.duration

    def draw(self, screen):
        current_time = pygame.time.get_ticks()
        time_alive = current_time - self.creation_time
        
        # Calculate current scale based on growth animation
        if time_alive < self.growth_duration:
            scale = time_alive / self.growth_duration
        else:
            scale = 1.0
            
        # Calculate current size
        current_size = (
            int(self.target_size[0] * scale),
            int(self.target_size[1] * scale)
        )
        
        # Scale image to current size
        scaled_image = pygame.transform.scale(self.original_image, current_size)
        explosion_rect = scaled_image.get_rect(center=self.position)
        screen.blit(scaled_image, explosion_rect)