import pygame

class FontParams:
    def __init__(self, 
                 fontpath: str = None, 
                 size: int = 20,
                 color: tuple = (0, 0, 0), 
                 align: int = 0, 
                 alias: bool = True,
                 wraplength: int = 0) -> None:
        
        self._fontpath = fontpath
        self._size = size
        self._color = color
        self._align = align
        self._alias = alias
        self._wraplength = wraplength

    def get_render(self, text: str) -> pygame.Surface:
        return self.get_font().render(text, self._alias, self._color, wraplength=self._wraplength)

    def get_font_size(self, text: str) -> tuple[int, int]:
        """
        Вернёт (ширину, высоту) изображения текста при заданных настройках шрифта.
        При этом никакой отрисовки не произойдёт.
        """
        return self.get_font().size(text)

    def get_font(self) -> pygame.font.Font:
        font = pygame.font.Font(self._fontpath, self._size)
        font.align = self._align
        return font

class Font:
    none = FontParams()

    def __init__(self) -> None:
        self._fonts = {}
    
    def create(self,
               name: str,
               fontpath: str = None,
               size: int = 20,
               color: tuple[int, int, int] = (0, 0, 0),
               align: int = 0,
               alias: bool = True,
               wraplength: int = 0) -> FontParams:
        fontparams = FontParams(fontpath, size, color, align, alias, wraplength)
        self.add(name, fontparams)
        return fontparams
    
    def add(self, name: str, fontparams: FontParams) -> None:
        if not name in self._fonts:
            self._fonts[name] = fontparams
    
    def get(self, name: str) -> FontParams:
        if name in self._fonts:
            return self._fonts[name]
        return self.none
