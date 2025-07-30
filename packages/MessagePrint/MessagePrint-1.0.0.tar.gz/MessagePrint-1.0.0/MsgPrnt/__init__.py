import pygame
import time

class Msg:
    def __init__(self, text, position, size=20, color=(255, 255, 255), font=None, delay=3000):
        self.text = text
        self.position = position
        self.size = size
        self.color = color
        self.font = font
        self.delay = delay
        self.start_time = pygame.time.get_ticks()  #Start time in ms

    #Draw text to scrn
    def display(self, screen):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time < self.delay:
            font = self.font or pygame.font.SysFont("arial", self.size)
            text_surface = font.render(self.text, True, self.color)
            screen.blit(text_surface, self.position)    #Draw



