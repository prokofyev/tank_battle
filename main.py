import pygame
import os
import math

class Projectile:
    def __init__(self, x, y, angle, speed=5):
        self.position = pygame.math.Vector2(x, y)
        self.angle = angle
        self.speed = speed
        self.distance_traveled = 0
        self.max_distance = 500
        self.image = pygame.image.load(os.path.join('img', 'shell.png'))
        self.image = pygame.transform.flip(self.image, flip_x=False, flip_y=True)
        self.image = pygame.transform.scale(self.image, 
            (int(self.image.get_width() * 0.1), int(self.image.get_height() * 0.1)))

    def update(self):
        radians = math.radians(-self.angle)
        movement = pygame.math.Vector2(
            self.speed * math.cos(radians),
            self.speed * math.sin(radians)
        )
        self.position += movement
        self.distance_traveled += movement.length()
        return self.distance_traveled <= self.max_distance

    def draw(self, screen):
        rotated_shell = pygame.transform.rotate(self.image, self.angle + 90)
        shell_rect = rotated_shell.get_rect(center=self.position)
        screen.blit(rotated_shell, shell_rect)

class Tank:
    def __init__(self, x, y):
        self.position = pygame.math.Vector2(x, y)
        self.current_speed = 0
        self.max_speed = 1
        self.acceleration = 0.1
        self.deceleration = 0.05
        self.body_angle = 0
        self.turret_angle = 0
        self.flash_visible = False
        self.flash_start_time = 0
        self.flash_duration = 50  # milliseconds
        self.recoil_speed = 0
        self.recoil_force = -0.5  # Negative because it pushes tank backwards
        self.projectiles = []
        self.last_shot_time = 0
        self.shot_cooldown = 2000  # 2000 milliseconds = 2 seconds
        self.load_images()

    def load_images(self):
        self.body_image = pygame.image.load(os.path.join('img', 'tank.png'))
        self.body_image = pygame.transform.scale(self.body_image, 
            (int(self.body_image.get_width() * 0.4), int(self.body_image.get_height() * 0.4)))
        
        self.turret_image = pygame.image.load(os.path.join('img', 'turret.png'))
        self.turret_image = pygame.transform.scale(self.turret_image, 
            (int(self.turret_image.get_width() * 0.4), int(self.turret_image.get_height() * 0.4)))
        
        self.flash_image = pygame.image.load(os.path.join('img', 'fire.png'))
        self.flash_image = pygame.transform.scale(self.flash_image, 
            (int(self.flash_image.get_width() * 0.4), int(self.flash_image.get_height() * 0.4)))
        
        self.rect = self.body_image.get_rect()
        self.rect.center = (round(self.position.x), round(self.position.y))

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

        radians = math.radians(-self.body_angle)
        self.position += pygame.math.Vector2(
            self.current_speed * math.cos(radians),
            self.current_speed * math.sin(radians)
        )

        radians = math.radians(-self.body_angle - self.turret_angle - 90)
        self.position += pygame.math.Vector2(
            self.recoil_speed * math.cos(radians),
            self.recoil_speed * math.sin(radians)
        )

        self.rect.center = (round(self.position.x), round(self.position.y))
    
    # Gradually reduce recoil
        if self.recoil_speed < 0:
            self.recoil_speed = min(0, self.recoil_speed + self.deceleration)

    def handle_input(self, keys):
        current_time = pygame.time.get_ticks()

        if keys[pygame.K_LEFT]:
            self.body_angle += 0.5
        if keys[pygame.K_RIGHT]:
            self.body_angle -= 0.5
        
        if keys[pygame.K_q] or keys[pygame.K_a]:
            self.turret_angle += 1.5
        if keys[pygame.K_e] or keys[pygame.K_d]:
            self.turret_angle -= 1.5
        if keys[pygame.K_w] and current_time - self.last_shot_time >= self.shot_cooldown:
            self.flash_visible = True
            self.flash_start_time = current_time
            self.last_shot_time = current_time
            self.recoil_speed = self.recoil_force  # Apply recoil force when firing

            # Create new projectile at turret position
            angle_rad = math.radians(-(self.body_angle + self.turret_angle + 90))
            SHELL_OFFSET = 60
            shell_pos = self.position + pygame.math.Vector2(
                SHELL_OFFSET * math.cos(angle_rad),
                SHELL_OFFSET * math.sin(angle_rad)
            )
            self.projectiles.append(Projectile(shell_pos.x, shell_pos.y, 
                                             self.body_angle + self.turret_angle + 90))

        # Update flash visibility
        if self.flash_visible and pygame.time.get_ticks() - self.flash_start_time > self.flash_duration:
            self.flash_visible = False
        
        self._handle_movement(keys)
        return not keys[pygame.K_ESCAPE]

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

    def update(self):
        # Update projectiles and remove those that have traveled max distance
        self.projectiles = [proj for proj in self.projectiles if proj.update()]

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
        
        # Draw muzzle flash if active
        if self.flash_visible:
            angle_rad = math.radians(-(self.body_angle + self.turret_angle + 90))
            
            FLASH_OFFSET = 90
            flash_offset = pygame.math.Vector2(FLASH_OFFSET * math.cos(angle_rad), FLASH_OFFSET * math.sin(angle_rad))
            
            rotated_flash = pygame.transform.rotate(self.flash_image, 
                                                  self.body_angle + self.turret_angle + 90)
            flash_pos = self.position + flash_offset
            flash_rect = rotated_flash.get_rect(center=flash_pos)
            screen.blit(rotated_flash, flash_rect)

        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(screen)

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
            self.tank.update()  # Add this line
            self.tank.handle_screen_wrap(self.width, self.height)
            
            self.screen.fill((0, 0, 0))
            self.tank.draw(self.screen)
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()