import pygame
import os
import math

class Tank:
    def __init__(self, x, y):
        self.position = pygame.math.Vector2(x, y)
        self.current_speed = 0
        self.max_speed = 1
        self.acceleration = 0.1
        self.deceleration = 0.05
        self.body_angle = 0
        self.turret_angle = 0
        self.load_images()

    def load_images(self):
        self.body_image = pygame.image.load(os.path.join('img', 'tank.png'))
        self.body_image = pygame.transform.scale(self.body_image, 
            (int(self.body_image.get_width() * 0.4), int(self.body_image.get_height() * 0.4)))
        
        self.turret_image = pygame.image.load(os.path.join('img', 'turret.png'))
        self.turret_image = pygame.transform.scale(self.turret_image, 
            (int(self.turret_image.get_width() * 0.4), int(self.turret_image.get_height() * 0.4)))
        
        self.rect = self.body_image.get_rect()
        self.rect.center = (round(self.position.x), round(self.position.y))

    def handle_input(self, keys):
        if keys[pygame.K_LEFT]:
            self.body_angle += 0.5
        if keys[pygame.K_RIGHT]:
            self.body_angle -= 0.5
        
        if keys[pygame.K_q]:
            self.turret_angle += 1.5
        if keys[pygame.K_e]:
            self.turret_angle -= 1.5

        self._handle_movement(keys)
        return not keys[pygame.K_ESCAPE]

    def _handle_movement(self, keys):
        if keys[pygame.K_UP]:
            self.current_speed = min(self.current_speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN]:
            self.current_speed = max(self.current_speed - self.acceleration, -self.max_speed)
        else:
            if self.current_speed > 0:
                self.current_speed = max(0, self.current_speed - self.deceleration)
            elif self.current_speed < 0:
                self.current_speed = min(0, self.current_speed + self.deceleration)

        if self.current_speed != 0:
            radians = math.radians(-self.body_angle)
            self.position += pygame.math.Vector2(
                self.current_speed * math.cos(radians),
                self.current_speed * math.sin(radians)
            )
            self.rect.center = (round(self.position.x), round(self.position.y))

    def handle_screen_wrap(self, screen_width, screen_height):
        if self.position.x > screen_width:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = screen_width
        if self.position.y > screen_height:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = screen_height
        self.rect.center = (round(self.position.x), round(self.position.y))

    def draw(self, screen):
        # Draw body
        rotated_body = pygame.transform.rotate(self.body_image, self.body_angle + 90)
        rotated_body_rect = rotated_body.get_rect(center=self.rect.center)
        screen.blit(rotated_body, rotated_body_rect)
        
        # Draw turret
        angle_rad = math.radians(-(self.body_angle + self.turret_angle + 90))
        offset = pygame.math.Vector2(20 * math.cos(angle_rad), 20 * math.sin(angle_rad))
        
        rotated_turret = pygame.transform.rotate(self.turret_image, 
                                               self.body_angle + self.turret_angle + 90)
        turret_pos = self.position + offset
        turret_rect = rotated_turret.get_rect(center=turret_pos)
        screen.blit(rotated_turret, turret_rect)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        pygame.display.set_caption("Tank Battle")
        self.tank = Tank(self.width // 2, self.height // 2)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            running = self.tank.handle_input(keys)
            self.tank.handle_screen_wrap(self.width, self.height)
            
            self.screen.fill((0, 0, 0))
            self.tank.draw(self.screen)
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()