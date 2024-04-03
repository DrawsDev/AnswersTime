import sys
import pygame
from scripts.questio import draw_quiz_bubbles
from scripts.audio import Audio
from scripts.image import Image
from scripts.font import Font
from scripts.input import Input
import scripts.settings as settings
import scripts.scenes as scenes

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(settings.GAME_TITLE)
        self.screen = pygame.display.set_mode(settings.SCREEN_SIZE, pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.audio = Audio()
        self.image = Image()
        self.font = Font()
        self.input = Input()
        self.init_scenes()
        draw_quiz_bubbles(self)

    def init_scenes(self) -> None:
        self.scene = None
        self.scenes = {}

        for scene in map(scenes.__dict__.get, scenes.__all__):
            self.scenes[scene.__name__] = scene(self)

        first_scene = list(self.scenes.keys())[0]
        self.change_scene(first_scene)

    def change_scene(self, name: str, *args) -> None:
        if name in self.scenes.keys():
            if self.scene:
                self.scene.onExit()
            self.scene = self.scenes[name]
            self.scene.onEnter(*args)

    def quit(self) -> None:
        pygame.quit()
        sys.exit()
    
    def loop(self) -> None:
        while True:
            delta = self.clock.tick(settings.FPS) / 1000
            self.update(delta)
            self.render()
            self.handle_events()
    
    def handle_events(self) -> None:
        self.input.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            self.input.handle_event(event)

    def update(self, delta: float) -> None:
        if self.scene:
            self.scene.update(delta)

    def render(self) -> None:
        self.screen.fill(settings.BACK_COLOR)
        
        if self.scene:
            self.scene.render(self.screen)

        pygame.display.update()
