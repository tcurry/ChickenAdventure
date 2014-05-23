#! /usr/bin/env python


import pygame
import random
from pygame.locals import *
import sys

SCREEN_SIZE = (1280, 720) #resolution of the game
global HORIZ_MOV_INCR
HORIZ_MOV_INCR = 20 #speed of movement
global FPS
global clock
global time_spent
score = -2

def RelRect(actor, camera):
    return pygame.Rect(actor.rect.x-camera.rect.x, actor.rect.y-camera.rect.y, actor.rect.w, actor.rect.h)

class Camera(object):
    '''Class for center screen on the player'''
    def __init__(self, screen, player, level_width, level_height):
        self.player = player
        self.rect = screen.get_rect()
        self.rect.center = self.player.center
        self.world_rect = Rect(0, 0, level_width, level_height)

    def update(self):
      if self.player.centerx > self.rect.centerx + 25:
          self.rect.centerx = self.player.centerx - 25
      if self.player.centerx < self.rect.centerx - 25:
          self.rect.centerx = self.player.centerx + 25
      if self.player.centery > self.rect.centery + 25:
          self.rect.centery = self.player.centery - 25
      if self.player.centery < self.rect.centery - 25:
          self.rect.centery = self.player.centery + 25
      self.rect.clamp_ip(self.world_rect)

    def draw_sprites(self, surf, sprites):
        for s in sprites:
            if s.rect.colliderect(self.rect):
                surf.blit(s.image, RelRect(s, self))


class Obstacle(pygame.sprite.Sprite):
    '''Class for create obstacles'''
    def __init__(self, x, y):
        self.x = x
        self.y = y
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("world/obstacle").convert()
        self.rect = self.image.get_rect()
        self.rect.topleft = [self.x, self.y]
        
class ChickenNugget(pygame.sprite.Sprite):
	def __init__(self, x, y):
		self.x = x
		self.y = y
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("actions/nugget").convert_alpha()
		self.rect = self.image.get_rect()
		self.rect.topleft = [self.x, self.y]
		self.frame = 0
		self.contact = False

class Chicken(pygame.sprite.Sprite):
    '''class for player and collision'''

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.movy = 0
        self.movx = 0
        self.x = x
        self.y = y
        self.Score = 0
        self.contact = False
        self.jump = False
        self.image = pygame.image.load('actions/chicken_right').convert()
        self.rect = self.image.get_rect()
        self.run_left = ["actions/chicken_left","actions/chicken_left2","actions/chicken_left","actions/chicken_left2","actions/chicken_left","actions/chicken_left2","actions/chicken_left","actions/chicken_left2"]
        self.run_right = ["actions/chicken_right","actions/chicken_right2","actions/chicken_right","actions/chicken_right2","actions/chicken_right","actions/chicken_right2","actions/chicken_right2","actions/chicken_right2"]

        self.direction = "right"
        self.rect.topleft = [x, y]
        self.frame = 0

	def getscore(self):
		return self.Score
		
    def update(self, up, down, left, right, score1):

        chicken_list = pygame.sprite.spritecollide(self, all_sprite, False)
        chicken_list.remove(self)
        for chickenNugget in chicken_list:
			score1 += 1
			self.Score = score1
			chickenNugget.remove()
			chickenNugget.kill()
		
				       
        myfont = pygame.font.SysFont("None", 34)
        scoretext = myfont.render("Score {0}".format(score1), 1, (0,0,0))
        screen.blit(scoretext, (5, 10))
        
        if up:
            if self.contact:
                if self.direction == "right":
                    self.image = pygame.image.load("actions/chicken_right")
                self.jump = True
                self.movy -= 20
        if down:
            if self.contact and self.direction == "right":
                self.image = pygame.image.load('actions/chicken_right').convert_alpha()
            if self.contact and self.direction == "left":
                self.image = pygame.image.load('actions/chicken_left').convert_alpha()

        if not down and self.direction == "right":
                self.image = pygame.image.load('actions/chicken_right').convert_alpha()

        if not down and self.direction == "left":
            self.image = pygame.image.load('actions/chicken_left').convert_alpha()

        if left:
            self.direction = "left"
            self.movx = -HORIZ_MOV_INCR
            if self.contact:
                self.frame += 1
                self.image = pygame.image.load(self.run_left[self.frame]).convert_alpha()
                if self.frame == 6: self.frame = 0
            else:
                self.image = self.image = pygame.image.load("actions/chicken_left").convert_alpha()

        if right:
            self.direction = "right"
            self.movx = +HORIZ_MOV_INCR
            if self.contact:
                self.frame += 1
                self.image = pygame.image.load(self.run_right[self.frame]).convert_alpha()
                if self.frame == 6: self.frame = 0
            else:
                self.image = self.image = pygame.image.load("actions/chicken_right").convert_alpha()

        if not (left or right):
            self.movx = 0
        self.rect.right += self.movx

        self.collide(self.movx, 0, world)


        if not self.contact:
            self.movy += 0.3
            if self.movy > 10:
                self.movy = 10
            self.rect.top += self.movy

        if self.jump:

            self.movy += 2
            self.rect.top += self.movy
            if self.contact == True:
                self.jump = False

        self.contact = False
        self.collide(0, self.movy, world)



    def collide(self, movx, movy, world):
        self.contact = False
        for o in world:
            if self.rect.colliderect(o):
                if movx > 0:
                    self.rect.right = o.rect.left
                if movx < 0:
                    self.rect.left = o.rect.right
                if movy > 0:
                    self.rect.bottom = o.rect.top
                    self.movy = 0
                    self.contact = True
                if movy < 0:
                    self.rect.top = o.rect.bottom
                    self.movy = 0
                    


class Level(object):
    '''Read a map and create a level'''
    def __init__(self, open_level):
        self.level1 = []
        self.world = []
        self.all_sprite = pygame.sprite.Group()
        self.level = open(open_level, "r")

    def create_level(self, x, y):
        for l in self.level:
            self.level1.append(l)

        for row in self.level1:
            for col in row:
                if col == "X":
                    obstacle = Obstacle(x, y)
                    self.world.append(obstacle)
                    self.all_sprite.add(self.world)
                if col == "C":
                    self.chicken = Chicken(x,y)
                    self.all_sprite.add(self.chicken)
                if col == "N":
					self.chickenNugget = ChickenNugget(x, y)
					self.all_sprite.add(self.chickenNugget)
                x += 25
            y += 25
            x = 0

    def get_size(self):
        lines = self.level1
        line = max(lines, key=len)
        self.width = (len(line))*25
        self.height = (len(lines))*25
        return (self.width, self.height)


def tps(orologio,fps):
    temp = orologio.tick(fps)
    tps = temp / 3000.
    return tps



pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE, FULLSCREEN, 32)
screen_rect = screen.get_rect()
background = pygame.image.load("world/background2.jpg").convert_alpha()
background_rect = background.get_rect()
level = Level("level/level1")
level.create_level(0,0)
world = level.world
chicken = level.chicken
chickenNugget = level.chickenNugget
pygame.mouse.set_visible(0)

camera = Camera(screen, chicken.rect, level.get_size()[0], level.get_size()[1])
all_sprite = level.all_sprite

FPS = 30
clock = pygame.time.Clock()

up = down = left = right = False
x, y = 0, 0

chickenNugget_list = pygame.sprite.Group()
all_sprites_list = pygame.sprite.Group()
		
while True:

    for event in pygame.event.get():
        if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN and event.key == K_UP:
            up = True
        if event.type == KEYDOWN and event.key == K_DOWN:
            down = True
        if event.type == KEYDOWN and event.key == K_LEFT:
            left = True
        if event.type == KEYDOWN and event.key == K_RIGHT:
            right = True

        if event.type == KEYUP and event.key == K_UP:
            up = False
        if event.type == KEYUP and event.key == K_DOWN:
            down = False
        if event.type == KEYUP and event.key == K_LEFT:
            left = False
        if event.type == KEYUP and event.key == K_RIGHT:
            right = False

    asize = ((screen_rect.w // background_rect.w + 1) * background_rect.w, (screen_rect.h // background_rect.h + 1) * background_rect.h)
    bg = pygame.Surface(asize)

    for x in range(0, asize[0], background_rect.w):
        for y in range(0, asize[1], background_rect.h):
            screen.blit(background, (x, y))

    time_spent = tps(clock, FPS)
    camera.draw_sprites(screen, all_sprite)

    chicken.update(up, down, left, right, score)
    score = chicken.Score
    
    fontObject = pygame.font.SysFont("None", 60) 
    if score == 16:
		screen.blit(fontObject.render("You Win!".format(), 1 , (0,0,0)), (40, 60))

    camera.update()
    pygame.display.flip()
