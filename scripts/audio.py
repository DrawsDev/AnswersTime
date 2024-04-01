import pygame

class Audio:
    def __init__(self) -> None:
        self._sounds: dict[str, pygame.mixer.Sound] = {}
    
    def load(self, name: str, path: str) -> None:
        if name in self._sounds:
            return
        
        self._sounds[name] = pygame.mixer.Sound(path)

    def play(self, name: str, loop: int = 0) -> None:
        if name in self._sounds:
            self._sounds[name].play(loop)
    
    def stop(self, name: str) -> None:
        if name in self._sounds:
            self._sounds[name].stop()
