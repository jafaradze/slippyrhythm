import pygame
from constants import *
import random
import sqlite3


score = 5

note_frames = {'g': [pygame.image.load('data/notes/note_green1.png'),
                     pygame.image.load('data/notes/note_green2.png'),
                     pygame.image.load('data/notes/note_green3.png'),
                     pygame.image.load('data/notes/note_green4.png'),
                     pygame.image.load('data/notes/note_green5.png')],
               'p': [pygame.image.load('data/notes/note_purple1.png'),
                     pygame.image.load('data/notes/note_purple2.png'),
                     pygame.image.load('data/notes/note_purple3.png'),
                     pygame.image.load('data/notes/note_purple4.png'),
                     pygame.image.load('data/notes/note_purple5.png')],
               'r': [pygame.image.load('data/notes/note_red1.png'),
                     pygame.image.load('data/notes/note_red2.png'),
                     pygame.image.load('data/notes/note_red3.png'),
                     pygame.image.load('data/notes/note_red4.png'),
                     pygame.image.load('data/notes/note_red5.png')],
               'y': [pygame.image.load('data/notes/note_yellow1.png'),
                     pygame.image.load('data/notes/note_yellow2.png'),
                     pygame.image.load('data/notes/note_yellow3.png'),
                     pygame.image.load('data/notes/note_yellow4.png'),
                     pygame.image.load('data/notes/note_yellow5.png')]}


class Note(pygame.sprite.Sprite):
    def __init__(self, color):
        super().__init__()
        self.color = color
        self.frames = note_frames[self.color]
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        match self.color:
            case 'g':
                self.rect.center = (200, 100)
                self.sound = pygame.mixer.Sound('data/sounds/FIRST.mp3')
            case 'p':
                self.rect.center = (400, 100)
                self.sound = pygame.mixer.Sound('data/sounds/SECOND.mp3')
            case 'r':
                self.rect.center = (600, 100)
                self.sound = pygame.mixer.Sound('data/sounds/THIRD.mp3')
            case 'y':
                self.rect.center = (800, 100)
                self.sound = pygame.mixer.Sound('data/sounds/FOURTH.mp3')
            case _:
                raise ValueError('Color string must be "g", "p", "r" or "y", not {self.color}')
        self.speed = 10
        self.animation_speed = 0.2
        self.last_update = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            global score
            score -= 1
            print(score)
            message.set_image('Miss')
            self.kill()

        now = pygame.time.get_ticks()
        if now - self.last_update > 1000 / FPS:
            self.last_update = now
            self.current_frame = (self.current_frame + self.animation_speed) % len(self.frames)
            self.image = self.frames[int(self.current_frame)]

    def get_color(self):
        return self.color
    
    def get_rect(self):
        return self.rect
    
    def play_sound(self):
        self.sound.play()


rhythmline_frames = {'g': [pygame.image.load('data/rhythmline/rhythmline_green1.png'),
                           pygame.image.load('data/rhythmline/rhythmline_green2.png')],
                     'p': [pygame.image.load('data/rhythmline/rhythmline_purple1.png'),
                           pygame.image.load('data/rhythmline/rhythmline_purple2.png')],
                     'r': [pygame.image.load('data/rhythmline/rhythmline_red1.png'),
                           pygame.image.load('data/rhythmline/rhythmline_red2.png')],
                     'y': [pygame.image.load('data/rhythmline/rhythmline_yellow1.png'),
                           pygame.image.load('data/rhythmline/rhythmline_yellow2.png')]}


class RhytmLine(pygame.sprite.Sprite):
    def __init__(self, color):
        super().__init__()
        self.color = color
        self.frames = rhythmline_frames[self.color]
        self.pressed = False
        self.image = self.frames[0] 
        self.rect = self.image.get_rect()
        match self.color:
            case 'g':
                self.rect.center = (200, 620)
            case 'p':
                self.rect.center = (400, 620)
            case 'r':
                self.rect.center = (600, 620)
            case 'y':
                self.rect.center = (800, 620)
            case _:
                raise ValueError('Color string must be "g", "p", "r" or "y", not {self.color}')
            
    def set_pressed(self, pressed, notes_sprites):
        self.pressed = pressed
        if self.pressed:
            self.image = self.frames[1]
            self.check_note_proximity(notes_sprites)
        else:
            self.image = self.frames[0]

    def check_note_proximity(self, notes_sprites):
        closest_note = None
        closest_distance = float('inf')
        for note in notes_sprites:
            if note.get_color() == self.color:
                distance = abs(note.get_rect().y - self.rect.y)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_note = note

        if closest_note:
            global score
            if closest_distance <= PERFECT_THRESHOLD:
                closest_note.play_sound()
                message.set_image('Perfect')
                score += 3
                closest_note.kill()
            elif closest_distance <= GOOD_THRESHOLD:
                closest_note.play_sound()
                message.set_image('Good')
                score += 2
                closest_note.kill()
            elif closest_distance <= OKAY_THRESHOLD:
                closest_note.play_sound()
                message.set_image('Okay')
                score += 1
                closest_note.kill()
            else:
                message.set_image('Miss')
                score -= 1
            print(score)


message_frames = {'Perfect': pygame.image.load('data/message/perfect.png'),
                  'Good': pygame.image.load('data/message/good.png'),
                  'Okay': pygame.image.load('data/message/okay.png'),
                  'Miss': pygame.image.load('data/message/miss.png'),
                  'Letsgo': pygame.image.load('data/message/letsgo.png')}


class Message(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = message_frames
        self.image = self.frames['Letsgo']
        self.rect = self.image.get_rect()
        self.rect.topleft = (300, 700)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def set_image(self, index):
        self.image = self.frames[index]


class MainMenu:
    def __init__(self):
        self.background = pygame.image.load('data/menu.png')
        self.buttons = pygame.sprite.Group()
        self.create_buttons()

    def create_buttons(self):
        start_button_frames = [pygame.image.load('data/buttons/start/start1.png'), 
                               pygame.image.load('data/buttons/start/start2.png')]
        start_button = Button(start_button_frames, (525, 375), self.start_game)
        self.buttons.add(start_button)

        highscore_button_frames = [pygame.image.load('data/buttons/highscore/highscore1.png'), 
                                   pygame.image.load('data/buttons/highscore/highscore2.png')]
        highscore_button = Button(highscore_button_frames, (520, 470), self.show_high_score)
        self.buttons.add(highscore_button)

        quit_button_frames = [pygame.image.load('data/buttons/quit/quit1.png'), 
                              pygame.image.load('data/buttons/quit/quit2.png')]
        quit_button = Button(quit_button_frames, (600, 600), self.quit_game)
        self.buttons.add(quit_button)

    def start_game(self):
        global state
        state = 'play'

    def show_high_score(self):
        global state
        state = 'highscore'

    def quit_game(self):
        global running
        running = False

    def update(self, events):
        self.buttons.update(events)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        self.buttons.draw(screen)


class Button(pygame.sprite.Sprite):
    def __init__(self, frames, pos, callback):
        super().__init__()
        self.frames = frames
        self.image = frames[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.callback = callback

    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.callback()
            elif event.type == pygame.MOUSEMOTION:
                if self.rect.collidepoint(event.pos):
                    self.image = self.frames[1]
                else:
                    self.image = self.frames[0]


digits = [pygame.image.load('data/digits/0.png'),
          pygame.image.load('data/digits/1.png'),
          pygame.image.load('data/digits/2.png'),
          pygame.image.load('data/digits/3.png'),
          pygame.image.load('data/digits/4.png'),
          pygame.image.load('data/digits/5.png'),
          pygame.image.load('data/digits/6.png'),
          pygame.image.load('data/digits/7.png'),
          pygame.image.load('data/digits/8.png'),
          pygame.image.load('data/digits/9.png')]


class Score(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        global score
        self.frames = digits
        self.images = [self.frames[score]]

    def update(self):
        global score
        if score <= 0:
            self.images = [self.frames[0]]
            return
        self.images = []
        for digit in str(score):
            self.images.append(self.frames[int(digit)])

    def draw(self, screen):
        x = WIDTH
        for image in self.images[::-1]:
            rect = image.get_rect(bottomright=(x, 800))
            screen.blit(image, rect)
            x -= 60


class PauseMenu:
    def __init__(self):
        self.background = pygame.Surface((WIDTH, HEIGHT))
        self.background.set_alpha(128)
        self.background.fill((0, 0, 0))
        self.buttons = pygame.sprite.Group()
        save_quit_button_frames = [pygame.image.load('data/buttons/save_quit/save_quit1.png'), 
                                   pygame.image.load('data/buttons/save_quit/save_quit2.png')]
        save_quit_button = Button(save_quit_button_frames, (330, 300), self.save_and_quit)
        self.buttons.add(save_quit_button)
        self.message = pygame.image.load('data/pause/pause.png')
        self.message_rect = self.message.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 200))

    def save_and_quit(self):
        global running, score
        player_name = self.ask_for_name(screen)
        if player_name:
            self.save_scores(player_name, score)
            running = False
            
    def save_scores(self, player_name, score):
        con = sqlite3.connect('results.sqlite')
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS scores
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          name TEXT, 
                          score INTEGER)''')
        cur.execute('INSERT INTO scores (name, score) VALUES (?, ?)', (player_name, score))
        con.commit()
        con.close()

    def ask_for_name(self, screen):
        image = pygame.image.load('data/background.png')
        image_rect = image.get_rect(topleft=(0, 0))
        font = pygame.font.Font(None, 74)
        input_box = pygame.Rect(400, 400, 340, 74)
        color_inactive = pygame.Color(LIGHTBLUE)
        color_active = pygame.Color(DARKBLUE)
        color = color_inactive
        active = False
        name = ''
        done = False
        enter_name = pygame.image.load('data/enter_name.png')
        enter_name_rect = enter_name.get_rect(center=(500, 200))

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        active = not active
                    else:
                        active = False
                    if active:
                        color = color_active
                    else:
                        color_inactive
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            return name
                        elif event.key == pygame.K_BACKSPACE:
                            name = name[:-1]
                        else:
                            name += event.unicode
            screen.blit(image, image_rect)
            name_surface = font.render(name, True, color)
            width = max(200, name_surface.get_width()+10)
            input_box.w = width
            screen.blit(name_surface, (input_box.x+5, input_box.y+5))
            pygame.draw.rect(screen, color, input_box, 2)
            screen.blit(enter_name, enter_name_rect)

            pygame.display.flip()

    def update(self, events):
        self.buttons.update(events)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        screen.blit(self.message, self.message_rect)
        self.buttons.draw(screen)


class HighScoreMenu:
    def __init__(self):
        self.background = pygame.image.load('data/background.png')
        self.font = pygame.font.Font(None, 36)
        self.buttons = pygame.sprite.Group()
        back_button_frames = [pygame.image.load('data/buttons/back/back1.png'), 
                              pygame.image.load('data/buttons/back/back2.png')]
        back_button = Button(back_button_frames, (0, 0), self.back_to_menu)
        self.buttons.add(back_button)

    def back_to_menu(self):
        global state
        state = 'menu'

    def fetch_scores(self):
        con = sqlite3.connect('results.sqlite')
        cur = con.cursor()
        cur.execute('SELECT name, score FROM scores ORDER BY score DESC LIMIT 10')
        scores = cur.fetchall()
        con.close()
        return scores

    def update(self, events):
        self.buttons.update(events)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        scores = self.fetch_scores()
        y = 100
        for name, score in scores:
            text = f'{name}: {score}'
            text_surface = self.font.render(text, True, pygame.Color('white'))
            screen.blit(text_surface, (100, y))
            y += 40
        self.buttons.draw(screen)


pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))

slippy = pygame.image.load('data/slippy.png')

all_sprites = pygame.sprite.Group()
notes_sprites = pygame.sprite.Group()
line_sprites = pygame.sprite.Group()

line_green = RhytmLine('g')
line_purple = RhytmLine('p')
line_red = RhytmLine('r')
line_yellow = RhytmLine('y')
all_sprites.add(line_green)
all_sprites.add(line_purple)
all_sprites.add(line_red)
all_sprites.add(line_yellow)
line_sprites.add(line_green)
line_sprites.add(line_purple)
line_sprites.add(line_red)
line_sprites.add(line_yellow)

message = Message()
all_sprites.add(message)

score_ui = Score()
all_sprites.add(score_ui)

main_menu = MainMenu()
pause_menu = PauseMenu()
highscore_menu = HighScoreMenu()

running = True
clock = pygame.time.Clock()
note_timer = pygame.USEREVENT + 1
pygame.time.set_timer(note_timer, 1000)

state = 'menu'

while running:
    clock.tick(FPS)
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if state == 'play':
                state = 'pause'
            elif state == 'pause':
                state = 'play'

    if state == 'menu':
        main_menu.update(events)
        main_menu.draw(screen)
    elif state == 'play':
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == note_timer:
                color = random.choice(['g', 'p', 'r', 'y'])
                note = Note(color)
                all_sprites.add(note)
                notes_sprites.add(note)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    line_green.set_pressed(True, notes_sprites)
                elif event.key == pygame.K_s:
                    line_purple.set_pressed(True, notes_sprites)
                elif event.key == pygame.K_j:
                    line_red.set_pressed(True, notes_sprites)
                elif event.key == pygame.K_k:
                    line_yellow.set_pressed(True, notes_sprites)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    line_green.set_pressed(False, notes_sprites)
                elif event.key == pygame.K_s:
                    line_purple.set_pressed(False, notes_sprites)
                elif event.key == pygame.K_j:
                    line_red.set_pressed(False, notes_sprites)
                elif event.key == pygame.K_k:
                    line_yellow.set_pressed(False, notes_sprites)
            
        all_sprites.update()

        screen.fill(WHITE)
        notes_sprites.draw(screen)
        line_sprites.draw(screen)
        message.draw(screen)
        screen.blit(slippy, (0, 0))
        score_ui.draw(screen)
    elif state == 'pause':
        screen.fill(WHITE)
        notes_sprites.draw(screen)
        line_sprites.draw(screen)
        message.draw(screen)
        screen.blit(slippy, (0, 0))
        score_ui.draw(screen)

        pause_menu.update(events)
        pause_menu.draw(screen)
    elif state == 'highscore':
        highscore_menu.update(events)
        highscore_menu.draw(screen)

    pygame.display.flip()


pygame.quit()