import pygame

class Image:
    def __init__(self) -> None:
        self._images: dict[str, pygame.Surface] = {}
    
    def load(self, name: str, path: str) -> None:
        if name in self._images:
            return
        
        self._images[name] = pygame.image.load(path)
        self._images[name].set_colorkey((0, 0, 0))

    def add(self, name: str, surface: pygame.Surface | list) -> None:
        if name in self._images:
            return
        
        self._images[name] = surface

    def get(self, name: str) -> pygame.Surface:
        if name in self._images:
            return self._images[name]
