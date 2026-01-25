import pygame
from sys import exit
import random

# game client size
GAME_WIDTH = 540
GAME_HEIGHT = 960

# bird class
bird_x = 60
bird_y = 480
bird_width = 50
bird_height = 40

class Bird(pygame.Rect):
    def __init__(self, img):
        pygame.Rect.__init__(self, bird_x, bird_y, bird_width, bird_height)
        self.img = img

# pipe class
pipe_x = GAME_WIDTH
pipe_y = 0
pipe_width = 100
pipe_height = 600

class Pipe(pygame.Rect):
    def __init__(self, img):
        pygame.Rect.__init__(self, pipe_x, pipe_y, pipe_width, pipe_height)
        self.img = img
        self.passed = False

# images
background_img = pygame.image.load("images/background.png")
bird_img = pygame.image.load("images/bird.png")
bird_image = pygame.transform.scale(bird_img, (bird_width, bird_height))
pipe_top_img = pygame.image.load("images/pipe_top.png")
pipe_top_img = pygame.transform.scale(pipe_top_img, (pipe_width, pipe_height))
pipe_bottom_img = pygame.image.load("images/pipe_bottom.png")
pipe_bottom_img = pygame.transform.scale(pipe_bottom_img, (pipe_width, pipe_height))

# game logic
bird = Bird(bird_image)
pipes = []
velocity_x = -2 # move pipes to left velocity
velocity_y = 0 # move bird up/down velocity
gravity = 0.4 # bird gravity
score = 0 # how many pipes passed
high_score = 0 # session high score
game_over = False
paused = False

def draw():
    window.blit(background_img, (0, 0))
    window.blit(bird.img, bird)

    for pipe in pipes:
        window.blit(pipe.img, pipe)

    font = pygame.font.SysFont("Comic Sans" , 30)
    font2 = pygame.font.SysFont("Comic Sans" , 60)
    font3 = pygame.font.SysFont("Comic Sans" , 25)

    score_value = int(score)
    score_text = "SCORE: " + str(score_value)

    high_score_value = int(high_score)
    high_score_text = "PB: " + str(high_score_value)

    window.blit(font.render(score_text, True, pygame.Color("black")), (5, 0))
    window.blit(font.render(high_score_text, True, pygame.Color("black")), (250, 0))

    if game_over:
        game_over_text = "GAME OVER!"
        score_text = "SCORE: " +  str(score_value)
        again_text = "PRESS ENTER TO TRY AGAIN"

        window.blit(font2.render(game_over_text, True, pygame.Color("black")), (80, 300))
        window.blit(font2.render(score_text, True, pygame.Color("black")), (80, 370))
        window.blit(font3.render(again_text, True, pygame.Color("black")), (80, 470))

        pygame.mixer.Sound("sounds/gameover.mp3").play()

def move():
    global velocity_y, score, game_over, high_score
    velocity_y += gravity
    bird.y += velocity_y

    if bird.y > GAME_HEIGHT: # game over if the bird falls off the map
        game_over = True
        return
    
    if bird.y < 0: # game over if the bird hits top of the map 
        game_over = True
        return

    for pipe in pipes:
        pipe.x += velocity_x

        if not pipe.passed and bird.x > pipe.x:
            score += 0.5 # 0.5 because there are 2 pipes passed at a time (top and bottom pipe)
            pipe.passed = True
            pygame.mixer.Sound("sounds/score.mp3").play()

        if score > high_score:
            high_score = score

        if bird.colliderect(pipe): # game over if the bird hits a pipe
            game_over = True
            return


    # remove pipes off-screen
    while len(pipes) > 0 and pipes[0].x + pipe_width < 0:
        pipes.pop(0)

def create_pipes():
    pipe_random_y = pipe_y - random.random() * 400 # pipe y position randomised 0-400
    pipe_gap = 200 # gap between top and bottom pipe

    pipe_top = Pipe(pipe_top_img)
    pipe_top.y = pipe_random_y
    pipes.append(pipe_top)

    pipe_bottom = Pipe(pipe_bottom_img)
    pipe_bottom.y = pipe_top.y + pipe_top.height + pipe_gap
    pipes.append(pipe_bottom)

# fps counter
def fps_counter():
    font = pygame.font.SysFont("Comic Sans" , 30)

    fps = int(clock.get_fps())
    fps_text = "FPS: " + str(fps)
    window.blit(font.render(fps_text, True, pygame.Color("black")), (430, 0))

pygame.init()
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

pipes_timer = pygame.USEREVENT + 0
pygame.time.set_timer(pipes_timer, 2000) # new pipe every 2 seconds

# game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and not game_over and not paused:
                paused = True # pause game

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and paused:
                paused = False # unpause
                pygame.time.set_timer(pipes_timer, 2000) # resets pipe spawn timer after pause to prevent pipes from spawning too close together

        if event.type == pipes_timer and not game_over and not paused:
            create_pipes() # spawn pipes on set interval and while game is not over

        if event.type == pygame.KEYDOWN:
            if not game_over and not paused and event.key in (pygame.K_SPACE, pygame.K_UP): # if spacebar or UP-arrow is pressed
                velocity_y = -6 # bird velocity upwards
                pygame.mixer.Sound("sounds/fly.mp3").play()

            # reset game after game over
            if game_over and event.key == pygame.K_RETURN:
                bird.y = bird_y
                velocity_y = 0
                pipes.clear()
                score = 0
                game_over = False

    if not game_over and not paused:
        move()
        draw()
        fps_counter()

    if paused:
        font = pygame.font.SysFont("Comic Sans" , 30)
        font2 = pygame.font.SysFont("Comic Sans" , 60)

        pause_text = "GAME PAUSED"
        continue_text = "PRESS ENTER TO CONTINUE"

        window.blit(font2.render(pause_text, True, pygame.Color("black")), (60, 300))
        window.blit(font.render(continue_text, True, pygame.Color("black")), (60, 370))

    pygame.display.update()
    clock.tick(60) # game runs 60 fps