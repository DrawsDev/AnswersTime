import pygame
from copy import deepcopy
from pygame.locals import *
from scripts.objects import *
from scripts.tween import *
from scripts.utils import *
from scripts.questio import *
from scripts.settings import *
from scripts.timer import Timer
import time

class Scene:
    def __init__(self, game) -> None:
        self.game = game
        self.objects = pygame.sprite.Group()
        self.ready()
    
    def ready(self) -> None:
        pass
    
    def update(self, delta: float) -> None:
        self.objects.update(delta)

    def render(self, surface: pygame.Surface) -> None:
        self.objects.draw(surface)
        for object in self.objects.sprites():
            if hasattr(object, "post_draw"):
                object.post_draw(surface)
    
    def onEnter(self, *args) -> None:
        pass

    def onExit(self) -> None:
        pass

class Intro(Scene):
    def ready(self) -> None:
        self.game.font.create("b16cW", asset_path(f"{FONTS_DIR}Ramona-Bold.ttf"), 16, WHITE, FONT_CENTER)
        self.game.font.create("b16cG", asset_path(f"{FONTS_DIR}Ramona-Bold.ttf"), 16, (150, 150, 150), FONT_CENTER)
        self.game.font.create("b28center", asset_path(f"{FONTS_DIR}Ramona-Bold.ttf"), 28, WHITE, FONT_CENTER)
        self.game.font.create("bubble_1", asset_path(f"{FONTS_DIR}Ramona-Light.ttf"), 28, BLACK, FONT_CENTER, True, 340)
        self.game.font.create("bubble_2", asset_path(f"{FONTS_DIR}Ramona-Light.ttf"), 24, BLACK, FONT_CENTER)
        self.game.font.create("menu_elem", asset_path(f"{FONTS_DIR}Ramona-Bold.ttf"), 24, WHITE, FONT_LEFT, True, 380)
        self.game.image.load("logo", asset_path(f"{IMAGES_DIR}logo.png"))
        self.game.image.load("hourglass", asset_path(f"{IMAGES_DIR}hourglass.png"))
        self.game.image.load("etu", asset_path(f"{IMAGES_DIR}etu.png"))
        self.game.audio.load("space", asset_path(f"{SOUNDS_DIR}answers_time.wav"))
        self.game.audio.load("enter", asset_path(f"{SOUNDS_DIR}enter.wav"))
        self.game.audio.load("escape", asset_path(f"{SOUNDS_DIR}escape.wav"))
        self.game.audio.load("last_sec", asset_path(f"{SOUNDS_DIR}last_sec.wav"))
        self.game.audio.load("time_up", asset_path(f"{SOUNDS_DIR}time_up.wav"))

        screen_rect = self.game.screen.get_rect()

        self._starfield = Starfield(self.game)
        self._logo = ImageSprite(self.game, pygame.transform.scale_by(self.game.image.get("logo").copy(), 1.5), screen_rect.center, "center")
        self._label = TextSprite(self.game, "НАЖМИТЕ ЛЮБУЮ КНОПКУ ЧТОБЫ НАЧАТЬ", screen_rect.center + vec2(0, 250), "center", self.game.font.get("b16cW"))
        
        self._logo.image.set_alpha(0)
        self._label.image.set_alpha(0)
        self._label_offset = vec2(0, 250)

        self._timer0 = Timer(1, False)
        self._show_ui = False
        self._alpha_ui = 0
        self._active = True

    def _create_logo(self) -> None:
        if self._timer0.expired and not self._show_ui:
            self._show_ui = True
            self.objects.add(self._logo, self._label)
            self.game.audio.play("space", -1)
        
        if self._show_ui and self._alpha_ui < 255:
            self._alpha_ui += 5
            self._alpha_ui = min(self._alpha_ui, 255)
            self._logo.image.set_alpha(self._alpha_ui)
            self._label.image.set_alpha(self._alpha_ui)

    def update(self, delta: float) -> None:
        super().update(delta)

        self._create_logo()

        self._starfield.update()

        if self._active:
            self._logo.position = self.game.screen.get_rect().center + (self.game.screen.get_rect().center - vec2(pygame.mouse.get_pos())) / 10
            self._label.position = self.game.screen.get_rect().center + self._label_offset + ((self.game.screen.get_rect().center + self._label_offset) - vec2(pygame.mouse.get_pos())) / 10

            if self._timer0.expired and 0 <= self._label.image.get_alpha() < 255:
                alpha = self._label.image.get_alpha() + 6
                alpha = min(alpha, 255)
                self._label.image.set_alpha(alpha)

            if self.game.input.is_key_pressed("escape"):
                self.game.quit()
            
            if self.game.input.is_anything_pressed():
                if self._show_ui and self._alpha_ui >= 255:
                    self.game.change_scene("Menu")
                else:
                    self._timer0.stop()
                    self._alpha_ui = 254
        else:
            self._logo.position = self.game.screen.get_rect().center
            self._label.position = self.game.screen.get_rect().center + self._label_offset

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(BLU_5)
        self._starfield.render()

        super().render(surface)
    
    def onEnter(self) -> None:
        self._starfield.set_cursor_mode(True)
        self._active = True
        self._logo.image.set_alpha(255)
        self._timer0.reset()

    def onExit(self) -> None:
        self._starfield.set_cursor_mode(False)
        self._active = False
        self._logo.image.set_alpha(80)
        self._label.image.set_alpha(0)

class Menu(Scene):
    def ready(self) -> None:
        self._quizzes = create_quizzes()

        #for i, quiz in enumerate(self.quizzes):
            #self.objects.add(TextSprite(self.game, quiz.title, (30, 30 + 30 * i), fontparams=self.game.font.get("b28center")))

        screen_rect = self.game.screen.get_rect()
        self.objects.add(TextSprite(self.game, "Выберите тест", screen_rect.midtop + vec2(0, 20), "midtop", self.game.font.get("b28center")))

        self._create_menu_elements()

    def _create_menu_elements(self, start=vec2(30, 80), offset=vec2(10, 10)) -> None:
        column, row = 0, 0
        for index, quiz in enumerate(self._quizzes):
            menu_element = QuizMenuBubble(self.game, quiz, index, anchor="topleft")
            x = start.x + (menu_element.size.x + offset.x) * column
            y = start.y + (menu_element.size.y + offset.y) * row
            
            column += 1
            if column >= 3:
                column, row = 0, row + 1

            menu_element.position = (x, y)

            self.objects.add(menu_element)

    def update(self, delta: float) -> None:
        self.game.scenes["Intro"].update(delta)

        super().update(delta)
        
        if self.game.input.is_key_pressed("escape"):
            self.game.change_scene("Intro")
            self.game.audio.play("escape")

        if self.game.input.is_key_pressed("m_left"):
            for index, sprite in enumerate(self.objects.sprites()):
                if type(sprite) == QuizMenuBubble and sprite.mouse_in():
                    self.game.change_scene("Quiz", deepcopy(self._quizzes[sprite.index]))
                    self.game.audio.stop("space")

    def render(self, surface: pygame.Surface) -> None:
        self.game.scenes["Intro"].render(surface)

        super().render(surface)    
    
    def onEnter(self, *args) -> None:
        self.game.audio.play("enter")

class Quiz(Scene):
    def ready(self) -> None:
        self._quiz: Quiz = None
        self._answer_sprites = set()
        self._endgame_objects = set()

        #self.font_params1 = FontParams(asset_path("assets\\fonts\\Ramona-Bold.ttf"), 28, (255, 255, 255), FONT_CENTER, wraplenth=1000)
        #self.font_params2 = FontParams(asset_path("assets\\fonts\\Ramona-Light.ttf"), 28, (0, 13, 44), FONT_CENTER, wraplenth=340)
        #self.font_params3 = FontParams(asset_path("assets\\fonts\\Ramona-Light.ttf"), 28, (0, 13, 44), FONT_CENTER)
        
        self.game.audio.load("answer_click", asset_path("assets\\sounds\\answer_click.wav"))
        self.game.audio.load("answer_select", asset_path("assets\\sounds\\answer_select.wav"))
        self.game.audio.load("quiz_ended", asset_path("assets\\sounds\\quiz_ended.wav"))
        self.game.audio.load("quiz_start", asset_path("assets\\sounds\\quiz_start.wav"))

        self._create_sprites()

        self._ended = False
        self._timer1 = Timer(1, True)
        self._tween1 = Tween(-10, 20, 2, TweenStyle.ElasticInOut, -1, True)
        self._tween2 = Tween(0, 10, 1, TweenStyle.SineInOut, -1, True)
        self._tween1.play()
        self._tween2.play()

    def _create_sprites(self) -> None:
        screen_rect = self.game.screen.get_rect()

        hourglass_image = self.game.image.get("hourglass")
        hourglass_rect = hourglass_image.get_rect()
        self._hourglass = ImageSprite(self.game, hourglass_image, screen_rect.bottomright - vec2(100, 100))
        self._hg_img_copy = hourglass_image.copy()
        self._hg_pos_copy = self._hourglass.position
        
        etu_image = self.game.image.get("etu")
        etu_rect = etu_image.get_rect()
        self._etu = ImageSprite(self.game, etu_image, screen_rect.bottomleft + vec2(100, -100))
        self._etu_img_copy = etu_image.copy()
        self._etu_pos_copy = self._etu.position
        
        self._timelabel = TextSprite(self.game, "", self._hourglass.position - vec2(0, hourglass_rect.h / 1.5), "center", self.game.font.get("b28center"))

        self.objects.add(self._hourglass, self._etu, self._timelabel)

    def _get_points(self) -> list:
        points = []
        rect = self.game.screen.get_rect().center
        w, h = rect[0], rect[1]
        w_half, h_half = w / 2, h / 2

        match self._quiz.answers_count:
            case 2:
                points.append([w_half + 125, h - 35])
                points.append([w + w_half - 125, h - 35])
            case 3:
                points.append([w_half + 125, h - 35])
                points.append([w + w_half - 125, h - 35])
                points.append([w, h + h_half - 35])
            case 4: 
                points.append([w_half + 125, h - 35])
                points.append([w + w_half - 125, h - 35])
                points.append([w_half + 125, h + h_half - 35])
                points.append([w + w_half - 125, h + h_half - 35])
            case _: 
                points.append(rect)

        return points

    def _create_ingame_ui(self) -> None:
        Q = self._quiz.question
        Qi = self._quiz.question_index
        A = self._quiz.answers
        screen_rect = self.game.screen.get_rect()
        points = self._get_points()
        nextbuttontext = "Продолжить" if Qi + 1 != self._quiz.questions_count else "Завершить"

        self._timelabel.draw_text(str(self._quiz.question.duration - 1))

        self._answer_sprites.add(TextSprite(self.game, f"ВОПРОС {Qi + 1}", (screen_rect.centerx, 50), "center", self.game.font.get("b28center")))
        self._answer_sprites.add(TextSprite(self.game, Q.title, (screen_rect.centerx, 100), "center", self.game.font.get("b28center")))
        self._answer_sprites.add(QuizButtonBubble(self.game, nextbuttontext, (screen_rect.centerx, screen_rect.bottom - 80), self.game.font.get("bubble_1")))
        
        if Q.inputtable:
            self._answer_sprites.add(QuizInputBubble(self.game, "Введите ответ", screen_rect.center, self.game.font.get("bubble_2")))
        else:
            [self._answer_sprites.add(QuizTextBubble(self.game, i, a, points[i], self.game.font.get("bubble_1"))) for i, a in enumerate(A)]
        
        self.objects.add(self._answer_sprites)

    def _create_endgame_ui(self) -> None:
        Ac = self._quiz.correct_answers_count
        Qc = self._quiz.questions_count
        screen_rect = self.game.screen.get_rect()

        self._endgame_objects.add(QuizButtonBubble(self.game, "В меню", (screen_rect.centerx, screen_rect.bottom - 80), self.game.font.get("bubble_1")))
        self._endgame_objects.add(TextSprite(self.game, f"Правильных ответов: {Ac} из {Qc}", self.game.screen.get_rect().center, "center", self.game.font.get("b28center")))

        self.objects.add(self._endgame_objects)

    def _get_answer_from_inputbox(self) -> None:
        for sprite in self.objects.sprites():
            if type(sprite) == QuizInputBubble:
                self._quiz.get_answer(sprite.answer_index)

    def _clear_quiz_ui(self) -> None:
        self.objects.remove(self._answer_sprites)
        self.objects.remove(self._endgame_objects)
        self._answer_sprites.clear()
        self._endgame_objects.clear()

    def _refresh_ui(self) -> None:
        self._clear_quiz_ui()

        if not self._ended:
            self._quiz.next_question()
            self._create_ingame_ui()
            self._timelabel.draw_text(str(math.floor(self._quiz.time_left)))
            self._timer1.reset()

            if self._quiz.ended:
                self._ended = True
                self._clear_quiz_ui()
                self._create_endgame_ui()
                self._timelabel.draw_text("")
                self.game.audio.play("quiz_ended")

    def _check_objects_under_mouse(self) -> None:
        for sprite in self.objects.sprites():
            if sprite.rect.collidepoint(pygame.mouse.get_pos()):
                if type(sprite) == QuizTextBubble and not self._quiz.ended:
                    self._quiz.get_answer(sprite.answer_index)
                    self.game.audio.play("answer_click")
                    sprite.checked = not sprite.checked
                if type(sprite) == QuizButtonBubble:
                    if not self._ended:
                        self._get_answer_from_inputbox()
                        self._refresh_ui()
                        self.game.audio.play("answer_click")
                    else:
                        self.game.change_scene("Menu")

    def update(self, delta: float) -> None:
        super().update(delta)

        self._tween1.update()
        self._tween2.update()
        self._hourglass.image = pygame.transform.rotate(self._hg_img_copy, self._tween1.value)
        self._hourglass.position = self._hg_pos_copy - vec2(self._tween1.value / 2, 0)
        self._etu.image = pygame.transform.scale(self._etu_img_copy, vec2(self._etu_img_copy.get_rect().size) - vec2(-self._tween2.value, self._tween2.value))
        self._etu.position = self._etu_pos_copy + vec2(0, self._tween2.value)

        if self._timer1.expired and not self._ended:
            self._timelabel.draw_text(str(math.floor(self._quiz.time_left)))

            if 0 < self._quiz.time_left <= 10:
                self.game.audio.play("last_sec")
        
        if self._quiz.time_left <= 0 and not self._ended:
            self._get_answer_from_inputbox()
            self._refresh_ui()
            self.game.audio.play("time_up")

        if self.game.input.is_key_pressed("escape"):
            self.game.change_scene("Menu")

        if self.game.input.is_key_pressed("m_left") and self._quiz:
            self._check_objects_under_mouse()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(ALT_BLU_5)

        super().render(surface)

    def onEnter(self, *args) -> None:
        self._quiz = args[0]
        self._quiz.time_left = time.time()
        self._create_ingame_ui()
        self._timer1.reset()
        self.game.audio.play("quiz_start")
    
    def onExit(self) -> None:
        self._quiz = None
        self._ended = False
        self._clear_quiz_ui()
        self.game.audio.stop("quiz_start")
        self.game.audio.play("space", -1)

__all__ = ["Intro", "Menu", "Quiz"]
