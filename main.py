import pygame
from tank import Tank
from explosion import Explosion

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Initialize sound system
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        pygame.display.set_caption("Tank Battle")
        
        # Create two tanks with different sprites
        self.player_tank = Tank(300, 300, 'tank.png', 'turret.png')
        self.enemy_tank = Tank(self.width - 300, self.height - 300, 
                             'tank2.png', 'turret2.png')
        self.enemy_tank.body_angle = 90
        
        self.projectiles = []
        self.explosions = []
        self.tank_hit_radius = 40  # Collision detection radius for tanks

    def check_projectile_collision(self, projectile):
        # Check collision with both tanks
        for tank in [self.player_tank, self.enemy_tank]:
            distance = (tank.position - projectile.position).length()
            if distance < self.tank_hit_radius:
                return True
        return False

    def update_projectiles(self):
        active_projectiles = []
        for proj in self.projectiles:
            if proj.update() and not self.check_projectile_collision(proj):
                active_projectiles.append(proj)
            else:
                # Create explosion at projectile's last position
                self.explosions.append(Explosion(proj.position.x, proj.position.y))
                proj.explosion_sound.play()  # Play sound when firing
        self.projectiles = active_projectiles

    def update_explosions(self):
        self.explosions = [exp for exp in self.explosions if not exp.should_remove()]

    def draw_projectiles(self):
        for projectile in self.projectiles:
            projectile.draw(self.screen)

    def draw_explosions(self):
        for explosion in self.explosions:
            explosion.draw(self.screen)

    def check_tank_collision(self):
        tank_distance = (self.player_tank.position - self.enemy_tank.position).length()
        min_distance = 100
        if tank_distance < min_distance:
            # Calculate collision direction and strength
            direction = (self.player_tank.position - self.enemy_tank.position).normalize()
            push_strength = 2.0
            
            # Apply push to both tanks
            self.enemy_tank.apply_push(-direction, push_strength)
            self.player_tank.apply_push(direction, push_strength)
            return True
        return False

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()

            if keys[pygame.K_ESCAPE]:
                running = False

            new_projectile = self.player_tank.handle_input(keys)
            if new_projectile:
                self.projectiles.append(new_projectile)
            
            # Check and handle tank collisions
            self.check_tank_collision()
                
            self.update_projectiles()
            self.update_explosions()
            self.player_tank.update_position(self.width, self.height)
            self.enemy_tank.update_position(self.width, self.height)

            self.player_tank.handle_screen_wrap(self.width, self.height)
            
            self.screen.fill((0, 0, 0))
            self.player_tank.draw(self.screen)
            self.enemy_tank.draw(self.screen)
            self.draw_projectiles()
            self.draw_explosions()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()