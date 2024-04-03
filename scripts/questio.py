import random
from time import time, strftime, gmtime
from pygame import Surface, draw, transform
from pygame.math import Vector2 as vec2
from scripts.utils import *
from scripts.settings import *

class Question:
    def __init__(self, 
                 title: str = "NewQuestion", 
                 answers: list = [["right"], ["wrong"]], 
                 duration: int = 20,
                 explain: str = "right is right",
                 inputtable: bool = False) -> None:
        self._title = title
        self._answers = answers
        self._duration = duration
        self._explain = explain
        self._inputtable = inputtable
    
    @property
    def title(self) -> str:
        return self._title

    @property
    def duration(self) -> int:
        return self._duration
    
    @property
    def answers(self) -> list:
        return self._answers
    
    @property
    def inputtable(self) -> bool:
        return self._inputtable

class Quiz:
    def __init__(self, 
                 title: str = "NewTest",
                 questions: list = []) -> None:
        self._title = title
        self._questions = questions
        self._question_index = 0
        self._correct_answers_count = 0
        self._question_start_time = 0
        self._merge_result = []
        self._ended = False
        self._explained = False
        self._answers_received = []

        self._shuffle_answers()
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def questions(self) -> list:
        return self._questions
    
    @property
    def questions_count(self) -> int:
        return len(self._questions)

    @property
    def question_index(self) -> int:
        return self._question_index

    @property
    def question(self) -> dict:
        if self._question_index >= len(self._questions):
            return self._questions[-1]
        return self._questions[self._question_index]

    @property
    def answers(self) -> list:
        return self._merge_result

    @property
    def answers_count(self) -> int:
        return len(self._merge_result)

    @property
    def correct_answers_count(self) -> int:
        return self._correct_answers_count

    @property
    def time_left(self) -> float:
        return self.question.duration - (time() - self._question_start_time)

    @time_left.setter
    def time_left(self, value: float) -> None:
        self._question_start_time = time()

    @property
    def ended(self) -> bool:
        return self._ended

    @property
    def explained(self) -> bool:
        return self._explained

    def get_qs_total_time(self, in_str=False) -> int | str:
        total_time = 0
        for i in self._questions:
            total_time += i.duration
        
        return strftime("%H`%M`%S", gmtime(total_time)) if in_str else total_time

    def _shuffle_answers(self) -> None:
        answers = self.question.answers
        self._merge_result = answers[0] + answers[1]
        random.shuffle(self._merge_result)

    def _check_answer(self) -> None:
        if time() - self._question_start_time > self.question.duration + 1:
            return

        correct = 0
        wrong = 0
        for answer in self._answers_received:
            if type(answer) == int:
                if self._merge_result[answer] in self.question.answers[0]:
                    correct += 1
                else:
                    wrong += 1
            if type(answer) == str:
                if answer.lower().replace(" ", "") in [i.lower().replace(" ", "") for i in self.question.answers[0]]:
                    self._correct_answers_count += 1
                else:
                    wrong = 1
        
        if correct == len(self.question.answers[0]) and wrong == 0:
            self._correct_answers_count += 1

    def get_answer(self, answer: int | str) -> None:
        answer_type = type(answer)
        answer_inputtable = self.question.inputtable

        if (answer_type is int) and (not answer_inputtable)\
        or (answer_type is str) and (answer_inputtable):
            if answer in self._answers_received:
                self._answers_received.remove(answer)
            else:
                self._answers_received.append(answer)

    def next_question(self) -> None:
        if self._ended: return

        if self._question_index == len(self._questions) - 1:
            self._ended = True

        self._check_answer()
        self._question_index += 1
        self._answers_received.clear()
        self._question_start_time = time()
        self._shuffle_answers()

def create_quizzes():
    files = get_files_from(asset_path("data"))
    quizzes = []
    for file in files:
        data = read_json(asset_path(f"data\\{file}"))
        questions = []
        for question in data["questions"]:
            title = question["title"]
            right = question["answers"]["right"]
            wrong = question["answers"]["wrong"]

            if len(right + wrong) > 4 or len(right + wrong) <= 0:
                continue

            duration = question["duration"]
            explain = question["explain"]
            inputtable = question.get("inputtable", False)
            questions.append(Question(title, [right, wrong], duration, explain, inputtable))
        quizzes.append(Quiz(data["title"], questions))
    return quizzes

def draw_quiz_bubbles(game):
    def _create_bubble(size, color1, color2, check=False, wasd=False):
        size = vec2(size)
        p0 = vec2(0, 0) #(10 + random.randrange(-5, 5), 10 + random.randrange(-5, 5))
        p1 = vec2(size.x, 0) #(size[0] - 10 + random.randrange(-5, 5), 10 + random.randrange(-5, 5))
        p2 = vec2(size.x, size.y)#(size[0] - 10 + random.randrange(-5, 5), size[1] - 10 + random.randrange(-5, 5))
        p3 = vec2(0, size.y)#(10 + random.randrange(-5, 5), size[1] - 10 + random.randrange(-5, 5))

        image = Surface(size)
        image.set_colorkey((0, 0, 0))
        #draw.polygon(image, color1, [(p0[0] - 10, p0[1] - 10), p1, (p2[0] + 10, p2[1] + 10), p3])
        #draw.polygon(image, color2, [p0, p1, p2, p3])

        r0 = random.randrange(-5, 0)
        r1 = random.randrange(-5, 0)
        r2 = random.randrange(-5, 0)
        r3 = random.randrange(-5, 0)

        draw.polygon(image, WHITE, [p0 + vec2(-r0, -r1), p1 + vec2(-12 + r2, 12 - r3), p2 + vec2(r0, r1), p3 + vec2(12 - r0, -12 + r2)])
        draw.polygon(image, color1, [p0 + vec2(4 - r0, 4 - r1), p1 + vec2(-16 + r2, 16 - r3), p2 + vec2(-4 + r0, -4 + r1), p3 + vec2(16 - r0, -16 + r2)])
        draw.polygon(image, color2, [p0 + vec2(16 - r0, 16 - r1), p1 + vec2(-16 + r2, 16 - r3), p2 + vec2(-16 + r0, -16 + r1), p3 + vec2(16 - r0, -16 + r2)])

        if check:
            check_image = game.image.get("check")
            check_rect = check_image.get_rect()
            startpos = image.get_rect().topright
            image.blit(check_image, (startpos[0] - check_rect.w, startpos[1]))

        if wasd:
            for _ in range(1):
                wasd_image = transform.scale_by(game.image.get("wasd").copy(), random.uniform(0.5, 2.5))
                bubble_rect = image.get_rect()
                x = random.uniform(10, bubble_rect.w - 10)
                y = random.uniform(10, bubble_rect.h - 10)
                wasd_rect = wasd_image.get_rect(center = (x, y))
                image.blit(wasd_image, wasd_rect)

        return image

    game.image.load("check", asset_path(f"{IMAGES_DIR}check.png"))
    game.image.load("wasd", asset_path(f"{IMAGES_DIR}wasd.png"))    
    game.image.add("quiz_bubble_idle", [_create_bubble((380, 170), BLU_4, BLU_1) for _ in range(3)])
    game.image.add("quiz_bubble_hover", _create_bubble((390, 180), BLU_3, BLU_0))
    game.image.add("quiz_bubble_idle_check", [_create_bubble((380, 170), GRE_4, GRE_2, True) for _ in range(3)])
    game.image.add("quiz_bubble_hover_check", _create_bubble((390, 180), GRE_3, GRE_1, True))
    game.image.add("quiz_next_question_idle", [_create_bubble((260, 80), BLU_4, BLU_1) for _ in range(3)])
    game.image.add("quiz_next_question_hover", _create_bubble((270, 90), BLU_3, BLU_0))
    game.image.add("quiz_bubble_input", [_create_bubble((780, 100), BLU_4, BLU_1) for _ in range(3)])