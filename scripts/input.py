import pygame

class Input:
    def __init__(self) -> None:
        self._keys_down = set()
        self._keys_pressed = set()
        self._mouse_keys = ("m_none", "m_left", "m_wheel", "m_right", "m_wheel_up", "m_wheel_down", "m_button1", "m_button2")
        self._mouse_moved = False
        self._unicode = ""
    
    @property
    def mousemoved(self) -> bool:
        return self._mouse_moved

    @property
    def unicode(self) -> str:
        return self._unicode

    def get_axis(self, positive_key: str, negative_key: str) -> int:
        key1 = int(self.is_key_down(positive_key))
        key2 = int(self.is_key_down(negative_key))
        return key1 - key2

    def is_key_down(self, key: str) -> bool:
        return key in self._keys_down

    def is_key_pressed(self, key: str) -> bool:
        return key in self._keys_pressed

    def is_anything_pressed(self) -> bool:
        return len(self._keys_pressed) > 0

    def update(self) -> None:
        self._keys_pressed = set()
        self._unicode = ""

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            self._keys_down.add(key_name)
            self._keys_pressed.add(key_name)
        
        if event.type == pygame.KEYUP:
            key_name = pygame.key.name(event.key)
            self._keys_down.discard(key_name)

        if event.type == pygame.MOUSEBUTTONDOWN:
            key_name = self._mouse_keys[event.button]
            self._keys_down.add(key_name)
            self._keys_pressed.add(key_name)
        
        if event.type == pygame.MOUSEBUTTONUP:
            key_name = self._mouse_keys[event.button]
            self._keys_down.discard(key_name)        

        if event.type == pygame.TEXTINPUT:
            self._unicode = event.text

        if self.is_key_pressed("f11"):
            pygame.display.toggle_fullscreen()

        self._mouse_moved = event.type == pygame.MOUSEMOTION
