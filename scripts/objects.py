import time
import math
import random
import pygame
from pygame.math import Vector2 as vec2
from pygame.math import Vector3 as vec3
from scripts.font import Font, FontParams
from scripts.timer import Timer
from scripts.utils import set_character
from scripts.settings import *

class InputBox:
    def __init__(self,
                 game,
                 label="Label",
                 maxlength=56) -> None:
        
        self._game = game
        self._label = label
        self._text = ""
        self._cursor = -1
        self._maxlength = maxlength
        self._enabled = False
        self._changed = False
    
    @property
    def text(self) -> str:
        return self._text

    @property
    def label(self) -> str:
        return self._label

    @property
    def changed(self) -> bool:
        return self._changed

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    @property
    def cursor(self) -> int:
        return self._cursor
    
    @cursor.setter
    def cursor(self, position: int) -> None:
        if 0 <= position <= len(self._text) - 1:
            self._cursor = position
    
    def _handle_events(self) -> bool:
        if not self._enabled: return False
        
        position = self._cursor
        length = len(self._text) - 1

        if self._game.input.is_key_pressed("backspace"):
            self._text = set_character(self._text, "", position)
            if position > length:
                self._cursor = length
            elif position > 0:
                self._cursor = position - 1
            elif length == 0:
                self._cursor = -1
            return True
        elif self._game.input.is_key_pressed("right") or self._game.input.is_key_pressed("left"):
            self.cursor += self._game.input.get_axis("right", "left")
            return True
        elif self._game.input.is_anything_pressed():
            unicode = self._game.input.unicode
            if unicode != "" and length < self._maxlength - 1:
                self._text = set_character(self._text, unicode, position)
                self.cursor += 1
                return True

        return False

    def update(self) -> None:
        self._changed = self._handle_events()

class ImageSprite(pygame.sprite.Sprite):
    def __init__(self, 
                 game,
                 image: pygame.Surface,
                 position: vec2 = vec2(0, 0),
                 anchor: str = "center") -> None:
        
        super().__init__()
        self.game = game
        self._position = position
        self._anchor = anchor
        self._create_image(image)

    @property
    def position(self) -> vec2:
        return vec2(self._position)
    
    @position.setter
    def position(self, value: vec2) -> None:
        self._position = value
        self._change_position()

    @property
    def size(self) -> vec2:
        return vec2(self.rect.size)

    @property
    def anchor(self) -> str:
        return self._anchor

    @anchor.setter
    def anchor(self, value: str) -> None:
        self._anchor = value
        self._change_position()

    def mouse_in(self) -> bool:
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def _change_position(self) -> None:
        self.rect = self.image.get_rect(**{self._anchor: self._position})

    def _create_image(self, image: pygame.Surface) -> None:
        self.image = image
        self._change_position()

class TextSprite(pygame.sprite.Sprite):
    def __init__(self, 
                 game, 
                 text: str = "Text", 
                 position: vec2 = vec2(0, 0),
                 anchor: str = "topleft",
                 fontparams: FontParams = Font.none) -> None:
        
        super().__init__()
        self.game = game
        self._position = position
        self._anchor = anchor
        self._fontparams = fontparams
        self.draw_text(text)

    @property
    def position(self) -> vec2:
        return vec2(self._position)
    
    @position.setter
    def position(self, value: vec2) -> None:
        self._position = value
        self._change_position()

    @property
    def anchor(self) -> str:
        return self._anchor

    @anchor.setter
    def anchor(self, value: str) -> None:
        self._anchor = value
        self._change_position()

    def _change_position(self) -> None:
        self.rect = self.image.get_rect(**{self._anchor: self._position})

    def draw_text(self, text: str) -> None:
        self.image = self._fontparams.get_render(text)
        self._change_position()

class InputBoxSprite(TextSprite):
    def __init__(self, 
                 game, 
                 label: str = "Text", 
                 position: vec2 = vec2(0, 0),
                 anchor: str = "topleft",
                 fontparams: FontParams = Font.none) -> None:
        
        super().__init__(game, label, position, anchor, fontparams)
        self._input_box = InputBox(game, label)
        self._cursor_rect = pygame.Rect(self.rect.midleft, (1, self.rect.h))
        
        self._t0 = time.time()
        self._blink = True
        self._noblink_time = 0.75
        self._blink_time = 0.5

    @property
    def text(self) -> str:
        return self._input_box.text

    @property
    def label(self) -> str:
        return self._input_box.label

    @property
    def enabled(self) -> bool:
        return self._input_box.enabled
    
    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._input_box.enabled = value

    def _draw_cursor(self, surface: pygame.Surface) -> None:
        x = self.rect.right - self._fontparams.get_font_size(self.text[self._input_box.cursor + 1:])[0]
        self._cursor_rect.midleft = (x, self.rect.centery)
        pygame.draw.rect(surface, (255, 255, 255), self._cursor_rect)

    def _check_inputbox_changed(self) -> None:
        if self._input_box.changed:
            self.draw_text(self.text if self.text != "" else self.label)
            self._blink = False
            self._t0 = time.time()
        
    def _check_blink(self) -> None:
        if not self._blink:
            if time.time() - self._t0 > self._noblink_time:
                self._blink = True

    def post_draw(self, surface: pygame.Surface) -> None:
        if self.enabled:
            if self._blink and time.time() % 1 > self._blink_time:
                self._draw_cursor(surface)
            
            if not self._blink:
                self._draw_cursor(surface)

    def update(self, delta: float) -> None:
        self._input_box.update()
        self._check_inputbox_changed()
        self._check_blink()

class ButtonSprite(TextSprite):
    def __init__(self, 
                 game, 
                 text: str = "Button", 
                 position: vec2 = vec2(0, 0), 
                 anchor: str = "topleft", 
                 fontparams: FontParams = Font.none) -> None:
        
        super().__init__(game, text, position, anchor, fontparams)
        self._hover = False
        print(self.image)
        self.rect = self.image
        self._change_image()

    def draw_text(self, text: str) -> None:
        self._text_image = self._fontparams.get_render(text)

    def _change_image(self) -> None:
        if self._hover:
            pygame.draw.rect(self.image, (255, 255, 255), pygame.Rect(self.rect.topleft, self.rect.bottomright))
        else:
            pygame.draw.rect(self.image, (200, 200, 200), pygame.Rect(self.rect.topleft, self.rect.bottomright))
        self.rect = self.image.get_rect(**{self._anchor: self._position})
    
    def _check_hover(self) -> None:
        prev_hover = self._hover

        self._hover = self.rect.collidepoint(pygame.mouse.get_pos())

        if self._hover != prev_hover:
            self._refresh_image()

    def post_draw(self, surface: pygame.Surface) -> None:
        surface.blit(self._text_image, self._text_image.get_rect(**{self._anchor: self._position}))

    def update(self, delta: float) -> None:
        self._check_hover()

class Particle(pygame.sprite.Sprite):
    def __init__(self,
                 position: vec2 = vec2(0, 0),
                 velocity: vec2 = vec2(0, -1),
                 speed: float = 100,
                 lifetime: int = 2) -> None:
        
        super().__init__()
        self._position = position
        self._velocity = velocity
        self._speed = speed
        self._lifetime = lifetime
        self._start_time = time.time()
        self._create_surface(position)

    def _create_surface(self, position: vec2) -> None:
        self.image = pygame.Surface((4, 4))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_frect(center = position)
        pygame.draw.circle(self.image, (255, 255, 255), (2, 2), 2)
    
    def _move(self, delta: float) -> None:
        self.rect.center += self._velocity * self._speed * delta

    def _check_lifetime(self) -> None:
        if time.time() - self._start_time > self._lifetime:
            self.kill()      

    def update(self, delta: float) -> None:
        self._move(delta)
        self._check_lifetime()

### thx @StandaloneCoder
class Star:
    def __init__(self, game) -> None:
        self._screen = game.screen
        self._pos3d = self.get_pos3d()
        self._velocity = random.uniform(0.15, 0.45)
        self._color = random.choice([BLU_1, BLU_2, BLU_3, BLU_4])
        self._size = 10
        self._screen_position = vec2(0, 0)
        self._cursor = True

    def get_pos3d(self, scale_pos=35) -> vec3:
        angle = random.uniform(0, 2 * math.pi)
        h = self._screen.get_rect().h
        radius = random.randrange(h // 4, h // 3) * scale_pos
        x = radius * math.sin(angle)
        y = radius * math.cos(angle)
        return vec3(x, y, 40)

    def update(self) -> None:
        self._pos3d.z -= self._velocity
        self._pos3d = self.get_pos3d() if self._pos3d.z < 1 else self._pos3d
        
        self._screen_position = vec2(self._pos3d.x, self._pos3d.y) / self._pos3d.z + self._screen.get_rect().center
        self._size = (40 - self._pos3d.z) / (0.2 * self._pos3d.z)

        self._pos3d.xy = self._pos3d.xy.rotate(0.2)
        if self._cursor:
            self._screen_position += (self._screen.get_rect().center - vec2(pygame.mouse.get_pos())) / 5

    def render(self) -> None:
        pygame.draw.rect(self._screen, self._color, (*self._screen_position, self._size, self._size))

class Starfield:
    def __init__(self, game, stars: int = 500) -> None:
        self._stars = [Star(game) for _ in range(stars)]

    def update(self) -> None:
        [star.update() for star in self._stars]
        self._stars.sort(key=lambda star: star._pos3d.z, reverse=True)
        
    def render(self) -> None:
        [star.render() for star in self._stars]
    
    def set_cursor_mode(self, value: bool) -> None:
        for star in self._stars: star._cursor = value
###

class QuizTextBubble(TextSprite):
    def __init__(self,
                 game,
                 answer_index: int,
                 text: str = "Text",
                 position: vec2 = vec2(0, 0),
                 fontparams: FontParams = Font.none) -> None:
        
        super().__init__(game, text, position, "center", fontparams)
        self._answer_index = answer_index
        self._hover = False
        self._checked = False
        self._change_bubble_image()

        self._timer0 = Timer(0.5, True)

    @property
    def answer_index(self) -> int:
        return self._answer_index

    @property
    def checked(self) -> bool:
        return self._checked
    
    @checked.setter
    def checked(self, value: bool) -> None:
        self._checked = value
        self._change_bubble_image()

    def draw_text(self, text: str) -> None:
        self._text_image = self._fontparams.get_render(text)

    def _change_bubble_image(self) -> None:
        if self._hover and not self._checked:
            self.image = self.game.image.get("quiz_bubble_hover")
        elif not self._hover and not self._checked:
            self.image = random.choice(self.game.image.get("quiz_bubble_idle"))
        elif self._hover and self._checked:
            self.image = self.game.image.get("quiz_bubble_hover_check")
        elif not self._hover and self._checked:
            self.image = random.choice(self.game.image.get("quiz_bubble_idle_check"))
        self.rect = self.image.get_rect(**{self._anchor: self._position})

    def _check_time_to_deform(self) -> None:
        if not self._hover and self._timer0.expired:
            self._change_bubble_image()

    def _check_hover(self) -> None:
        prev_hover = self._hover

        self._hover = self.rect.collidepoint(pygame.mouse.get_pos())

        if self._hover != prev_hover:
            if self._hover: 
                self.game.audio.play("answer_select")
            self._change_bubble_image()

    def post_draw(self, surface: pygame.Surface) -> None:
        surface.blit(self._text_image, self._text_image.get_rect(**{self._anchor: self._position}))

    def update(self, delta: float) -> None:
        self._check_hover()
        self._check_time_to_deform()

class QuizInputBubble(TextSprite):
    def __init__(self, 
                 game, 
                 label: str = "Text", 
                 position: vec2 = vec2(0, 0), 
                 fontparams: FontParams = Font.none) -> None:
        
        super().__init__(game, label, position, "center", fontparams)
        self._inputbox = InputBox(game, label)
        self._inputbox.enabled = True
        self._cursor_rect = pygame.Rect((-1, -1), (1, self._text_image.get_rect().h))
        self._change_image()
        
        self._timer0 = Timer(0.5, True)
        self._timer1 = Timer(0.75, False)
        self._cursor_blinking = True

    @property
    def answer_index(self) -> str:
        return self._inputbox.text

    def draw_text(self, text: str) -> None:
        self._text_image = self._fontparams.get_render(text)

    def _change_image(self) -> None:
        self.image = random.choice(self.game.image.get("quiz_bubble_input"))
        self._change_position()

    def _draw_cursor(self, surface: pygame.Surface) -> None:
        rect = self._text_image.get_rect(**{self._anchor: self._position})
        x = rect.right - self._fontparams.get_font_size(self._inputbox.text[self._inputbox.cursor + 1:])[0]
        self._cursor_rect.midleft = (x, rect.centery)
        pygame.draw.rect(surface, BLACK, self._cursor_rect)

    def _handle_inputbox(self) -> None:
        self._inputbox.update()
        if self._inputbox.changed:
            self.draw_text(self._inputbox.text if self._inputbox.text != "" else self._inputbox.label)
            self._timer1.reset()                   ###############
            self._cursor_blinking = False          ###############

    def post_draw(self, surface: pygame.Surface) -> None:
        surface.blit(self._text_image, self._text_image.get_rect(**{self._anchor: self._position}))
        if self._cursor_blinking:                  ###############
            if time.time() % 1 > 0.5:              ###############
                self._draw_cursor(surface)         ###############
        else:                                      ###############
            self._draw_cursor(surface)             ###############

    def update(self, delta: float) -> None:
        self._handle_inputbox()

        if self._timer0.expired:
            self._change_image()

        if self._timer1.expired and not self._cursor_blinking: ###############
            self._cursor_blinking = True                       ###############

class QuizButtonBubble(QuizTextBubble):
    def __init__(self, 
                 game,
                 text: str = "Done", 
                 position: vec2 = vec2(0, 0), 
                 fontparams: FontParams = Font.none) -> None:
        
        super().__init__(game, 0, text, position, fontparams)
    
    def _change_bubble_image(self) -> None:
        if self._hover:
            self.image = self.game.image.get("quiz_next_question_hover")
        else:
            self.image = random.choice(self.game.image.get("quiz_next_question_idle"))
        self.rect = self.image.get_rect(**{self._anchor: self._position})

class QuizMenuBubble(ImageSprite):
    def __init__(self, 
                 game,
                 quiz,
                 index: int,
                 position: vec2 = vec2(0, 0), 
                 anchor: str = "center") -> None:

        super().__init__(game, pygame.Surface((400, 300)), position, anchor)
        self.index = index
        self._create_quiz_info(quiz)

    def _create_quiz_info(self, quiz) -> None:
        self.image.fill(ALT_BLU_3)
        self.image.set_alpha(240)

        back_image = pygame.transform.scale_by(self.game.image.get("hourglass").copy(), 2)
        back_image.set_alpha(50)

        self.image.blit(back_image, back_image.get_rect(bottomright = self.rect.bottomright))
        pygame.draw.rect(self.image, WHITE, self.rect, 2)

        font = self.game.font.get("menu_elem")
        
        title_image = font.get_render(quiz.title)
        title_rect = title_image.get_rect()
        questions_count_image = font.get_render(f"Questions: {quiz.questions_count}") 
        time_image = font.get_render(f"Total time: {quiz.get_qs_total_time(True)}")

        self._label = font.get_render("Click to start")

        self.image.blit(title_image, (10, 10))
        self.image.blit(questions_count_image, (10, title_rect.h + 25))
        self.image.blit(time_image, (10, title_rect.h + 55))
        pygame.draw.line(self.image, WHITE, (10, title_rect.h + 15), (390, title_rect.h + 15))
    
    def post_draw(self, surface: pygame.Surface) -> None:
        if self.mouse_in():
            surface.blit(self._label, self._label.get_rect(center=self.rect.midbottom - vec2(0, 30)))
