import asyncio
import random

import pygame

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


async def main():
    global bird, pipes, velocity_x, velocity_y, gravity, score, high_score
    global game_over, paused, window, clock

    pygame.mixer.pre_init(44100, -16, 2, 1024)  # match browser audio rate, roomy buffer
    pygame.init()
    window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    pygame.display.set_caption("Flappy Bird")
    clock = pygame.time.Clock()

    # match the page background (behind/around the canvas) to the sky; no-op on desktop
    try:
        import platform
        platform.document.body.style.background = "#16171d"
    except (ImportError, AttributeError):
        pass

    # images (load after set_mode so they can be converted for the web canvas)
    background_img = pygame.image.load("images/background.png").convert()
    bird_img = pygame.image.load("images/bird.png").convert_alpha()
    bird_image = pygame.transform.scale(bird_img, (bird_width, bird_height))
    pipe_top_img = pygame.image.load("images/pipe_top.png").convert_alpha()
    pipe_top_img = pygame.transform.scale(pipe_top_img, (pipe_width, pipe_height))
    pipe_bottom_img = pygame.image.load("images/pipe_bottom.png").convert_alpha()
    pipe_bottom_img = pygame.transform.scale(pipe_bottom_img, (pipe_width, pipe_height))

    # fonts (create once, not every frame; Font(None) = built-in font, safe on web)
    font = pygame.font.Font(None, 38)
    font2 = pygame.font.Font(None, 72)
    font3 = pygame.font.Font(None, 30)

    # sounds (preload once; guard in case audio is unavailable)
    def load_sound(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            return None

    fly_sound = load_sound("sounds/fly.ogg")
    score_sound = load_sound("sounds/score.ogg")
    gameover_sound = load_sound("sounds/gameover.ogg")

    def play(sound):
        if sound is not None:
            sound.stop()  # avoid the same clip stacking on itself (sounds harsh on rapid flaps)
            sound.play()

    def blit_centered(text_font, text, y, color="black"):
        surface = text_font.render(text, True, pygame.Color(color))
        window.blit(surface, surface.get_rect(center=(GAME_WIDTH // 2, y)))

    # game logic
    bird = Bird(bird_image)
    pipes = []
    velocity_x = -2  # move pipes to left velocity
    velocity_y = 0  # move bird up/down velocity
    gravity = 0.4  # bird gravity
    score = 0  # how many pipes passed
    high_score = 0  # session high score
    game_over = False
    paused = False
    gameover_played = False

    def draw():
        window.blit(background_img, (0, 0))
        window.blit(bird.img, bird)

        for pipe in pipes:
            window.blit(pipe.img, pipe)

        score_value = int(score)
        score_text = "SCORE: " + str(score_value)
        high_score_text = "PB: " + str(int(high_score))

        window.blit(font.render(score_text, True, pygame.Color("black")), (5, 0))

        pb_surface = font.render(high_score_text, True, pygame.Color("black"))
        window.blit(pb_surface, (GAME_WIDTH - pb_surface.get_width() - 5, 0))

        if game_over:
            blit_centered(font2, "GAME OVER!", 330)
            blit_centered(font2, "SCORE: " + str(score_value), 400)
            blit_centered(font3, "PRESS ENTER TO TRY AGAIN", 470)

    def move():
        nonlocal gameover_played
        global velocity_y, score, game_over, high_score
        velocity_y += gravity
        bird.y += velocity_y

        if bird.y > GAME_HEIGHT:  # game over if the bird falls off the map
            game_over = True
            return

        if bird.y < 0:  # game over if the bird hits top of the map
            game_over = True
            return

        for pipe in pipes:
            pipe.x += velocity_x

            if not pipe.passed and bird.x > pipe.x:
                score += 0.5  # 0.5 because 2 pipes are passed at a time (top and bottom)
                pipe.passed = True
                play(score_sound)

            if score > high_score:
                high_score = score

            if bird.colliderect(pipe):  # game over if the bird hits a pipe
                game_over = True
                return

        # remove pipes off-screen
        while len(pipes) > 0 and pipes[0].x + pipe_width < 0:
            pipes.pop(0)

    def create_pipes():
        pipe_random_y = pipe_y - random.random() * 400  # pipe y position randomised 0-400
        pipe_gap = 200  # gap between top and bottom pipe

        pipe_top = Pipe(pipe_top_img)
        pipe_top.y = pipe_random_y
        pipes.append(pipe_top)

        pipe_bottom = Pipe(pipe_bottom_img)
        pipe_bottom.y = pipe_top.y + pipe_top.height + pipe_gap
        pipes.append(pipe_bottom)

    PIPE_INTERVAL = 2000  # spawn a new pipe pair every 2 seconds
    last_pipe_time = pygame.time.get_ticks()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not game_over and not paused:
                    paused = True  # pause game

                if event.key == pygame.K_RETURN and paused:
                    paused = False  # unpause
                    last_pipe_time = pygame.time.get_ticks()  # reset spawn timer after pause

                if not game_over and not paused and event.key in (pygame.K_SPACE, pygame.K_UP):
                    velocity_y = -6  # bird velocity upwards
                    play(fly_sound)

                # reset game after game over
                if game_over and event.key == pygame.K_RETURN:
                    bird.y = bird_y
                    velocity_y = 0
                    pipes.clear()
                    score = 0
                    game_over = False
                    gameover_played = False
                    last_pipe_time = pygame.time.get_ticks()

        # spawn pipes on interval while the game is running (set_timer is unavailable on web)
        now = pygame.time.get_ticks()
        if not game_over and not paused and now - last_pipe_time >= PIPE_INTERVAL:
            create_pipes()
            last_pipe_time = now

        if not game_over and not paused:
            move()
            draw()
        elif game_over:
            draw()
            if not gameover_played:
                play(gameover_sound)
                gameover_played = True
        elif paused:
            blit_centered(font2, "GAME PAUSED", 330)
            blit_centered(font, "PRESS ENTER TO CONTINUE", 400)

        pygame.display.update()
        clock.tick(60)  # game runs 60 fps
        await asyncio.sleep(0)  # hand control back to the browser each frame

    pygame.quit()


asyncio.run(main())
