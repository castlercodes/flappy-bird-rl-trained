import pygame, random
from pygame.locals import *
from agent import train

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 800
SPEED = 10
GRAVITY = 1
GAME_SPEED = 10

GROUND_WIDTH = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 100

PIPE_WIDTH = 80
PIPE_HEIGHT = 500

PIPE_GAP = 200

pygame.font.init()
font = pygame.font.Font(None, 36) 

class Bird(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.images = [pygame.image.load('bluebird-upflap.png').convert_alpha(),
                       pygame.image.load('bluebird-midflap.png').convert_alpha(),
                       pygame.image.load('bluebird-downflap.png').convert_alpha()]

        self.speed = SPEED

        self.current_image = 0

        self.image = pygame.image.load('bluebird-upflap.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDTH / 2
        self.rect[1] = SCREEN_HEIGHT / 2

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[ self.current_image ]

        self.speed += GRAVITY

        # Update height
        self.rect[1] += self.speed
    
    def bump(self):
        self.speed = -SPEED

class Pipe(pygame.sprite.Sprite):

    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load('pipe-red.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDTH,PIPE_HEIGHT))

        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect[0] -= GAME_SPEED

class Ground(pygame.sprite.Sprite):

    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load('base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDTH, GROUND_HEIGHT))

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT
    
    def update(self):
        self.rect[0] -= GAME_SPEED

def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])

def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return (pipe, pipe_inverted)


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

BACKGROUND = pygame.image.load('background-day.png')
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))


def initialize_game():
    global bird, bird_group, pipe_group, ground_group, distance, game_over, reward, score, previous_pos, current_pos
    previous_pos = SCREEN_HEIGHT / 2
    current_pos = SCREEN_HEIGHT / 2
    reward = 0
    score = 0
    distance = 0
    game_over = 0       
    bird_group = pygame.sprite.Group()
    bird = Bird()
    bird_group.add(bird)

    ground_group = pygame.sprite.Group()
    for i in range(2):
        ground = Ground(GROUND_WIDTH * i)
        ground_group.add(ground)

    pipe_group = pygame.sprite.Group()
    for i in range(2):
        pipes = get_random_pipes(SCREEN_WIDTH * i + 800)
        pipe_group.add(pipes[0])
        pipe_group.add(pipes[1])

initialize_game()

clock = pygame.time.Clock()

def get_state():
    bird_state = [bird.rect[1], bird.speed]  # Bird's vertical position and speed

    # Check if there is a pipe in the bird's forward path at the current height
    danger_forward = 0

    for move in range(0, 150): 
        temp_bird_forward = Bird()
        temp_bird_forward.rect = bird.rect.move(move, 0)
        if any(pygame.sprite.spritecollide(temp_bird_forward, pipe_group, False, pygame.sprite.collide_mask)):
            danger_forward = 1
            break  # Break out of the loop if a collision is detected

    temp_bird_up = Bird()
    temp_bird_up.rect = bird.rect.move(0, temp_bird_up.rect[1] - SPEED + GRAVITY)
    danger_up = any(pygame.sprite.spritecollide(temp_bird_up, pipe_group, False, pygame.sprite.collide_mask))
    danger_up = int(danger_up or (temp_bird_up.rect[1] - SPEED + GRAVITY < 0))

    temp_bird_down = Bird()
    temp_bird_down.rect = bird.rect.move(0, temp_bird_down.rect[1] + temp_bird_down.speed + GRAVITY)
    danger_down = any(pygame.sprite.spritecollide(temp_bird_down, pipe_group, False, pygame.sprite.collide_mask))
    danger_down = int(danger_down or (temp_bird_down.rect[1] + temp_bird_down.speed + GRAVITY > SCREEN_HEIGHT))

    inverted_pipe_bottom = pipe_group.sprites()[1].rect[1] + PIPE_HEIGHT
    correct_pipe_top = pipe_group.sprites()[0].rect[1]  

    mid_pipe_position = (inverted_pipe_bottom + correct_pipe_top) / 2

    opening_up = 0
    opening_down = 0

    if mid_pipe_position <= bird.rect[1]:
        opening_up = 1
    
    if mid_pipe_position >= bird.rect[1]:
        opening_down = 1

    state = bird_state + [danger_forward, danger_down, danger_up, inverted_pipe_bottom, correct_pipe_top]

    return state

def play_step(action):
    
    global bird, bird_group, pipe_group, ground_group, distance, game_over, reward, score, previous_pos, current_pos
    reward = 0

    clock.tick(1000)
    if action == 1:
        bird.bump() 

    # print(action)

    current_pos = bird.rect[1]
    
    screen.blit(BACKGROUND, (0, 0))

    if is_off_screen(ground_group.sprites()[0]):
        ground_group.remove(ground_group.sprites()[0])

        new_ground = Ground(GROUND_WIDTH - 20)
        ground_group.add(new_ground)

    if is_off_screen(pipe_group.sprites()[0]):
        pipe_group.remove(pipe_group.sprites()[0])
        pipe_group.remove(pipe_group.sprites()[0])

        pipes = get_random_pipes(SCREEN_WIDTH * 2)

        pipe_group.add(pipes[0])
        pipe_group.add(pipes[1])

    bird_group.update()
    ground_group.update()
    pipe_group.update()

    bird_group.draw(screen)
    pipe_group.draw(screen)
    ground_group.draw(screen)

    if game_over:
        text = font.render("Game Over", True, (255, 255, 255))  # White text
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    else :
        distance += GAME_SPEED / 10

    text = font.render(f"Distance: {int(distance)} pixels", True, (255, 255, 255))  # White text
    screen.blit(text, (10, 10))

    pygame.display.update()

    inverted_pipe_bottom = pipe_group.sprites()[1].rect[1] + PIPE_HEIGHT
    correct_pipe_top = pipe_group.sprites()[0].rect[1]  

    if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
    pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask)) or bird.rect[1] < 0:
        # Game over
        reward = -100
        game_over = 1

    else:
        score += 1

    mid_of_pipe = (inverted_pipe_bottom + correct_pipe_top) / 2
    
    if abs(previous_pos - mid_of_pipe) > abs(current_pos - mid_of_pipe) or inverted_pipe_bottom + 50 <= bird.rect[1] <= correct_pipe_top - 50:
        reward = 30
    else:
        reward = -100

    # print(reward, game_over, score)
    previous_pos = current_pos
    return reward, game_over, score

while True:
    train(initialize_game, get_state, play_step)
