import pygame, sys, math
from pygame.locals import *

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()


class KeyBoard(object):
    def __init__(self):
        self.Down, self.Up, self.Pressed = None, None, pygame.key.get_pressed()


keys = KeyBoard()


class Game(object):
    def __init__(self, w, h, title, time=0):
        self.width, self.height = w, h
        pygame.display.set_caption(title)
        self.screen = pygame.display.set_mode([w, h])
        self.background, self.backgroundXY, self.backgroundXYSet = None, [], False
        self.fps, self.time, self.clock = 20, time + 1, pygame.time.Clock()
        self.left, self.top, self.right, self.bottom = 0, 0, w, h
        self.over, self.score = False, 0
        #self.font = Font()

    def update(self, fps=1):
        self.fps = fps
        if self.time > 0:
            self.time -= 1 / fps
        pygame.display.flip()
        self.clock.tick(fps)

    def processInput(self):
        self.keysPressed = pygame.key.get_pressed()
        keys.Pressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.over = True
            if event.type == pygame.KEYDOWN:
                keys.Down = event.key
            else:
                keys.Down = None

            if event.type == pygame.KEYUP:
                keys.Up = event.key
            else:
                keys.Up = None


class Image(object):
    def __init__(self, path, game, use_alpha=True):
        self.game = game
        if not isinstance(path, str):
            self.image = path
        else:
            if use_alpha:
                self.image = pygame.image.load(path).convert_alpha()
            else:
                self.image = pygame.image.load(path).convert()
                trans_color = self.image.get_at((0, 0))
                self.image.set_colorkey(trans_color)

        self.width, self.original_width, self.oldwidth = self.image.get_width(
        ), self.image.get_width(), self.image.get_width()
        self.height, self.original_height, self.oldheight = self.image.get_height(
        ), self.image.get_height(), self.image.get_height()
        self.rect = None
        self.original, self.src = self.image, self.image
        self.angle, self.da = 0, 0
        self.x, self.y, self.dx, self.dy, self.dxsign, self.dysign = self.game.width / 2, self.game.height / 2, 0, 0, 1, 1
        self.left, self.top, self.right, self.bottom = 0, 0, 0, 0
        #self.bounce = False
        self.flipV, self.flipH, self.offsetX, self.offsetY = False, False, 0, 0
        self.rotate, self.rotate_angle, self.rda = "still", 0, 0
        #self.speed = 0
        self.visible = True

    def resizeTo(self, w, h):
        self.original = pygame.transform.scale(self.src, (int(w), int(h)))
        self.image = self.original
        self.width, self.height = self.image.get_width(
        ), self.image.get_height()
        self.oldwidth, self.oldheight = self.width, self.height

    def setImage(self, image):
        self.image = image
        self.original = image

    def draw(self):
        if self.width != self.oldwidth or self.height != self.oldheight:
            self.resizeTo(self.width, self.height)
        if self.flipV or self.flipH:
            self.image = pygame.transform.flip(self.image, self.flipV, self.flipH)
        if self.rotate == "left" or self.rotate == "right" or self.rotate == "to":
            self.image = self.original
            self.image = pygame.transform.rotate(
                self.image, self.rotate_angle * 180 / math.pi)
            self.width, self.height = self.image.get_width(
            ), self.image.get_height()
            self.oldwidth, self.oldheight = self.width, self.height
        if self.visible:
            self.game.screen.blit(
                self.image,
                [self.x - self.width / 2, self.y - self.height / 2])
        self.rect = pygame.Rect(self.left, self.top, self.width, self.height)
        self.left, self.top, self.right, self.bottom = self.x - self.width / 2, self.y - self.height / 2, self.x + self.width / 2, self.y + self.height / 2

##########################################################################



###DO NOT COPY BEYOND HERE!!!!!!!








#######################################################################################


class Animation(Image):
    def __init__(self,
                 path,
                 sequence,
                 game,
                 width=0,
                 height=0,
                 frate=1,
                 use_alpha=True):
        self.f, self.frate, self.ftick, self.loop, self.once = 0, frate, 0, True, True
        self.game = game
        self.playAnim = True
        self.images = []
        self.source = []
        if width == 0 and height == 0:
            Image.__init__(self, path + "1.gif", game)
            for i in range(sequence):
                self.images.append(
                    pygame.image.load(path + str(i + 1) +
                                      ".gif").convert_alpha())
                self.source.append(self.images[i])
        else:
            if use_alpha:
                self.sheet = pygame.image.load(path).convert_alpha()
            else:
                self.sheet = pygame.image.load(path).convert()
                trans_color = self.sheet.get_at((0, 0))
                self.sheet.set_colorkey(trans_color)

            tmp = self.sheet.subsurface((0, 0, width, height))
            Image.__init__(self, tmp, game)
            self.frame_width, self.frame_height = width, height
            self.frame_rect = 0, 0, width, height
            try:
                self.columns = self.sheet.get_width() / width
            except:
                print("Wrong size sheet")
            for i in range(sequence):
                frame_x = (i % self.columns) * self.frame_width
                frame_y = (i // self.columns) * self.frame_height
                rect = (frame_x, frame_y, self.frame_width, self.frame_height)
                frame_image = self.sheet.subsurface(rect)
                self.images.append(frame_image)
                self.source.append(frame_image)

    def draw(self, loop=True):
        if self.visible:
            Image.setImage(self, self.images[self.f % len(self.images)])
            Image.draw(self)
            self.ftick += 1
            if self.ftick % self.frate == 0 and self.playAnim:
                self.f += 1
                self.ftick = 0
            if not loop and self.f == len(self.images) - 1:
                self.visible = False
                self.f = 0
            if self.f > len(self.images) - 1:
                self.f = 0
                self.ftick = 0

    def resizeTo(self, w, h):
        self.width, self.height = w, h
        for i in range(len(self.images)):
            self.images[i] = pygame.transform.scale(
                self.source[i], (int(self.width), int(self.height)))


##########################################################################

#main program
game = Game(1200, 800,'Game 2')

user = Animation("cutie.png", 8, game, 1098/2, 1932/4, 4)








while game.over == False:
    game.processInput()
    game.screen.fill((247,166,253))
    user.draw()






    if keys.Pressed[K_ESCAPE]:
        game.over = True

    game.update(60)

pygame.quit()
