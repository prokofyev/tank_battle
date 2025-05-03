import pygame
from tank import Tank


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