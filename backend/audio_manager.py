import pygame

pygame.mixer.init()

class AudioManager:

    def __init__(self):

        self.playing = False

    def play_lofi(self):

        pygame.mixer.music.load("assets/sounds/lofi.mp3")
        pygame.mixer.music.play(-1)

        self.playing = True

    def stop(self):

        pygame.mixer.music.stop()

        self.playing = False