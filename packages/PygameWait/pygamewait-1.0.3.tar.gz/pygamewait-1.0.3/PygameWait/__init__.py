import pygame
import sys

class wait:
    def __init__(self):
        pass  # Add setup here later if needed

    @staticmethod
    def wait(seconds):
        pygame.init()
        screen = pygame.display.set_mode((100, 100))  # Small dummy surface

        start_time = pygame.time.get_ticks()
        while (pygame.time.get_ticks() - start_time) < seconds * 1000:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.time.delay(10)

        pygame.quit()

