import csv
import math
import random
import pygame
import os  
from Key import Key
SCREEN_WIDTH = 448
SCREEN_HEIGHT = 535
pygame.init()
pygame.font.init()
pygame.mixer.init()
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption('GAME PACMAN')
FPS = 60

musicPlaying = 0
MusicPath = "res/sound/"
clock = pygame.time.Clock()
background_img = pygame.image.load("res/img/background.png")
start_img = pygame.transform.scale(pygame.image.load("res/img/nen.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT))
game_over_bg = pygame.transform.scale(pygame.image.load("res/img/end.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
high_score_bg = pygame.transform.scale(pygame.image.load("res/img/anh.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))


k_up = Key()
k_down = Key()
k_left = Key()
k_right = Key()

game_first_input = False
score = 0
entities = []
wall = []
ghosts = []
level = []
lives = 3
totalFood = 0
dic = [0, math.pi, math.pi / 2, math.pi * 3 / 2]

running = True
gameOver = False
win = False
paused = False
show_high_score = False  
show_instructions = False  
blinkGhost = None
clydeGhost = None
inkyGhost = None
pinkyGhost = None
pacman = None
timerStart = 0

def save_high_score(new_score):
    high_score = get_high_score()
    if new_score > high_score:
        with open("highscore.txt", "w") as f:
            f.write(str(new_score))

def get_high_score():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            try:
                return int(f.read())
            except ValueError:
                return 0
    else:
        return 0

def draw_start_screen(start_button, instructions_button, exit_button, font):
    screen.blit(start_img, (0, 0))
    pygame.draw.rect(screen, (0, 255, 0), start_button, border_radius=5)
    pygame.draw.rect(screen, (255, 165, 0), instructions_button, border_radius=5)  
    pygame.draw.rect(screen, (255, 0, 0), exit_button, border_radius=5)

    start_text = font.render('Start', True, (0, 0, 0))
    instructions_text = font.render('Guide', True, (0, 0, 0))
    exit_text = font.render('Exit', True, (0, 0, 0))

    screen.blit(start_text, (start_button.x + 8, start_button.y + 13))
    screen.blit(instructions_text, (instructions_button.x + 12, instructions_button.y + 12))
    screen.blit(exit_text, (exit_button.x + 17, exit_button.y + 14))
    pygame.display.flip()
    
def start_screen():
    global running, show_instructions
    font = pygame.font.Font("res/font/font.ttf", 16)
    start_button = pygame.Rect(174, 150, 100, 50)
    instructions_button = pygame.Rect(174, 230, 100, 50)
    exit_button = pygame.Rect(174, 310, 100, 50)
    while True:
        clock.tick(FPS)
        draw_start_screen(start_button, instructions_button, exit_button, font)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if start_button.collidepoint(mouse_pos):
                    return True
                if instructions_button.collidepoint(mouse_pos):
                    show_instructions = True
                    instructions_screen()
                if exit_button.collidepoint(mouse_pos):
                    running = False
                    return False

def instructions_screen():
    global running, show_instructions
    font = pygame.font.Font("res/font/VAGRB.TTF", 17)
    back_button = pygame.Rect(174, 460, 80, 50)
    instructions = [
       "PAC-MAN GAME INSTRUCTIONS:", "", "Your to control Pac-Man to eat all the Pac-Gums", "in the maze while avoiding the ghosts.", "", "Controls:", "- Use the arrow keys to move Pac-Man.", "", "Items:", "- Pac-Gum: Eat to gain points.", "- Super Pac-Gum: Allows Pac-Man to eat ghosts for a short time.", "", "                 Enjoy playing the game!"
    ]
    while show_instructions:
        clock.tick(FPS)
        screen.fill((0, 0, 0))
        y_offset = 50
        for line in instructions:
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (20, y_offset))
            y_offset += 30
        pygame.draw.rect(screen, (192, 192, 192), back_button, border_radius=5)
        back_text = font.render('Back', True, (0, 0, 0))
        screen.blit(back_text, (back_button.x + 22, back_button.y + 10))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                show_instructions = False
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if back_button.collidepoint(mouse_pos):
                    show_instructions = False

def draw_game_over_screen(high_score_button):
    global score , game_over_bg
    font = pygame.font.Font("res/font/font.ttf", 20)
    game_over_rect = pygame.Rect(130, 10, 210, 60)
    score_rect = pygame.Rect(110, 190, 245, 50)  
    high_score_rect = high_score_button  # Nút xem điểm cao nhất
    replay_rect = pygame.Rect(7, 330, 435, 50)  
    screen.blit(game_over_bg, (0, 0))
    
    pygame.draw.rect(screen, (255, 255, 255), game_over_rect, border_radius=5)
    pygame.draw.rect(screen, (0, 0, 255), score_rect, border_radius=5)
    pygame.draw.rect(screen, (255, 255, 0), high_score_rect, border_radius=5)   
    pygame.draw.rect(screen, (0, 255, 0), replay_rect, border_radius=5)

    game_over_text = font.render('Game Over', True, (0, 0, 0))
    score_text = font.render('Score: ' + str(score), True, (0, 0, 0))
    high_score_text = font.render('High Score', True, (0, 0, 0))
    replay_text = font.render('Press Space To Replay', True, (0, 0, 0))

    screen.blit(game_over_text, (game_over_rect.x + 17, game_over_rect.y + 15))
    screen.blit(score_text, (score_rect.x + 20, score_rect.y + 10))
    screen.blit(high_score_text, (high_score_rect.x + 19, high_score_rect.y + 10))
    screen.blit(replay_text, (replay_rect.x + 15, replay_rect.y + 10))

def draw_high_score_screen():
    global high_score_bg 
    font = pygame.font.Font("res/font/font.ttf", 20)
    high_score_rect = pygame.Rect(100, 150, 250, 50)
    back_rect = pygame.Rect(150, 250, 150, 50)
    screen.blit(high_score_bg, (0, 0))
    
    pygame.draw.rect(screen, (0, 0, 255), high_score_rect, border_radius=5)
    pygame.draw.rect(screen, (0, 255, 0), back_rect, border_radius=5)

    high_score = get_high_score()
    high_score_text = font.render('Score: ' + str(high_score), True, (255, 255, 255))
    back_text = font.render('Back', True, (255, 255, 255))

    screen.blit(high_score_text, (high_score_rect.x + 20, high_score_rect.y + 10))
    screen.blit(back_text, (back_rect.x + 35, back_rect.y + 10))
    pygame.display.flip()
    return back_rect

def draw_pause_screen():
    font = pygame.font.Font("res/font/font.ttf", 20)
    pause_rect = pygame.Rect(108, 10, 245, 55)
    continue_rect = pygame.Rect(130, 220, 200, 50)
    exit_rect = pygame.Rect(130, 290, 200, 50)

    pygame.draw.rect(screen, (255, 255, 255), pause_rect, border_radius=5)
    pygame.draw.rect(screen, (0, 255, 0), continue_rect, border_radius=5)
    pygame.draw.rect(screen, (255, 0, 0), exit_rect, border_radius=5)

    pause_text = font.render('Pause Game', True, (0, 0, 0))
    continue_text = font.render('Continue', True, (0, 0, 0))
    exit_text = font.render('Exit', True, (0, 0, 0))

    screen.blit(pause_text, (pause_rect.x + 27, pause_rect.y + 12))
    screen.blit(continue_text, (continue_rect.x + 22, continue_rect.y + 10))
    screen.blit(exit_text, (exit_rect.x + 59, exit_rect.y + 10))

    pygame.display.flip()
    return continue_rect, exit_rect

def pause_screen():
    global running, paused
    while paused:
        clock.tick(FPS)
        continue_button, exit_button = draw_pause_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                paused = False
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if continue_button.collidepoint(mouse_pos):
                    paused = False
                if exit_button.collidepoint(mouse_pos):
                    running = False
                    paused = False
                    return    
def draw_victory_screen():
    global score
    font = pygame.font.Font("res/font/font.ttf", 20)
    victory_rect = pygame.Rect(130, 10, 210, 60)
    score_rect = pygame.Rect(110, 190, 245, 50)
    replay_rect = pygame.Rect(7, 245, 435, 50)

    pygame.draw.rect(screen, (255, 255, 255), victory_rect, border_radius=5)
    pygame.draw.rect(screen, (0, 0, 255), score_rect, border_radius=5)
    pygame.draw.rect(screen, (0, 255, 0), replay_rect, border_radius=5)

    victory_text = font.render('VICTORY', True, (0, 0, 0))
    score_text = font.render('Score: ' + str(score), True, (0, 0, 0))
    replay_text = font.render('Press Space To Replay', True, (0, 0, 0))

    screen.blit(victory_text, (victory_rect.x + 40, victory_rect.y + 15))
    screen.blit(score_text, (score_rect.x + 30, score_rect.y + 10))
    screen.blit(replay_text, (replay_rect.x + 10, replay_rect.y + 10))

    pygame.display.flip()
class Entity:

    def __init__(self, xPos, yPos, size):
        self.xPos = xPos
        self.yPos = yPos
        self.size = size
        self.dead = False

    def draw(self):
        pass

    def update(self):
        pass

    def getRect(self):
        pass

    def getSize(self):
        return self.size

    def isDead(self):
        return self.dead

    def getXPos(self):
        return self.xPos

    def getYPos(self):
        return self.yPos

    def setDead(self):
        self.xPos = -32
        self.yPos = -32
        self.dead = True

class MovingEntity(Entity):

    def __init__(self, xPos, yPos, size, speed, spriteName, imgSpeed, imgPerCycle):
        super().__init__(xPos, yPos, size)

        self.speed = speed
        self.sprite = pygame.image.load("res/img/" + spriteName)
        self.imgSpeed = imgSpeed
        self.imgPerCycle = imgPerCycle
        self.direction = 0
        self.xSpeed = 0
        self.ySpeed = 0
        self.subImg = 0
        self.x_start = xPos
        self.y_start = yPos

    def draw(self):
        screen.blit(
            self.sprite.subsurface(self.direction * self.imgPerCycle * self.size + self.size * int(self.subImg), 0,
                                   self.size, self.size), (self.xPos, self.yPos))

    def update(self):
        self.updatePos()

    def onTheGrid(self):
        return self.xPos % 8 == 0 and self.yPos % 8 == 0

    def onTheGamePlay(self):
        return 0 < self.xPos < SCREEN_WIDTH and 0 < self.yPos < SCREEN_HEIGHT

    def updatePos(self):

        if not (self.xSpeed == 0 and self.ySpeed == 0):
            self.xPos += self.xSpeed
            self.yPos += self.ySpeed

            if self.xSpeed > 0:
                self.direction = 0
            elif self.xSpeed < 0:
                self.direction = 1
            elif self.ySpeed < 0:
                self.direction = 2
            elif self.ySpeed > 0:
                self.direction = 3
            self.subImg += self.imgSpeed
            if self.subImg >= self.imgPerCycle:
                self.subImg = 0
        if self.xPos > SCREEN_WIDTH:
            self.xPos = -self.size
        if self.xPos < -self.size:
            self.xPos = SCREEN_WIDTH
        if self.yPos > SCREEN_HEIGHT:
            self.yPos = -self.size
        if self.yPos < -self.size:
            self.yPos = SCREEN_HEIGHT

    def getRect(self):
        return pygame.Rect((self.xPos, self.yPos), (self.size, self.size))

    def getDir(self):
        return self.direction

    def reset(self):
        self.xPos = self.x_start
        self.yPos = self.y_start
        self.direction = 0
        self.xSpeed = 0
        self.ySpeed = 0
        self.subImg = 0

class StaticEntity(Entity):
    def __init__(self, xPos, yPos, size):
        super().__init__(xPos, yPos, size)
        self.rect = pygame.Rect((xPos, yPos), (size, size))

    def getRect(self):
        return self.rect


class PacGum(StaticEntity):
    def __init__(self, xPos, yPos):
        super().__init__(xPos, yPos, 4)

    def draw(self):
        pygame.draw.rect(screen, pygame.Color(255, 183, 174), (self.xPos + 8, self.yPos + 8, self.size, self.size))


class Pacman(MovingEntity):

    def __init__(self, xPos, yPos):
        super().__init__(xPos + 8, yPos, 32, 2, "pacman.png", 0.2, 4)
        self.lives = 3

    def input(self):
        global game_first_input

        if not game_first_input:
            game_first_input = True

        if not self.onTheGrid():
            return
        if not self.onTheGamePlay():
            return

        new_x_speed = 0
        new_y_speed = 0

        if k_left.getPressed() and self.xSpeed >= 0 and not checkWallCollision(self, -self.speed, 0
                                                                               ):
            new_x_speed = -self.speed
        if k_right.getPressed() and self.xSpeed <= 0 and not checkWallCollision(self, self.speed, 0
                                                                                ):
            new_x_speed = self.speed
        if k_up.getPressed() and self.ySpeed >= 0 and not checkWallCollision(self, 0, -self.speed):
            new_y_speed = -self.speed
        if k_down.getPressed() and self.ySpeed <= 0 and not checkWallCollision(self, 0, self.speed
                                                                               ):
            new_y_speed = self.speed

        if new_x_speed == 0 and new_y_speed == 0:
            return

        if not abs(new_x_speed) == abs(new_y_speed):
            self.xSpeed = new_x_speed
            self.ySpeed = new_y_speed
        else:
            if not self.xSpeed == 0:
                self.xSpeed = 0
                self.ySpeed = new_y_speed
            else:
                self.xSpeed = new_x_speed
                self.ySpeed = 0

    def update(self):
        if not checkWallCollision(self, self.xSpeed, self.ySpeed):
            self.updatePos()

    def reset(self):
        super().reset()


class SuperPacGum(StaticEntity):
    def __init__(self, xPos, yPos):
        super().__init__(xPos, yPos, 16)
        self.flicker = 0

    def update(self):
        self.flicker += 1
        if self.flicker > 60:
            self.flicker = 0

    def draw(self):
        if self.flicker < 30:
            pygame.draw.ellipse(screen, pygame.Color(255, 183, 174), (self.xPos, self.yPos, self.size, self.size))


class Wall(StaticEntity):
    def __init__(self, xPos, yPos):
        super().__init__(xPos, yPos, 8)


class GhostDoor(Wall):
    def __init__(self, xPos, yPos):
        super().__init__(xPos, yPos)


class Ghost(MovingEntity):
    def __init__(self, xPos, yPos, sprite, time):
        super().__init__(xPos, yPos, 32, 1, sprite, 0.3, 2)

        self.ghost_eaten_sprite = pygame.image.load('res/img/ghost_eaten.png')
        self.ghost_frightened_1 = pygame.image.load('res/img/ghost_frightened.png')
        self.ghost_frightened_2 = pygame.image.load('res/img/ghost_frightened_2.png')

        # MODE
        self.chaseMode = ChaseMode(self)
        self.scatterMode = ScatterMode(self)
        self.frightenedMode = FrightenedMode(self)
        self.eatenMode = EatenMode(self)
        self.houseMode = HouseMode(self)
        self.state = self.houseMode

        self.modeTimer = 0
        self.frightenedTimer = 0
        self.isChasing = False
        self.time = time
        self.count = 0

    def getChasePos(self):
        pass

    def getScatterPos(self):
        pass

    def draw(self):
        if self.state == self.frightenedMode:
            if self.frightenedTimer <= (60 * 5) or (self.frightenedTimer % 20 > 10):
                screen.blit(self.ghost_frightened_1.subsurface(self.size * int(self.subImg), 0, self.size, self.size),
                            (self.xPos, self.yPos))
            else:
                screen.blit(self.ghost_frightened_2.subsurface(self.size * int(self.subImg), 0, self.size, self.size),
                            (self.xPos, self.yPos))

        elif self.state == self.eatenMode:
            screen.blit(self.ghost_eaten_sprite.subsurface(self.size * self.direction, 0, self.size, self.size),
                        (self.xPos, self.yPos))
        else:
            screen.blit(
                self.sprite.subsurface(self.direction * self.imgPerCycle * self.size + self.size * int(self.subImg), 0,
                                       self.size, self.size), (self.xPos, self.yPos))

    def switchFrightenedMode(self):
        self.frightenedTimer = 0
        self.state = self.frightenedMode

    def switchScatterMode(self):
        self.state = self.scatterMode

    def switchHouseMode(self):
        self.state = self.houseMode

    def switchEatenMode(self):
        self.state = self.eatenMode

    def switchChaseModeOrScatterMode(self):
        if self.isChasing:
            self.switchChaseMode()
        else:
            self.switchScatterMode()

    def switchChaseMode(self):
        self.state = self.chaseMode

    def getState(self):
        return self.getState()

    def update(self):

        if self.count < (self.time * 60):
            self.count += 1
        else:
            if not game_first_input:
                return
            if self.state == self.frightenedMode:
                self.frightenedTimer += 1
                if self.frightenedTimer >= (60 * 7):
                    self.state.timeFrightenModeOver()
                    self.frightenedTimer = 0

            if self.state == self.chaseMode or self.state == self.scatterMode:
                self.modeTimer += 1
                if self.isChasing and self.modeTimer >= (60 * 20) or (
                        not self.isChasing and self.modeTimer >= (60 * 10)):
                    self.state.timeModeOver()
                    self.isChasing = not self.isChasing
                    self.modeTimer = 0

            if self.xPos == 208 and self.yPos == 168:
                self.state.outsideHouse()
            if self.xPos == 208 and self.yPos == 200:
                self.state.insideHouse()
            self.state.computeNextDir()
            self.updatePos()

    def reset(self):
        super().reset()
        self.state = self.houseMode


class BlinkyGhost(Ghost):

    def __init__(self, xPos, yPos):
        super().__init__(xPos, yPos, "blinky.png", 0)

    def getChasePos(self):
        return pacman.getXPos(), pacman.getYPos()

    def getScatterPos(self):
        return SCREEN_WIDTH, 0


class ClydeGhost(Ghost):

    def __init__(self, xPos, yPos):
        super().__init__(xPos, yPos, "clyde.png", 4)

    def getChasePos(self):
        if getDistance(self.xPos, self.yPos, pacman.xPos, pacman.yPos) >= 256:
            return pacman.xPos, pacman.yPos
        return self.getScatterPos()

    def getScatterPos(self):
        return 0, 496


class InkyGhost(Ghost):
    def __init__(self, xPos, yPos, otherGhost: BlinkyGhost = None):
        super().__init__(xPos, yPos, "inky.png", 3)
        self.otherGhost = otherGhost

    def getChasePos(self):
        distance2Cell = getPointDistanceDirection(pacman.xPos, pacman.yPos, 32, dic[pacman.getDir()])
        distanceToBlinky = getDistance(distance2Cell[0], distance2Cell[1], self.otherGhost.xPos, self.otherGhost.yPos)
        directionToBlinky = getDirection(self.otherGhost.xPos, self.otherGhost.yPos, distance2Cell[0], distance2Cell[1])
        return getPointDistanceDirection(distance2Cell[0], distance2Cell[1], distanceToBlinky, directionToBlinky)

    def getScatterPos(self):
        return SCREEN_WIDTH, 496


class PinkyGhost(Ghost):

    def __init__(self, xPos, yPos):
        super().__init__(xPos, yPos, "pinky.png", 2)

    def getChasePos(self):
        return getPointDistanceDirection(pacman.xPos, pacman.yPos, 64, dic[pacman.getDir()])

    def getScatterPos(self):
        return 0, 0


class GhostState:

    def __init__(self, ghost: Ghost):
        self.ghost = ghost

    def superPacGumEaten(self):
        pass

    def timeModeOver(self):
        pass

    def timeFrightenModeOver(self):
        pass

    def eaten(self):
        pass

    def outsideHouse(self):
        pass

    def insideHouse(self):
        pass

    def getTargetPos(self):
        return [0, 0]

    def computeNextDir(self):
        new_x_speed = 0
        new_y_speed = 0

        if not self.ghost.onTheGrid():
            return
        if not self.ghost.onTheGamePlay():
            return

        min_dist = float('inf')
        if self.ghost.xSpeed <= 0 and not checkWallCollision(self.ghost, -self.ghost.speed, 0):
            distance = getDistance(self.ghost.xPos - self.ghost.speed, self.ghost.yPos, self.getTargetPos()[0],
                                   self.getTargetPos()[1])
            if distance < min_dist:
                new_x_speed = -self.ghost.speed
                new_y_speed = 0
                min_dist = distance

        if self.ghost.xSpeed >= 0 and not checkWallCollision(self.ghost, self.ghost.speed, 0):
            distance = getDistance(self.ghost.xPos + self.ghost.speed, self.ghost.yPos, self.getTargetPos()[0],
                                   self.getTargetPos()[1])
            if distance < min_dist:
                new_x_speed = self.ghost.speed
                new_y_speed = 0
                min_dist = distance

        if self.ghost.ySpeed <= 0 and not checkWallCollision(self.ghost, 0, -self.ghost.speed):
            distance = getDistance(self.ghost.xPos, self.ghost.yPos - self.ghost.speed, self.getTargetPos()[0],
                                   self.getTargetPos()[1])
            if distance < min_dist:
                new_x_speed = 0
                new_y_speed = -self.ghost.speed
                min_dist = distance
        if self.ghost.ySpeed >= 0 and not checkWallCollision(self.ghost, 0, self.ghost.speed):
            distance = getDistance(self.ghost.xPos, self.ghost.yPos + self.ghost.speed, self.getTargetPos()[0],
                                   self.getTargetPos()[1])
            if distance < min_dist:
                new_x_speed = 0
                new_y_speed = self.ghost.speed
                min_dist = distance
        if new_x_speed == 0 and new_y_speed == 0:
            return

        if not abs(new_x_speed) == abs(new_y_speed):
            self.ghost.xSpeed = new_x_speed
            self.ghost.ySpeed = new_y_speed
        else:
            if not self.ghost.xSpeed == 0:
                self.ghost.xSpeed = 0
                self.ghost.ySpeed = new_y_speed
            else:
                self.ghost.xSpeed = new_x_speed
                self.ghost.ySpeed = 0


class ChaseMode(GhostState):
    def __init__(self, ghost: Ghost):
        super().__init__(ghost)

    def superPacGumEaten(self):
        self.ghost.switchFrightenedMode()

    def timeModeOver(self):
        self.ghost.switchScatterMode()

    def getTargetPos(self):
        return self.ghost.getChasePos()


class EatenMode(GhostState):
    def __init__(self, ghost: Ghost):
        super().__init__(ghost)

    def insideHouse(self):
        self.ghost.switchHouseMode()

    def getTargetPos(self):
        return 208, 200

    def computeNextDir(self):
        new_x_speed = 0
        new_y_speed = 0

        if not self.ghost.onTheGrid():
            return
        if not self.ghost.onTheGamePlay():
            return

        minDist = float('inf')
        if self.ghost.xSpeed <= 0 and not checkWallCollisionIgnoreGhostDoor(self.ghost, -self.ghost.speed, 0, True):
            distance = getDistance(self.ghost.xPos - self.ghost.speed, self.ghost.yPos, self.getTargetPos()[0],
                                   self.getTargetPos()[1])
            if distance < minDist:
                new_x_speed = -self.ghost.speed
                new_y_speed = 0
                minDist = distance

        if self.ghost.xSpeed >= 0 and not checkWallCollisionIgnoreGhostDoor(self.ghost, self.ghost.speed, 0, True):
            distance = getDistance(self.ghost.xPos + self.ghost.speed, self.ghost.yPos, self.getTargetPos()[0],
                                   self.getTargetPos()[1])
            if distance < minDist:
                new_x_speed = self.ghost.speed
                new_y_speed = 0
                minDist = distance

        if self.ghost.ySpeed <= 0 and not checkWallCollisionIgnoreGhostDoor(self.ghost, 0, -self.ghost.speed, True):
            distance = getDistance(self.ghost.xPos, self.ghost.yPos - self.ghost.speed, self.getTargetPos()[0],
                                   self.getTargetPos()[1])
            if distance < minDist:
                new_x_speed = 0
                new_y_speed = -self.ghost.speed
                minDist = distance
        if self.ghost.ySpeed >= 0 and not checkWallCollisionIgnoreGhostDoor(self.ghost, 0, self.ghost.speed, True):
            distance = getDistance(self.ghost.xPos, self.ghost.yPos + self.ghost.speed, self.getTargetPos()[0],
                                   self.getTargetPos()[1])
            if distance < minDist:
                new_x_speed = 0
                new_y_speed = self.ghost.speed
                minDist = distance
        if new_x_speed == 0 and new_y_speed == 0:
            return
        if not abs(new_x_speed) == abs(new_y_speed):
            self.ghost.xSpeed = new_x_speed
            self.ghost.ySpeed = new_y_speed
        else:
            if not self.ghost.xSpeed == 0:
                self.ghost.xSpeed = 0
                self.ghost.ySpeed = new_y_speed
            else:
                self.ghost.xSpeed = new_x_speed
                self.ghost.ySpeed = 0


class FrightenedMode(GhostState):
    def __init__(self, ghost: Ghost):
        super().__init__(ghost)

    def eaten(self):
        self.ghost.switchEatenMode()

    def timeFrightenModeOver(self):
        self.ghost.switchChaseModeOrScatterMode()

    def getTargetPos(self):
        r = random.choice([0, 1])
        x = self.ghost.getXPos()
        y = self.ghost.getYPos()
        if r == 0:
            x += random.choice([-1, 1])
        else:
            y += random.choice([-1, 1])
        return x, y


class HouseMode(GhostState):
    def __init__(self, ghost: Ghost):
        super().__init__(ghost)

    def outsideHouse(self):
        self.ghost.switchChaseModeOrScatterMode()

    def getTargetPos(self):
        return 208, 168

    def computeNextDir(self):
        new_x_speed = 0
        new_y_speed = 0

        if not self.ghost.onTheGrid():
            return
        if not self.ghost.onTheGamePlay():
            return

        minDist = float('inf')
        if self.ghost.xSpeed <= 0 and not checkWallCollisionIgnoreGhostDoor(self.ghost, -self.ghost.speed, 0, True):
            distance = getDistance(self.ghost.xPos - self.ghost.speed, self.ghost.yPos, self.getTargetPos()[0],
                                   self.getTargetPos()[1])
            if distance < minDist:
                new_x_speed = -self.ghost.speed
                new_y_speed = 0
                minDist = distance

        if self.ghost.xSpeed >= 0 and not checkWallCollisionIgnoreGhostDoor(self.ghost, self.ghost.speed, 0, True):
            distance = getDistance(self.ghost.xPos + self.ghost.speed, self.ghost.yPos, self.getTargetPos()[0],
                                   self.getTargetPos()[1])
            if distance < minDist:
                new_x_speed = self.ghost.speed
                new_y_speed = 0
                minDist = distance

        if self.ghost.ySpeed <= 0 and not checkWallCollisionIgnoreGhostDoor(self.ghost, 0, -self.ghost.speed, True):
            distance = getDistance(self.ghost.xPos, self.ghost.yPos - self.ghost.speed, self.getTargetPos()[0],
                                   self.getTargetPos()[1])
            if distance < minDist:
                new_x_speed = 0
                new_y_speed = -self.ghost.speed
                minDist = distance
        if self.ghost.ySpeed >= 0 and not checkWallCollisionIgnoreGhostDoor(self.ghost, 0, self.ghost.speed, True):
            distance = getDistance(self.ghost.xPos, self.ghost.yPos + self.ghost.speed, self.getTargetPos()[0],
                                   self.getTargetPos()[1])
            if distance < minDist:
                new_x_speed = 0
                new_y_speed = self.ghost.speed
                minDist = distance
        if new_x_speed == 0 and new_y_speed == 0:
            return
        if not abs(new_x_speed) == abs(new_y_speed):
            self.ghost.xSpeed = new_x_speed
            self.ghost.ySpeed = new_y_speed
        else:
            if not self.ghost.xSpeed == 0:
                self.ghost.xSpeed = 0
                self.ghost.ySpeed = new_y_speed
            else:
                self.ghost.xSpeed = new_x_speed
                self.ghost.ySpeed = 0


class ScatterMode(GhostState):
    def __init__(self, ghost: Ghost):
        super().__init__(ghost)

    def superPacGumEaten(self):
        self.ghost.switchFrightenedMode()

    def timeModeOver(self):
        self.ghost.switchChaseMode()

    def getTargetPos(self):
        return self.ghost.getScatterPos()


def checkFood():
    global pacman, entities, score, ghosts, totalFood, win 
    # Get center square
    r = pygame.Rect((pacman.xPos + pacman.size / 2 - 8, pacman.yPos + pacman.size / 2 - 8), (16, 16))
    for i in entities:
        if r.collidepoint((i.getXPos() + i.getSize() / 2, i.getYPos() + i.getSize() / 2)):
            if isinstance(i, PacGum):
                i.setDead()
                score += 10
                playMusic("munch_1.wav")
                totalFood -= 1

            if isinstance(i, SuperPacGum):
                i.setDead()
                score += 100
                totalFood -= 1
                forcePlayMusic("power_pellet.wav")
                for j in ghosts:
                    j.state.superPacGumEaten()
    if totalFood == 0:
        win = True


def checkGhostCollisionFrighten():
    global score, gameOver, level, k_up, k_down, k_left, k_right, entities, ghosts, wall, blinkGhost, clydeGhost, inkyGhost, pacman, timerStart, pinkyGhost

    gh = checkRectCollision()
    if gh is not None:
        if isinstance(gh.state, FrightenedMode):
            score += 300
            gh.state.eaten()
        elif not isinstance(gh.state, EatenMode):
            if pacman.lives > 1:
                pacman.lives -= 1
                pacman.reset()
                for g in ghosts:
                    g.reset()
            else:

                gameOver = True


def checkRectCollision():
    global ghosts, pacman
    for gh in ghosts:
        if not gh.isDead() and pygame.Rect.colliderect(pacman.getRect(), gh.getRect()):
            return gh
    return None


def checkWallCollision(obj: Entity, dx, dy):
    global wall
    r = pygame.Rect((obj.xPos + dx, obj.yPos + dy), (obj.size, obj.size))
    for i in wall:
        if pygame.Rect.colliderect(r, i.getRect()):
            return True
    return False


def checkWallCollisionIgnoreGhostDoor(obj: Entity, dx, dy, ignoreGhostDoor):
    global wall
    r = pygame.Rect((obj.xPos + dx, obj.yPos + dy), (obj.size, obj.size))
    for i in wall:
        if (not (ignoreGhostDoor and isinstance(i, GhostDoor))) and r.colliderect(i):
            return True
    return False


def getDistance(xA, yA, xB, yB):
    return math.sqrt(pow(xB - xA, 2) + pow(yB - yA, 2))


def getDirection(xA, yA, xB, yB):
    return math.atan2((yB - yA), (xB - xA))


def getPointDistanceDirection(x, y, distance, direction):
    return (x + math.cos(direction) * distance), (y + math.sin(direction) * distance)


def drawString(name, xPos, yPos):
    font = pygame.font.Font("res/font/font.ttf", 10)
    text = font.render(name, False, (255, 255, 255))
    screen.blit(text, (xPos, yPos))


def drawLives():
    for i in range(pacman.lives):
        screen.blit(pacman.sprite.subsurface(32, 0, pacman.size, pacman.size),
                    (270 + (i * 30), 500))


def draw():
    for i in entities:
        if not i.isDead():
            i.draw()
    drawString('SCORE:' + str(score), 10, 510)
    drawLives()


def update():
    for i in entities:
        if not i.isDead():
            i.update()


def init():
    global level, pacman, blinkGhost, inkyGhost, pinkyGhost, clydeGhost, ghosts, wall, totalFood
    file = open("res/level/level.csv", "r")
    level = list(csv.reader(file, delimiter=";"))
    file.close()

    size = 8

    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == ".":
                entities.append(PacGum(j * size, i * size))
                totalFood += 1
            elif level[i][j] == "o":
                entities.append(SuperPacGum(j * size, i * size))
                totalFood += 1
            elif level[i][j] == "x":
                entities.append(Wall(j * size, i * size))
            elif level[i][j] == "-":
                entities.append(GhostDoor(j * size, i * size))
            elif level[i][j] == "P":
                pacman = Pacman(j * size, i * size)
            elif level[i][j] == "b":
                blinkGhost = BlinkyGhost(j * size, i * size)
            elif level[i][j] == "i":
                inkyGhost = InkyGhost(j * size, i * size, blinkGhost)
            elif level[i][j] == "p":
                pinkyGhost = PinkyGhost(j * size, i * size)
            elif level[i][j] == "c":
                clydeGhost = ClydeGhost(j * size, i * size)

    entities.append(pacman)
    entities.append(blinkGhost)
    entities.append(inkyGhost)
    entities.append(pinkyGhost)
    entities.append(clydeGhost)

    for i in entities:
        if isinstance(i, Wall):
            wall.append(i)
        if isinstance(i, Ghost):
            ghosts.append(i)


def playMusic(music):
    # return False # Uncomment to disable music
    global musicPlaying
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.unload()
        pygame.mixer.music.load(MusicPath + music)
        pygame.mixer.music.queue(MusicPath + music)
        pygame.mixer.music.play(loops=1)
        if music == "begin.wav":
            musicPlaying = 0
        elif music == "siren_1.wav":
            musicPlaying = 2
        else:
            musicPlaying = 1
        pygame.mixer.stop()


def forcePlayMusic(music):
    # return False # Uncomment to disable music
    pygame.mixer.music.unload()
    pygame.mixer.music.load(MusicPath + music)
    pygame.mixer.music.play()
    global musicPlaying
    musicPlaying = 1

def main():
    global score, gameOver, level, k_up, k_down, k_left, k_right, entities, ghosts, wall
    global blinkGhost, clydeGhost, inkyGhost, pacman, timerStart, pinkyGhost, win, paused
    global musicPlaying, blinkGhost, game_first_input, running, gameOver, show_high_score, show_instructions  # Thêm 'show_instructions' vào đây

    init()
    if not start_screen():
        return
    timerCount = 0
    high_score_button = pygame.Rect(110, 260, 245, 50)  
    back_button = pygame.Rect(150, 250, 150, 50)  

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if show_high_score:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if back_button.collidepoint(mouse_pos):
                        show_high_score = False
            elif show_instructions:
                # Các sự kiện đã được xử lý trong instructions_screen()
                pass
            elif paused:
                # Xử lý sự kiện trong trạng thái tạm dừng nếu cần
                pass
            elif gameOver:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if high_score_button.collidepoint(mouse_pos):
                        show_high_score = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        gameOver = False
                        score = 0
                        game_first_input = False
                        entities.clear()
                        wall.clear()
                        ghosts.clear()
                        level.clear()

                        blinkGhost = None
                        clydeGhost = None
                        inkyGhost = None
                        pinkyGhost = None
                        pacman = None
                        timerStart = 0
                        win = False

                        init()
            elif win:
              
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        win = False
                        score = 0
                        game_first_input = False
                        entities.clear()
                        wall.clear()
                        ghosts.clear()
                        level.clear()

                        blinkGhost = None
                        clydeGhost = None
                        inkyGhost = None
                        pinkyGhost = None
                        pacman = None
                        timerStart = 0
                        gameOver = False

                        init()
            else:
                # Xử lý sự kiện trong trạng thái chơi bình thường
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        k_right.toggle(True)
                    elif event.key == pygame.K_LEFT:
                        k_left.toggle(True)
                    elif event.key == pygame.K_DOWN:
                        k_down.toggle(True)
                    elif event.key == pygame.K_UP:
                        k_up.toggle(True)
                    elif event.key == pygame.K_p:
                        paused = True
                        pause_screen()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_RIGHT:
                        k_right.toggle(False)
                    elif event.key == pygame.K_LEFT:
                        k_left.toggle(False)
                    elif event.key == pygame.K_DOWN:
                        k_down.toggle(False)
                    elif event.key == pygame.K_UP:
                        k_up.toggle(False)

        # Vẽ và cập nhật màn hình dựa trên trạng thái
        if show_high_score:
            screen.fill((0, 0, 0))
            back_button = draw_high_score_screen()
        elif show_instructions:
            # Màn hình hướng dẫn đã được vẽ trong instructions_screen()
            pass
        elif gameOver:
            screen.fill((0, 0, 0))
            save_high_score(score)  # Lưu điểm cao
            draw_game_over_screen(high_score_button)
            pygame.display.flip()
        elif win:
             draw_victory_screen()
             pygame.display.flip()
        elif paused:
            # Nếu cần vẽ gì đó trong trạng thái tạm dừng
            pass
        else:
            screen.fill((0, 0, 0))
            screen.blit(background_img, (0, 0))
            if not game_first_input:
                game_first_input = True
            if timerCount < (60 * 1):
                timerCount += 1
                drawString('READY', 200, 270)
            else:
                update()
            pacman.input()
            draw()
            checkGhostCollisionFrighten()
            checkFood()
            pygame.display.flip()

    pygame.quit()
