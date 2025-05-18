import pygame
from tank import Tank
from explosion import Explosion
import os
import random

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Initialize sound system
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        pygame.display.set_caption("Tank Battle")

        # Debug settings
        self.DRAW_ENEMY_TANK_DESTINATION = False
        
        # Create two tanks with different sprites
        self.player_tank = Tank(300, 300, 'tank.png', 'turret.png')
        self.enemy_tank = Tank(self.width - 300, self.height - 300, 
                             'tank2.png', 'turret2.png')
        self.enemy_tank.body_angle = 180
        
        self.projectiles = []
        self.explosions = []
        self.tank_hit_radius = 40  # Collision detection radius for tanks
        self.victory_start_time = 0
        self.victory_duration = 3000  # 3 seconds in milliseconds
        self.victory_font = pygame.font.Font(os.path.join('fonts', 'army_rust.ttf'), 250)
        self.show_victory = False
        self.game_over_start_time = 0
        self.game_over_duration = 3000  # 3 seconds
        self.show_game_over = False
        self.enemy_target = pygame.math.Vector2(
            random.randint(0, self.width),
            random.randint(0, self.height)
        )
        self.enemy_next_shot = pygame.time.get_ticks() + random.randint(2000, 10000)

    def reset_game(self):
        self.player_tank = Tank(300, 300, 'tank.png', 'turret.png')
        self.enemy_tank = Tank(self.width - 300, self.height - 300, 
                             'tank2.png', 'turret2.png')
        self.enemy_tank.body_angle = 180
        self.projectiles = []
        self.explosions = []
        self.show_victory = False
        self.show_game_over = False

    def draw_victory_message(self):
        if not self.show_victory:
            return
            
        current_time = pygame.time.get_ticks()
        if current_time - self.victory_start_time > self.victory_duration:
            self.reset_game()
            return
            
        text = self.victory_font.render("VICTORY", True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, text_rect)

    def draw_game_over_message(self):
        if not self.show_game_over:
            return
            
        current_time = pygame.time.get_ticks()
        if current_time - self.game_over_start_time > self.game_over_duration:
            self.reset_game()
            return
            
        text = self.victory_font.render("GAME OVER", True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, text_rect)

    def check_projectile_collision(self, projectile):
        # Check collision with both tanks
        for tank in [self.player_tank, self.enemy_tank]:
            distance = (tank.position - projectile.position).length()
            if distance < self.tank_hit_radius:
                tank.take_damage()
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
            # If either tank is dying (on fire), destroy the other tank
            if self.player_tank.is_dying:
                self.enemy_tank.health = 0
                self.enemy_tank.start_death_sequence()
            if self.enemy_tank.is_dying:
                self.player_tank.health = 0
                self.player_tank.start_death_sequence()

            # Calculate collision direction and strength
            direction = (self.player_tank.position - self.enemy_tank.position).normalize()
            push_strength = 0.9
            
            # Apply regular collision damage only if tanks aren't dying
            if not (self.player_tank.is_dying or self.enemy_tank.is_dying):
                self.player_tank.take_collision_damage()
                self.enemy_tank.take_collision_damage()
            
            # Apply push to both tanks
            self.enemy_tank.apply_push(-direction, push_strength)
            self.player_tank.apply_push(direction, push_strength)
            return True
        return False

    def update_enemy(self):
         # Update enemy movement
        if self.enemy_tank.move_to_target(self.enemy_target):
            # Keep generating new points until we find one far enough
            while True:
                new_target = pygame.math.Vector2(
                    random.randint(0, self.width),
                    random.randint(0, self.height)
                )
                # Check if the new point is far enough from current position
                if (new_target - self.enemy_tank.position).length() >= 500:
                    self.enemy_target = new_target
                    break

        self.enemy_tank.aim_turret_at(self.player_tank.position)

        # Handle enemy shooting
        current_time = pygame.time.get_ticks()
        if current_time >= self.enemy_next_shot and self.enemy_tank.health > 0:
            new_projectile = self.enemy_tank.shoot()
            if new_projectile:
                self.projectiles.append(new_projectile)
            self.enemy_next_shot = current_time + random.randint(2000, 10000)

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
            
            self.player_tank.update_death_animation()
            self.enemy_tank.update_death_animation()

            self.update_enemy()
            
            # Check for victory condition
            if self.enemy_tank.health == 0 and not self.show_victory and not self.show_game_over:
                self.show_victory = True
                self.victory_start_time = pygame.time.get_ticks()
            if self.player_tank.health == 0 and not self.show_victory and not self.show_game_over:
                self.show_game_over = True
                self.game_over_start_time = pygame.time.get_ticks()
            
            self.screen.fill((0, 0, 0))
            self.draw_enemy_destination()  # Add this line before health bars
            self.player_tank.draw_body(self.screen)
            self.enemy_tank.draw_body(self.screen)
            self.player_tank.draw_turret(self.screen)
            self.enemy_tank.draw_turret(self.screen)
            self.draw_projectiles()
            self.draw_explosions()
            self.player_tank.draw_health_bar(self.screen, 50, 50)
            self.enemy_tank.draw_health_bar(self.screen, self.width - 250, 50)
            self.draw_victory_message()
            self.draw_game_over_message()
            pygame.display.flip()

        pygame.quit()

    def draw_enemy_destination(self):
            if not self.DRAW_ENEMY_TANK_DESTINATION:
                return
                
            # Draw a red cross at target position
            cross_size = 20
            pygame.draw.line(self.screen, (255, 0, 0),
                            (self.enemy_target.x - cross_size, self.enemy_target.y - cross_size),
                            (self.enemy_target.x + cross_size, self.enemy_target.y + cross_size), 3)
            pygame.draw.line(self.screen, (255, 0, 0),
                            (self.enemy_target.x - cross_size, self.enemy_target.y + cross_size),
                            (self.enemy_target.x + cross_size, self.enemy_target.y - cross_size), 3)

if __name__ == "__main__":
    game = Game()
    game.run()