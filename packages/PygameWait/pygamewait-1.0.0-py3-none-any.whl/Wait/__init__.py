import pygame
import sys

def wait(seconds):
    start_time = pygame.time.get_ticks()
    while (pygame.time.get_ticks() - start_time) < seconds * 1000:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.time.delay(10)  # Small delay to avoid maxing out CPU
