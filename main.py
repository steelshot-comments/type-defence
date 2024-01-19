import pygame, csv
from pygame import mixer
from itertools import chain
from pygame.locals import *
from math import hypot, cos, sin, atan2, pi, trunc
from random import choice, uniform

pygame.init()
mixer.init()

# Setting up audio files
ch0 = pygame.mixer.Channel(0)
ch1 = pygame.mixer.Channel(1)
ch2 = pygame.mixer.Channel(2)

# start_audio = pygame.mixer.Sound('assets/audio/fx/start-level.wav')
lobby_music = pygame.mixer.Sound('assets/audio/slow-travel.wav')
battle_music = pygame.mixer.Sound('assets/audio/battle.wav')
end_music = pygame.mixer.Sound('assets/audio/meet-the-princess.wav')

ch0.play(lobby_music, loops=-1, fade_ms=1000)

# extracting letter patterns from csv file
file = open("letters.csv", "r")
data = list(csv.reader(file, delimiter=","))
letters = list(chain.from_iterable(data))
file.close()

# GLOBAL VARIABLES
dt, total_keys, correct_keys, wpm, accuracy, awpm, index = 0, 0, 0, 0, 0, 0, 0
running = True
game_state = "menu"
difficulty = 20

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# create the window and clock
screen = pygame.display.set_mode((720, 720))
pygame.display.set_caption('Type defense')
width, height = pygame.display.get_window_size()
clock = pygame.time.Clock()

# SETTING THE FONT SIZE AND FAMILY
pygame.font.init()
font = pygame.font.SysFont('arialblack', 30)

class Player(pygame.sprite.Sprite):
    def __init__(self, sprite_sheet):
        pygame.sprite.Sprite.__init__(self)
        self.x = width/2
        self.y = height/2
        self.radius = 30 * 2
        self.sprite_sheet = sprite_sheet
        self.frames = [0, ] * 77
        self.frameX = 12
        self.create_frames()

    def create_frames(self):
        for i in range(77):
            img = pygame.Surface((72, 72)).convert_alpha()
            img.blit(self.sprite_sheet, (0, 0), (self.frameX, 12, 72, 72))
            img.set_colorkey(BLACK)
            self.frames[i] = img
            self.frameX += 96

    def draw(self):
        if self.frameX < 76:
            self.frameX += 1
        else:
            self.frameX = 0

        screen.blit(self.frames[self.frameX], (self.x-36, self.y-36))

enemies = []
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed, img, letter):
        pygame.sprite.Sprite.__init__(self)
        self.destroy = False
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.sprite = pygame.transform.rotate(pygame.image.load('assets/asteroids/asteroid.png'), angle*180/pi)
        self.explosion_sprite = pygame.image.load('assets/asteroids/explode.png')
        self.frames = [0, ] * 7
        self.frameX = 0
        self.letter = letter
        self.create_frames()

    def create_frames(self):
        for i in range(7):
            img = pygame.Surface((96, 96)).convert_alpha()
            img.blit(self.explosion_sprite, (0, 0), (self.frameX, 0, 96, 96))
            img = pygame.transform.rotate(img, self.angle*180/pi)
            img.set_colorkey((0, 0, 0))
            self.frames[i] = img
            self.frameX += 96
        self.frameX = 0

    def draw(self, color):
        screen.blit(self.sprite, (self.x-15, self.y-15))
        text = font.render(self.letter, True, color)
        screen.blit(text, (self.x+38, self.y+38))

    def update(self, dt, color):
        self.x += cos(self.angle) * self.speed * dt
        self.y += sin(self.angle) * self.speed * dt
        self.draw(color)

    def explode(self):
        global running, enemies
        if self.frameX < 5:
            self.frameX += 1/5
        else:
            return True
        self.x += cos(self.angle) * self.speed * dt
        self.y += sin(self.angle) * self.speed * dt
        screen.blit(self.frames[trunc(self.frameX)], (self.x-15, self.y-15))
        return False

# function to add enemies
def addEnemy():
    global index, letters
    x = uniform(-200, width+200)
    if(x > 0 and x < width):
        y = choice([0, height])
    else:
        y = uniform(0, height)
    angle = atan2(height/2 - (y+48), width/2 - (x+48))
    letter = letters[index]
    enemies.append(Enemy(x, y, angle, 0.1, pygame.image.load('assets/asteroids/asteroid_resized.png'), letter))
    index += 1

class Button:
    def __init__(self, text, width, height, pos):
        self.top_rect = pygame.Rect((pos[0] - width/2, pos[1], width, height))
        self.top_color = '#475f77'
        self.text_surf = font.render(text, True, '#ffffff')
        self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.top_rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        pygame.draw.rect(screen, self.top_color, self.top_rect, border_radius=12)
        screen.blit(self.text_surf, self.text_rect)
        return action

# Load backgrounds
bg = pygame.image.load('assets/backgrounds/blue_nebula.png').convert()
bg = pygame.transform.scale(bg, (width, width))

end_bg = pygame.image.load('assets/backgrounds/main_menu.png').convert()
end_bg = pygame.transform.scale(end_bg, (width, width))

menu_bg = pygame.image.load('assets/backgrounds/main_menu.png').convert()
menu_bg = pygame.transform.scale(menu_bg, (width, width))

main_bg = pygame.image.load('assets/backgrounds/main_menu.png').convert()
main_bg = pygame.transform.scale(main_bg, (width, width))

options_bg = pygame.image.load('assets/backgrounds/options_bg.png').convert()
options_bg = pygame.transform.scale(options_bg, (width, width))

# create player object
player_sprite = pygame.image.load('assets/planets/earth_w_glow.png').convert()
player = Player(player_sprite)

# create button objects
play_btn = Button('play', 120, 50, (width/2, 250))
resume_btn = Button('resume', 120, 50, (width/2, 250))
restart_btn = Button('restart', 120, 50, (width/2, height/2 + 30))
options_btn = Button('options', 120, 50, (width/2, height/2))
exit_btn = Button('exit', 120, 50, (width/2, height-250))
back_btn = Button('back', 120, 50, (width/2, height/2))
quit_btn = Button('quit', 120, 50, (width/2, height/2 + 120))

def main_menu():
    global game_state, running

    ch1.pause()
    ch0.unpause()

    screen.blit(main_bg, (0, 0))

    if play_btn.draw():
        game_state = "play"
    if options_btn.draw():
        game_state = "options"
    if exit_btn.draw():
        running = False

def play_screen():
    dt = clock.tick(60)

    if ch2.get_busy():
        ch2.fadeout(1000)
    ch0.fadeout(1000)
    if ch1.get_busy():
        ch1.unpause()
    else:
        ch1.play(battle_music, loops=-1, fade_ms=1000)

    global total_keys, game_state, difficulty, accuracy, wpm

    if pygame.time.get_ticks()%30000 < 30:
        difficulty += 5

    # Spawn a new enemy at difficulty interval
    if pygame.time.get_ticks() % 1000 < difficulty:
        addEnemy()

    screen.blit(bg, (0, 0))
    # text_surface = font.render(''.join(letters[:7]), True, WHITE)
    # Display the text at the top of the screen
    # text_rect = text_surface.get_rect(center=(width // 2, height // 4))
    # screen.blit(text_surface, text_rect)
    player.draw()

    for enemy in enemies:
        if hypot(width/2 - (enemy.x + 48), height/2 - (enemy.y+48)) <= 48:
            game_state = "end"
        if enemy == enemies[0]:
            color = (0, 255, 0)
        else:
            color = WHITE
        if enemy.destroy == False:
            enemy.update(dt, color)
        else:
            if enemy.explode():
                enemies.remove(enemy)

    pygame.draw.rect(screen, (BLACK), pygame.Rect(0, 0, 120, 50))
    wpm = round((total_keys/5)/(pygame.time.get_ticks()/60000), 2)
    if total_keys == 0:
        accuracy = 100
    else:
        accuracy = round(correct_keys/total_keys * 100, 2)
    words_per_min = font.render(f"{wpm} wpm", True, WHITE)
    screen.blit(words_per_min, (0, 0))
    acc = font.render(f"{accuracy}%", True, WHITE)
    screen.blit(acc, (0, 20))

def check_key(key):
    global correct_keys, total_keys, enemies
    if len(enemies) > 0:
        total_keys += 1
        if key == enemies[0].letter:
            correct_keys += 1
            enemies[0].destroy = True

def pause_menu():
    global running, game_state

    ch1.fadeout(1000)
    if ch0.get_busy():
        ch0.unpause()
    else:
        ch0.play(lobby_music, loops=-1, fade_ms=1000)

    screen.blit(menu_bg, (0, 0))

    if resume_btn.draw():
        game_state = "play"
    if options_btn.draw():
        game_state = "options"
    if exit_btn.draw():
        running = False

def options_screen():
    global game_state

    screen.blit(options_bg, (0, 0))

    if back_btn.draw():
        game_state = "menu"

def restart():
    global enemies, wpm, accuracy, dt, total_keys, correct_keys, awpm, index, game_state
    enemies = []
    wpm, accuracy, dt, total_keys, correct_keys, awpm, index = 0, 0, 0, 0, 0, 0, 0
    game_state = "play"

def end_screen():
    global wpm, accuracy, running

    ch1.fadeout(1000)
    if ch2.get_busy():
        ch2.unpause()
    else:
        ch2.play(end_music, loops=-1, fade_ms=1000)

    awpm = round(wpm * (accuracy/100), 2)
    screen.blit(end_bg, (0, 0))
    pygame.draw.rect(screen, (15, 46, 79), pygame.Rect(100, height/2 - 140, 500, 320))
    words = font.render(f"Words per minute = {wpm}", True, (112, 181, 255))
    acc = font.render(f"Accuracy = {accuracy}", True, (112, 181, 255))
    adj = font.render(f"Adjusted words per minute = {awpm}", True, (112, 181, 255))
    screen.blit(words, (110, height/2 - 120))
    screen.blit(acc, (110, height/2 - 90))
    screen.blit(adj, (110, height/2 - 60))
    if restart_btn.draw():
        restart()
    if quit_btn.draw():
        running = False

# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key)
            if key == "escape":
                if game_state == "play":
                    game_state = "pause"
                elif game_state == "pause":
                    game_state = "play"
            elif key.isalpha():
                check_key(key)

    if game_state == "menu":
        main_menu()
    elif game_state == "pause":
        pause_menu()
    elif game_state == "options":
        options_screen()
    elif game_state == "play":
        play_screen()
    elif game_state == "end":
        end_screen()
    pygame.display.update()

pygame.quit()