import pygame
from tank import Tank

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        pygame.display.set_caption("Tank Battle")
        self.tank = Tank(self.width // 2, self.height // 2)
        self.projectiles = []

    def update_projectiles(self):
        self.projectiles = [proj for proj in self.projectiles if proj.update()]

    def draw_projectiles(self):
        for projectile in self.projectiles:
            projectile.draw(self.screen)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()

            if keys[pygame.K_ESCAPE]:
                running = False

            new_projectile = self.tank.handle_input(keys)
            if new_projectile:
                self.projectiles.append(new_projectile)
                
            self.update_projectiles()
            self.tank.handle_screen_wrap(self.width, self.height)
            
            self.screen.fill((0, 0, 0))
            self.tank.draw(self.screen)
            self.draw_projectiles()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()