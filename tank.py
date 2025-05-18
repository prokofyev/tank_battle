import pygame
import math
import os
from projectile import Projectile

import random

class Tank:
    def __init__(self, x, y, tank_img='tank.png', turret_img='turret.png'):
        self.position = pygame.math.Vector2(x, y)
        self.tank_img = tank_img
        self.turret_img = turret_img
        self.current_speed = 0
        self.max_speed = 0.5
        self.last_body_angle = 0
        self.acceleration = 0.1
        self.deceleration = 0.005
        self.body_angle = 0
        self.turret_angle = -90
        self.flash_visible = False
        self.flash_start_time = 0
        self.flash_duration = 50  # milliseconds
        self.recoil_speed = 0
        self.recoil_force = -0.1  # Negative because it pushes tank backwards
        self.last_shot_time = 0
        self.shot_cooldown = 2000  # 2000 milliseconds = 2 seconds
        self.load_images()
        self.fire_sound = pygame.mixer.Sound(os.path.join('sound', 'fire.mp3'))
        self.track_sound = pygame.mixer.Sound(os.path.join('sound', 'track.mp3'))
        self.track_sound.set_volume(0.0)
        self.track_sound_playing = False
        self.track_sound_volume = 0.0  # Текущая громкость гусениц (0..1)
        self.track_sound_target_volume = 0.5  # Целевая громкость при движении
        self.track_sound_fade_speed = 0.05  # Скорость изменения громкости
        self.engine_sound = pygame.mixer.Sound(os.path.join('sound', 'engine.mp3'))
        self.engine_sound.set_volume(0.05)
        self.engine_sound.play(-1)  # Включаем звук двигателя при создании танка
        self.engine_sound_playing = True
        self.push_speed = 0
        self.push_direction = None
        self.push_deceleration = 0.05
        self.health = 100
        self.max_health = 100
        self.is_dying = False
        self.death_start_time = 0
        self.death_duration = 5000  # 5 seconds in milliseconds
        self.death_explosions = []
        self.death_next_explosion = 0
        self.explosion_sound = pygame.mixer.Sound(os.path.join('sound', 'explosion.mp3'))

    def load_images(self):
        self.body_image = pygame.image.load(os.path.join('img', self.tank_img))
        self.body_image = pygame.transform.scale(self.body_image, 
            (int(self.body_image.get_width() * 0.4), int(self.body_image.get_height() * 0.4)))
        
        self.turret_image = pygame.image.load(os.path.join('img', self.turret_img))
        self.turret_image = pygame.transform.scale(self.turret_image, 
            (int(self.turret_image.get_width() * 0.4), int(self.turret_image.get_height() * 0.4)))
        
        self.flash_image = pygame.image.load(os.path.join('img', 'fire.png'))
        self.flash_image = pygame.transform.scale(self.flash_image, 
            (int(self.flash_image.get_width() * 0.4), int(self.flash_image.get_height() * 0.4)))
        
        self.rect = self.body_image.get_rect()
        self.rect.center = (round(self.position.x), round(self.position.y))

    def _update_sounds(self):
        # Плавное изменение громкости гусениц
        if abs(self.current_speed) > 0.01 or self.last_body_angle != self.body_angle:  # Если танк движется
            if not self.track_sound_playing:
                self.track_sound.play(-1)
                self.track_sound_playing = True
            # Плавное увеличение громкости до целевой
            if self.track_sound_volume < self.track_sound_target_volume:
                self.track_sound_volume = min(
                    self.track_sound_volume + self.track_sound_fade_speed,
                    self.track_sound_target_volume
                )
                self.track_sound.set_volume(self.track_sound_volume)
        else:  # Если танк стоит
            # Плавное уменьшение громкости
            if self.track_sound_volume > 0:
                self.track_sound_volume = max(
                    0,
                    self.track_sound_volume - self.track_sound_fade_speed
                )
                self.track_sound.set_volume(self.track_sound_volume)
            else:
                if self.track_sound_playing:
                    self.track_sound.stop()
                    self.track_sound_playing = False

    def update_position(self, width, height):
        # Apply forward/backward movement
        radians = math.radians(-self.body_angle)
        self.position += pygame.math.Vector2(
            self.current_speed * math.cos(radians),
            self.current_speed * math.sin(radians)
        )

        # Apply recoil movement
        radians = math.radians(-self.body_angle - self.turret_angle - 90)
        self.position += pygame.math.Vector2(
            self.recoil_speed * math.cos(radians),
            self.recoil_speed * math.sin(radians)
        )

        # Apply push movement
        if self.push_direction:
            radians = math.atan2(self.push_direction.y, self.push_direction.x)
            self.position += pygame.math.Vector2(
                self.push_speed * math.cos(radians),
                self.push_speed * math.sin(radians)
            )

        # Update rectangle position
        self.rect.center = (round(self.position.x), round(self.position.y))

        # Reduce speeds
        if self.push_speed != 0:
            if self.push_speed > 0:
                self.push_speed = max(0, self.push_speed - self.push_deceleration)
            else:
                self.push_speed = min(0, self.push_speed + self.push_deceleration)

        if self.recoil_speed < 0:
            self.recoil_speed = min(0, self.recoil_speed + self.deceleration)

        # Update flash visibility
        if self.flash_visible and pygame.time.get_ticks() - self.flash_start_time > self.flash_duration:
            self.flash_visible = False

        self.handle_screen_wrap(width, height)

    def apply_push(self, direction, strength):
        self.push_speed = strength
        self.push_direction = direction

    def handle_input(self, keys):
        current_time = pygame.time.get_ticks()

        if keys[pygame.K_UP] and self.health > 0:
            self.current_speed = min(self.current_speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN] and self.health > 0:
            self.current_speed = max(self.current_speed - self.acceleration, -self.max_speed)
        else:
            if self.current_speed > 0:
                self.current_speed = max(0, self.current_speed - self.deceleration)
            elif self.current_speed < 0:
                self.current_speed = min(0, self.current_speed + self.deceleration)

        if keys[pygame.K_LEFT] and self.health > 0:
            self.body_angle += 0.2
        if keys[pygame.K_RIGHT] and self.health > 0:
            self.body_angle -= 0.2

        self._update_sounds()

        self.last_body_angle = self.body_angle

        if (keys[pygame.K_q] or keys[pygame.K_a]) and self.health > 0:
            self.turret_angle += 0.3
        if (keys[pygame.K_e] or keys[pygame.K_d]) and self.health > 0:
            self.turret_angle -= 0.3

        new_projectile = None
        if keys[pygame.K_w] and current_time - self.last_shot_time >= self.shot_cooldown \
                and self.health > 0:
            self.fire_sound.play()  # Play sound when firing
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
            new_projectile = Projectile(shell_pos.x, shell_pos.y, 
                                             self.body_angle + self.turret_angle + 90,
                                             self.current_speed, self.body_angle)

        return new_projectile

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

    def draw_body(self, screen):
        # Draw body
        rotated_body = pygame.transform.rotate(self.body_image, self.body_angle + 90)
        rotated_body_rect = rotated_body.get_rect(center=self.rect.center)
        screen.blit(rotated_body, rotated_body_rect)

    def draw_turret(self, screen):
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

        if self.is_dying:
            for explosion in self.death_explosions:
                rect = explosion['image'].get_rect(center=explosion['pos'])
                screen.blit(explosion['image'], rect)

    def take_damage(self):
        damage = random.randint(30, 50)
        self.health = max(0, self.health - damage)
        if self.health == 0 and not self.is_dying:
            self.start_death_sequence()
        return damage

    def take_collision_damage(self):
        damage = random.randint(5, 10)
        self.health = max(0, self.health - damage)
        if self.health == 0 and not self.is_dying:
            self.start_death_sequence()
        return damage

    def start_death_sequence(self):
        self.is_dying = True
        self.death_start_time = pygame.time.get_ticks()
        self.explosion_sound.play()

    def update_death_animation(self):
        if not self.is_dying:
            return
        
        current_time = pygame.time.get_ticks()
        if current_time - self.death_start_time > self.death_duration:
            self.is_dying = False
            return

        # Add new explosion every 100ms
        if current_time > self.death_next_explosion:
            self.death_next_explosion = current_time + 100
            # Random position within tank's rectangle
            x_offset = random.randint(-30, 30)
            y_offset = random.randint(-30, 30)
            pos = self.position + pygame.math.Vector2(x_offset, y_offset)
            
            # Random rotation angle
            rotation_angle = random.randint(0, 360)
            explosion_img = pygame.transform.scale(
                pygame.image.load(os.path.join('img', 'fire.png')),
                (60, 60)
            )
            rotated_explosion = pygame.transform.rotate(explosion_img, rotation_angle)

            self.death_explosions.append({
                'pos': pos,
                'start_time': current_time,
                'duration': random.randint(300, 700),
                'image': rotated_explosion
            })

        # Update existing explosions
        self.death_explosions = [exp for exp in self.death_explosions 
                               if current_time - exp['start_time'] < exp['duration']]

    def draw_health_bar(self, screen, x, y):
        bar_width = 200
        bar_height = 30
        fill_width = int((self.health / self.max_health) * bar_width)
        
        # Draw background
        pygame.draw.rect(screen, (128, 128, 128), (x, y, bar_width, bar_height))
        # Draw health
        pygame.draw.rect(screen, (255, 0, 0), (x, y, fill_width, bar_height))
        # Draw border
        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)

    def __del__(self):
        # Останавливаем все звуки при удалении объекта
        if self.track_sound_playing:
            self.track_sound.stop()
        if self.engine_sound_playing:
            self.engine_sound.stop()

    def move_to_target(self, target_pos):
        if self.health <= 0:
            self.current_speed = max(self.current_speed - self.deceleration, 0)
            return False

        # Calculate angle to target
        direction = target_pos - self.position
        target_angle = - (math.degrees(math.atan2(direction.y, direction.x)))
        
        # Normalize angle difference to -180 to 180
        angle_diff = (target_angle - self.body_angle) % 360
        if angle_diff > 180:
            angle_diff -= 360
            
        # Rotate towards target
        if abs(angle_diff) > 0.5:
            self.body_angle += 0.3 if angle_diff > 0 else -0.3
            return False
            
        # Move forward if pointing at target
        self.current_speed = min(self.current_speed + self.acceleration, self.max_speed)
        return direction.length() < 50  # Return True if reached target

    def aim_turret_at(self, target_pos):
        if self.health <= 0:
            return 

        # Calculate angle to target
        direction = target_pos - self.position
        target_angle = -(math.degrees(math.atan2(direction.y, direction.x)))
        
        # Calculate the shortest rotation direction
        angle_diff = (target_angle - (self.body_angle + self.turret_angle + 90)) % 360
        if angle_diff > 180:
            angle_diff -= 360
            
        # Rotate turret towards target
        self.turret_angle += angle_diff * 0.005
