#
Overview
##
This library allows for printing messages onto the actual pygame screen itself, rather than into the syntax window.

###
Key Features
###
- Printing messages to screen

####
Basic Usage
####

from MsgPrnt import Msg
import pygame

pygame.init()
screen = pygame.display.set_mode((640, 480))

#Create animation
Msg = (""Hello World, (0, 0), size=20, color=(255, 255, 255), font=None, delay=3000)	#font None is default

#Main loop
running = True
while running:
    screen.fill((0, 0, 0))
    Msg.display(screen)
    pygame.display.flip()

pygame.quit()
