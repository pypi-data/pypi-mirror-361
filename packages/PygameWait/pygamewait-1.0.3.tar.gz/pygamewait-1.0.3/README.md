# Wait an extention fot Pygame

A extention for Pygame, that is also a libary
it like time.sleep() but this dont get in the way of

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                
infact, it even add it as well
# Requirements

you also need other librarys to make this library work

you need

pygame

# Importing

install it using pip

pip install PygameWait

then Import

from PygameWait import wait

# How To Use

To wait type

wait.wait([seconds])

replace [seconds] to the amount of seconds you wanna wait
