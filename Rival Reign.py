#-----------------------------------------------------------------------------------------------
#Import statements
#-----------------------------------------------------------------------------------------------
import pygame
from datetime import datetime
import random
import sys
#-----------------------------------------------------------------------------------------------
#Initialising Pygame
#-----------------------------------------------------------------------------------------------
pygame.mixer.init()
pygame.init()
#-----------------------------------------------------------------------------------------------
#Game variables
#-----------------------------------------------------------------------------------------------
pygame.mixer.music.load("assets/audio/music.wav")
pygame.mixer.music.set_volume(1)
pygame.mixer.music.play(-1, 0.0, 5000)
sword_fx = pygame.mixer.Sound("assets/audio/sword.wav")
sword_fx.set_volume(0.5)
magic_fx = pygame.mixer.Sound("assets/audio/magic.wav")
magic_fx.set_volume(0.75)

info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Rival Reign")
icon = pygame.image.load("assets/images/icons/Rival icon.jpg")
pygame.display.set_icon(icon)

RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREEN = (1, 150, 32)
BLUE = (51, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

pygame.font.init()

SPEED = 10
GRAVITY = 2
#-----------------------------------------------------------------------------------------------
#Fighter Class
#-----------------------------------------------------------------------------------------------
class Fighter:
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0  
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.attack_sound = sound
        self.hit = False
        self.health = 100
        self.alive = True

    def load_images(self, sprite_sheet, animation_steps):
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(
                    x * self.size, y * self.size, self.size, self.size
                )
                temp_img_list.append(
                    pygame.transform.scale(
                        temp_img, (self.size * self.image_scale, self.size * self.image_scale)
                    )
                )
            animation_list.append(temp_img_list)
        return animation_list

    def move(self, screen_width, screen_height, surface, target, round_over):
        pass

    def attack(self, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            self.attack_sound.play()
            attacking_rect = pygame.Rect(
                self.rect.centerx - (2 * self.rect.width * self.flip),
                self.rect.y,
                2 * self.rect.width,
                self.rect.height
            )
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True

    def update(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)  
            self.rect.y = max(self.rect.y, SCREEN_HEIGHT - 170 - self.rect.height / 2)
        elif self.hit:
            self.update_action(5)  
        elif self.attacking:
            if self.attack_type == 1:
                self.update_action(3)  
            elif self.attack_type == 2:
                self.update_action(4)  
        elif self.jump:
            self.update_action(2)  
        elif self.running:
            self.update_action(1)  
        else:
            self.update_action(0)  

        animation_cooldown = 50
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.animation_list[self.action]):
            if not self.alive:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                if self.action == 5:
                    self.hit = False
                    self.attacking = False
                    self.attack_cooldown = 20

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(
            img,
            (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale))
        )
#-----------------------------------------------------------------------------------------------
#Separate move function for single player mode
#-----------------------------------------------------------------------------------------------
class SinglePlayerFighter(Fighter):
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound, ai=False, selected_level=None):
        super().__init__(player, x, y, flip, data, sprite_sheet, animation_steps, sound)
        self.ai = ai
        self.attack_timer = 0
        self.selected_level = selected_level

    def move(self, screen_width, screen_height, surface, target, round_over):
        if not self.alive:
            return

        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        keys = pygame.key.get_pressed()

        if self.ai:
            distance = abs(self.rect.centerx - target.rect.centerx)
            if target.alive:
                if distance < 200:
                    if random.choice([True, False]):
                        if not self.jump:
                            self.vel_y = -30
                            self.jump = True
                    else:
                        if self.rect.centerx < target.rect.centerx:
                            dx = SPEED
                        elif self.rect.centerx > target.rect.centerx:
                            dx = -SPEED

            if self.selected_level == 0:
                timer = 500
            elif self.selected_level == 1:
                timer = 260
            elif self.selected_level == 2:
                timer = 130
            if target.alive and pygame.time.get_ticks() - self.attack_timer > timer and distance < 150:
                self.attack(target)
                self.attack_type = random.randint(1, 2)
                self.attack_timer = pygame.time.get_ticks()

        else:
            if self.attacking == False and self.alive == True and round_over == False:
                if self.player == 1:
                    if keys[pygame.K_a]:
                        dx = -SPEED
                        self.running = True
                    if keys[pygame.K_d]:
                        dx = SPEED
                        self.running = True
                    if keys[pygame.K_w] and self.jump == False:
                        self.vel_y = -30
                        self.jump = True

                    mouse_buttons = pygame.mouse.get_pressed()
                    if mouse_buttons[0]:  
                        self.attack(target)
                        self.attack_type = 1
                    if mouse_buttons[2]:  
                        self.attack(target)
                        self.attack_type = 2

        self.vel_y += GRAVITY
        dy += self.vel_y

        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 80:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 80 - self.rect.bottom

        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.rect.x += dx
        self.rect.y += dy
#-----------------------------------------------------------------------------------------------
#Separate move function for two player mode
#-----------------------------------------------------------------------------------------------
class TwoPlayerFighter(Fighter):
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
        super().__init__(player, x, y, flip, data, sprite_sheet, animation_steps, sound)

    def move(self, screen_width, screen_height, surface, target, round_over):
        if not self.alive:
            return

        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        keys = pygame.key.get_pressed()

        if self.attacking == False and self.alive == True and round_over == False:
            if self.player == 1:
                if keys[pygame.K_a]:
                    dx = -SPEED
                    self.running = True
                if keys[pygame.K_d]:
                    dx = SPEED
                    self.running = True
                if keys[pygame.K_w] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True

                if keys[pygame.K_r]:  
                    self.attack(target)
                    self.attack_type = 1
                if keys[pygame.K_t]:  
                    self.attack(target)
                    self.attack_type = 2

            elif self.player == 2:
                if keys[pygame.K_LEFT]:
                    dx = -SPEED
                    self.running = True
                if keys[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True
                if keys[pygame.K_UP] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True

                if keys[pygame.K_KP1]:  
                    self.attack(target)
                    self.attack_type = 1
                if keys[pygame.K_KP2]:  
                    self.attack(target)
                    self.attack_type = 2

        self.vel_y += GRAVITY
        dy += self.vel_y

        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 80:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 80 - self.rect.bottom
            
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.rect.x += dx
        self.rect.y += dy
#-----------------------------------------------------------------------------------------------
#Pause screen
#-----------------------------------------------------------------------------------------------
def display_pause_screen(game_mode, player1_name, player2_name, score, game_level):
    pause_font = pygame.font.Font("assets/fonts/turok.ttf", 90)
    options_font = pygame.font.Font("assets/fonts/turok.ttf", 40)
    options = "Press SPACE to resume."
    single_player_image = pygame.image.load('assets/images/background/Single player controls.png')
    two_player_image = pygame.image.load('assets/images/background/Two player controls.png')
    
    screen.fill((0, 0, 0))
    draw_text("PAUSED", pause_font, RED, SCREEN_WIDTH / 2 - 125, 40)
    draw_text(options, options_font, WHITE, SCREEN_WIDTH / 2 - 195, 140)

    back_image = pygame.image.load("assets/images/icons/quit.png").convert_alpha()
    back_rect = back_image.get_rect(center=(SCREEN_WIDTH * 0.95, SCREEN_HEIGHT * 0.93))
    screen.blit(back_image, back_rect.topleft)
    if game_mode == 0:
        screen.blit(single_player_image,(180,240))

    else:
        screen.blit(two_player_image,(180,240))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  
                    return
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(event.pos):
                    save_scores(game_mode, player1_name, player2_name, score, game_level)
                    main_menu()  

        pygame.display.update()
#-----------------------------------------------------------------------------------------------
#Draw player name and score in the game window
#-----------------------------------------------------------------------------------------------
def draw_names(name1, name2, score_font):
    draw_text(name1, score_font, RED, SCREEN_WIDTH * 0.0147, SCREEN_HEIGHT * 0.0857)
    draw_text(name2, score_font, RED, SCREEN_WIDTH * 0.6852, SCREEN_HEIGHT * 0.0857)
#-----------------------------------------------------------------------------------------------
#Draw player health bar in the game window
#-----------------------------------------------------------------------------------------------
def draw_health_bar(health, x, y):
    bar_width = int(SCREEN_WIDTH * 0.3)
    bar_height = int(SCREEN_HEIGHT * 0.04)
    outline_thickness = 2
    
    ratio = health / 100

    pygame.draw.rect(screen, WHITE, (x - outline_thickness, y - outline_thickness, bar_width + outline_thickness * 2, bar_height + outline_thickness * 2))
    pygame.draw.rect(screen, RED, (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (x, y, bar_width * ratio, bar_height))
#-----------------------------------------------------------------------------------------------
#Draw text
#-----------------------------------------------------------------------------------------------
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))
#-----------------------------------------------------------------------------------------------
#Draw background frame by frame
#-----------------------------------------------------------------------------------------------
background_frame_index = 0
background_frame_timer = pygame.time.get_ticks()
BACKGROUND_FRAME_DELAY = 35 
def draw_bg(background_frames):
    global background_frame_index, background_frame_timer

    if pygame.time.get_ticks() - background_frame_timer > BACKGROUND_FRAME_DELAY:
        background_frame_index = (background_frame_index + 1) % len(background_frames)
        background_frame_timer = pygame.time.get_ticks()

    scaled_bg = pygame.transform.scale(background_frames[background_frame_index], (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0, 0))
#-----------------------------------------------------------------------------------------------
#Play again or quit screen
#-----------------------------------------------------------------------------------------------
def final_screen():
    foption_font = pygame.font.Font("assets/fonts/turok.ttf", 60)

    menu_running = True

    play_again_text = "Play Again"
    quit_text = "Quit"
    play_again_rect = pygame.Rect(SCREEN_WIDTH / 2 - foption_font.size(play_again_text)[0] / 2, SCREEN_HEIGHT / 2 - 50, 300, 40)
    quit_rect = pygame.Rect(SCREEN_WIDTH / 2 - foption_font.size(quit_text)[0] / 2, SCREEN_HEIGHT / 2 + 10, 300, 40)

    while menu_running:
        scaledbg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaledbg, (0, 0))
        
        draw_text(play_again_text, foption_font, BLUE, SCREEN_WIDTH / 2 - foption_font.size(play_again_text)[0] / 2, SCREEN_HEIGHT / 2 - 50)
        draw_text(quit_text, foption_font, BLUE, SCREEN_WIDTH / 2 - foption_font.size(quit_text)[0] / 2, SCREEN_HEIGHT / 2 + 10)

        mouse_pos = pygame.mouse.get_pos()

        if play_again_rect.collidepoint(mouse_pos):
            draw_text(play_again_text, foption_font, GREEN, SCREEN_WIDTH / 2 - foption_font.size(play_again_text)[0] / 2, SCREEN_HEIGHT / 2 - 50)
            
        if quit_rect.collidepoint(mouse_pos):
            draw_text(quit_text, foption_font, RED, SCREEN_WIDTH / 2 - foption_font.size(quit_text)[0] / 2, SCREEN_HEIGHT / 2 + 10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_rect.collidepoint(mouse_pos):
                    display_menu()
                if quit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
#-----------------------------------------------------------------------------------------------
#Score saved to text file
#-----------------------------------------------------------------------------------------------
def save_scores(game_mode, player1_name, player2_name, score, game_level=None):
    level_names = {0: "Easy", 1: "Medium", 2: "Difficult"}
    
    try:
        with open("score.txt", "a") as file:
            if game_mode == 0:
                mode = "SINGLE PLAYER"
            else:
                mode = "TWO PLAYER"
            now = datetime.now()
            fnow = now.strftime("%Y-%m-%d   %I:%M:%S %p")
            
            file.write(f"{mode}\n")
            if game_mode == 0 and game_level is not None:
                file.write(f"Level: {level_names[game_level]}\n")
            file.write(f"{player1_name}: {score[0]}\n")
            file.write(f"{player2_name}: {score[1]}\n")
            file.write(f"{fnow}\n")
            file.write("-------------------------------\n")

        print(f"Scores saved: {player1_name} - {score[0]}, {player2_name} - {score[1]}")
    except Exception as e:
        print(f"Error saving scores: {e}")

#-----------------------------------------------------------------------------------------------
#Versus screen
#-----------------------------------------------------------------------------------------------
def vs(vs_image, player1_name, player2_name, duration=5000):
    score_font = pygame.font.Font("assets/fonts/turok.ttf", 60)
    vs_image_resized = pygame.transform.scale(vs_image, (int(SCREEN_WIDTH), int(SCREEN_HEIGHT * 0.7)))
    vs_rect = vs_image_resized.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    start_time = pygame.time.get_ticks()

    while True:
        screen.fill((0, 0, 0))
        screen.blit(vs_image_resized, vs_rect)
        draw_text(f"{player1_name}", score_font, (255, 255,255), SCREEN_WIDTH * 0.1617, SCREEN_HEIGHT * 0.4429)
        draw_text(f"{player2_name}", score_font, (255, 255,255), SCREEN_WIDTH * 0.7206, SCREEN_HEIGHT * 0.4429)

        pygame.display.update()

        current_time = pygame.time.get_ticks()
        if current_time - start_time >= duration:
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
#-----------------------------------------------------------------------------------------------
#Main game function
#---------------------------------------------------------------------------------------------    
def game(vs_image, player1_name, player2_name, game_mode, game_level):
    clock = pygame.time.Clock()
    run = True  
    paused = False  
    game_over = False
    current_state = "vs_screen"  
    vs_start_time = pygame.time.get_ticks()  
    VS_DISPLAY_DURATION = 3000  
    intro_count = 4
    last_count_update = pygame.time.get_ticks()
    score = [0, 0]  
    round_over = False
    ROUND_OVER_COOLDOWN = 2000
    scores_saved = False

    WARRIOR_SIZE = 162
    WARRIOR_SCALE = 4
    WARRIOR_OFFSET = [72, 47]
    WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]
    WIZARD_SIZE = 250
    WIZARD_SCALE = 3
    WIZARD_OFFSET = [112, 95]
    WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]

    background_frames = []
    for i in range(1, 12):
        frame = pygame.image.load(f"assets/images/background/Frames 3/frame ({i}).png").convert_alpha()
        background_frames.append(frame)

    warrior_sheet = pygame.image.load("assets/images/warrior/Sprites/warrior.png").convert_alpha()
    wizard_sheet = pygame.image.load("assets/images/wizard/Sprites/wizard.png").convert_alpha()

    WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]
    WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]

    if game_mode == 0:  
        fighter_1 = SinglePlayerFighter(1, int(SCREEN_WIDTH * 0.22), int(SCREEN_HEIGHT * 0.44), False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx, ai=False, selected_level=game_level)
        fighter_2 = SinglePlayerFighter(2, int(SCREEN_WIDTH * 0.74), int(SCREEN_HEIGHT * 0.44), True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx, ai=True, selected_level=game_level)
    else:  
        fighter_1 = TwoPlayerFighter(1, int(SCREEN_WIDTH * 0.22), int(SCREEN_HEIGHT * 0.44), False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
        fighter_2 = TwoPlayerFighter(2, int(SCREEN_WIDTH * 0.74), int(SCREEN_HEIGHT * 0.44), False, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)

    FPS = 60
    MESSAGE_DISPLAY_TIME = 5000
    score_font = pygame.font.Font("assets/fonts/turok.ttf", 40)  
    game_over_font = pygame.font.Font("assets/fonts/turok.ttf", 90)  

    while run:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if not scores_saved:
                    save_scores(game_mode, player1_name, player2_name, score, game_level)
                    scores_saved = True
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if not game_over:  
                    if event.key == pygame.K_SPACE:  
                        paused = not paused  
                        if paused:
                            display_pause_screen(game_mode, player1_name, player2_name, score, game_level)  
                            paused = False  
                else:
                    run = False  

        if not paused and not game_over:  
            if current_state == "vs_screen":
                vs(vs_image, player1_name, player2_name)
                pygame.display.update()

                if pygame.time.get_ticks() - vs_start_time > VS_DISPLAY_DURATION:
                    current_state = "playing"

            elif current_state == "playing":
                draw_bg(background_frames)

                draw_names(player1_name, player2_name, score_font)
                draw_health_bar(fighter_1.health, SCREEN_WIDTH * 0.0147, SCREEN_HEIGHT * 0.0285)
                draw_health_bar(fighter_2.health, SCREEN_WIDTH * 0.6852, SCREEN_HEIGHT * 0.0285)

                draw_text(f"{player1_name}: {score[0]}", score_font, RED, SCREEN_WIDTH * 0.0147, SCREEN_HEIGHT * 0.0857)  
                draw_text(f"{player2_name}: {score[1]}", score_font, RED, SCREEN_WIDTH * 0.6852, SCREEN_HEIGHT * 0.0857)
  

                if intro_count <= 0:
                    fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over)
                    fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over)
                else:
                    draw_text(str(intro_count), pygame.font.Font("assets/fonts/turok.ttf", 90), RED, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
                    if pygame.time.get_ticks() - last_count_update >= 1000:
                        intro_count -= 1
                        last_count_update = pygame.time.get_ticks()

                fighter_1.update()
                fighter_2.update()
                fighter_1.draw(screen)
                fighter_2.draw(screen)

                if not round_over:
                    if not fighter_1.alive:
                        score[1] += 1
                        round_over = True
                        round_over_time = pygame.time.get_ticks()
                        message = f"{player2_name} WINS!" if game_mode == 1 else "DEFEAT!"
                        message_display_start_time = pygame.time.get_ticks()
                    elif not fighter_2.alive:
                        score[0] += 1
                        round_over = True
                        round_over_time = pygame.time.get_ticks()
                        message = f"{player1_name} WINS!" if game_mode == 1 else "VICTORY!"
                        message_display_start_time = pygame.time.get_ticks()
                else:
                    if pygame.time.get_ticks() - message_display_start_time <= MESSAGE_DISPLAY_TIME:
                        message_text = (pygame.font.Font("assets/fonts/turok.ttf", 90)).render(message, True, RED)
                        message_x = SCREEN_WIDTH / 2 - message_text.get_width() / 2
                        draw_text(message, pygame.font.Font("assets/fonts/turok.ttf", 90), RED, message_x, SCREEN_HEIGHT / 2.5)
                    elif pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                        if score[0] == 3 or score[1] == 3:
                            save_scores(game_mode, player1_name, player2_name, score, game_level)
                            scores_saved = True
                            game_over = True  
                        else:
                            round_over = False
                            intro_count = 4
                            if game_mode == 0:
                                fighter_1 = SinglePlayerFighter(1, 300, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx, ai=False, selected_level=game_level)
                                fighter_2 = SinglePlayerFighter(2, 1000, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx, ai=True, selected_level=game_level)
                            else:
                                fighter_1 = TwoPlayerFighter(1, 300, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
                                fighter_2 = TwoPlayerFighter(2, 1000, 310, False, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)

        if game_over:
            draw_text("GAME OVER", game_over_font, RED, SCREEN_WIDTH / 2 - 190, SCREEN_HEIGHT / 2 - 90)
            draw_text(f"{player1_name}: {score[0]}  {player2_name}: {score[1]}", score_font, RED, SCREEN_WIDTH / 2 - 155, SCREEN_HEIGHT / 2 + 10)
            draw_text("Press any key to continue", score_font, (51, 255, 255), SCREEN_WIDTH / 2 - 210, SCREEN_HEIGHT / 2 + 70)

        pygame.display.update()

    final_screen()
#-----------------------------------------------------------------------------------------------
#Instructions screen
#-----------------------------------------------------------------------------------------------
def display_instructions(game_mode, player1_name, player2_name, game_level):
    instructions_font = pygame.font.Font("assets/fonts/turok.ttf", 40)
    option_font = pygame.font.Font("assets/fonts/turok.ttf", 40)
    
    single_player_image = pygame.image.load('assets/images/background/Single player controls.png')
    two_player_image = pygame.image.load('assets/images/background/Two player controls.png')
    
    back_text = "Back"
    quit_text = "Quit"
    back_rect = pygame.Rect(SCREEN_WIDTH * 0.01, SCREEN_HEIGHT * 0.93, 300, 40)
    quit_rect = pygame.Rect(SCREEN_WIDTH * 0.94, SCREEN_HEIGHT * 0.93, 300, 40)

    if game_mode == 0:
        single_player_image_resized = pygame.transform.scale(single_player_image, (int(SCREEN_WIDTH * 0.6), int(SCREEN_HEIGHT * 0.5)))
        screen.blit(single_player_image_resized, (SCREEN_WIDTH * 0.2, SCREEN_HEIGHT * 0.35))
        instructions = [
            "Instructions:",
            "1. The first player to reach 3 points wins!",
            "2. Press space to pause/resume",
            "",
            "Press Enter key to start the match."]
    else:
        two_player_image_resized = pygame.transform.scale(two_player_image, (int(SCREEN_WIDTH * 0.6), int(SCREEN_HEIGHT * 0.5)))
        screen.blit(two_player_image_resized, (SCREEN_WIDTH * 0.2, SCREEN_HEIGHT * 0.35))
        instructions = [
            "Instructions:",
            "1. The first player to reach 3 points wins!",
            "2. Press space to pause/resume",
            "",
            "Press Enter key to start the match."]

    while True:

        mouse_pos = pygame.mouse.get_pos()
        if back_rect.collidepoint(mouse_pos):
            draw_text(back_text, option_font, YELLOW, SCREEN_WIDTH * 0.01, SCREEN_HEIGHT * 0.93)
        else:
            draw_text(back_text, option_font, WHITE, SCREEN_WIDTH * 0.01, SCREEN_HEIGHT * 0.93)
            
        if quit_rect.collidepoint(mouse_pos):
            draw_text(quit_text, option_font, RED, SCREEN_WIDTH * 0.94, SCREEN_HEIGHT * 0.93)
        else:
            draw_text(quit_text, option_font, WHITE, SCREEN_WIDTH * 0.94, SCREEN_HEIGHT * 0.93)

        y_offset = SCREEN_HEIGHT * 0.01
        for line in instructions[:-1]:
            draw_text(line, instructions_font, (51, 255, 255), SCREEN_WIDTH / 80, y_offset)
            y_offset += 40

        enter_text = instructions[-1]
        enter_text_surface = instructions_font.render(enter_text, True, (51, 255, 255))
        enter_text_x = (SCREEN_WIDTH - enter_text_surface.get_width()) / 2
        enter_text_y = y_offset
        screen.blit(enter_text_surface, (enter_text_x, enter_text_y))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    vs_image = pygame.image.load("assets/images/vs/vs6.jpg").convert_alpha()
                    game(vs_image, player1_name, player2_name, game_mode, game_level)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(event.pos):
                    if game_mode == 0:
                        get_player_names(0)
                    else:
                        get_player_names(1)

                if quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
#-----------------------------------------------------------------------------------------------
#Function to get user input in text box
#-----------------------------------------------------------------------------------------------
def get_user_input(prompt, game_mode):
    font = pygame.font.Font("assets/fonts/turok.ttf", 60)
    option_font = pygame.font.Font("assets/fonts/turok.ttf", 40)

    input_box_width = 400
    input_box_height = 60
    input_box = pygame.Rect(SCREEN_WIDTH / 2 - input_box_width / 2, SCREEN_HEIGHT / 2 - input_box_height / 2, input_box_width, input_box_height)

    color_inactive = pygame.Color(0, 255, 0)
    color = color_inactive
    text = ''
    active = False
    clock = pygame.time.Clock()

    back_text = "Back"
    back_rect = pygame.Rect(SCREEN_WIDTH * 0.01, SCREEN_HEIGHT * 0.93, 300, 40)

    quit_text = "Quit"
    quit_rect = pygame.Rect(SCREEN_WIDTH * 0.94, SCREEN_HEIGHT * 0.93, 300, 40)

    while True:
        scaledbg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaledbg, (0, 0))

        mouse_pos = pygame.mouse.get_pos()
        if back_rect.collidepoint(mouse_pos):
            draw_text(back_text, option_font, YELLOW, SCREEN_WIDTH * 0.01, SCREEN_HEIGHT * 0.93)
        else:
            draw_text(back_text, option_font, WHITE, SCREEN_WIDTH * 0.01, SCREEN_HEIGHT * 0.93)

        if quit_rect.collidepoint(mouse_pos):
            draw_text(quit_text, option_font, RED, SCREEN_WIDTH * 0.94, SCREEN_HEIGHT * 0.93)
        else:
            draw_text(quit_text, option_font, WHITE, SCREEN_WIDTH * 0.94, SCREEN_HEIGHT * 0.93)

        prompt_surf = font.render(prompt, True, pygame.Color(BLUE))
        screen.blit(prompt_surf, (SCREEN_WIDTH / 2 - prompt_surf.get_width() / 2, SCREEN_HEIGHT / 2 - 100))

        txt_surface = font.render(text, True, color)
        txt_surface_width, txt_surface_height = txt_surface.get_size()

        pygame.draw.rect(screen, color, input_box, 2)
        screen.blit(txt_surface, (input_box.x + (input_box.width - txt_surface_width) / 2, input_box.y + (input_box.height - txt_surface_height) / 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return text  
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]  
                elif len(text) < 8:
                    text += event.unicode  

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(event.pos):
                    if game_mode == 0:
                        level_menu()  
                    else:
                        display_menu()

                if quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(30)
#-----------------------------------------------------------------------------------------------
#Level selection menu
#-----------------------------------------------------------------------------------------------
def level_menu():
    menu_font = pygame.font.Font("assets/fonts/turok.ttf", 70)
    option_font = pygame.font.Font("assets/fonts/turok.ttf", 50)
    back_font = pygame.font.Font("assets/fonts/turok.ttf", 40)

    menu_running = True

    easy_text = "Easy"
    medium_text = "Medium"
    difficult_text = "Difficult"
    back_text = "Back"
    quit_text = "Quit"

    easy_rect = pygame.Rect(SCREEN_WIDTH / 2 - option_font.size(easy_text)[0] / 2, SCREEN_HEIGHT / 2 - 70, 300, 40)
    medium_rect = pygame.Rect(SCREEN_WIDTH / 2 - option_font.size(medium_text)[0] / 2, SCREEN_HEIGHT / 2 - 10, 300, 40)
    difficult_rect = pygame.Rect(SCREEN_WIDTH / 2 - option_font.size(difficult_text)[0] / 2, SCREEN_HEIGHT / 2 + 50, 300, 40)

    back_rect = pygame.Rect(SCREEN_WIDTH * 0.01, SCREEN_HEIGHT * 0.93, 300, 40)
    quit_rect = pygame.Rect(SCREEN_WIDTH * 0.94, SCREEN_HEIGHT * 0.93, 300, 40)

    while menu_running:
        scaledbg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaledbg, (0, 0))

        draw_text("Select The Level", menu_font, BLUE, SCREEN_WIDTH / 2 - menu_font.size("Select The Level")[0] / 2, SCREEN_HEIGHT / 3 - 100)
        draw_text(easy_text, option_font, BLUE, SCREEN_WIDTH / 2 - option_font.size(easy_text)[0] / 2, SCREEN_HEIGHT / 2 - 70)
        draw_text(medium_text, option_font, BLUE, SCREEN_WIDTH / 2 - option_font.size(medium_text)[0] / 2, SCREEN_HEIGHT / 2 - 10)
        draw_text(difficult_text, option_font, BLUE, SCREEN_WIDTH / 2 - option_font.size(difficult_text)[0] / 2, SCREEN_HEIGHT / 2 + 50)
        draw_text(back_text, back_font, WHITE, SCREEN_WIDTH * 0.01, SCREEN_HEIGHT * 0.93)
        draw_text(quit_text, back_font, WHITE, SCREEN_WIDTH * 0.94, SCREEN_HEIGHT * 0.93)

        mouse_pos = pygame.mouse.get_pos()

        if easy_rect.collidepoint(mouse_pos):
            draw_text(easy_text, option_font, GREEN, SCREEN_WIDTH / 2 - option_font.size(easy_text)[0] / 2, SCREEN_HEIGHT / 2 - 70)
        if medium_rect.collidepoint(mouse_pos):
            draw_text(medium_text, option_font, GREEN, SCREEN_WIDTH / 2 - option_font.size(medium_text)[0] / 2, SCREEN_HEIGHT / 2 - 10)
        if difficult_rect.collidepoint(mouse_pos):
            draw_text(difficult_text, option_font, GREEN, SCREEN_WIDTH / 2 - option_font.size(difficult_text)[0] / 2, SCREEN_HEIGHT / 2 + 50)
        if back_rect.collidepoint(mouse_pos):  
            draw_text(back_text, back_font, YELLOW, SCREEN_WIDTH * 0.01, SCREEN_HEIGHT * 0.93)
        if quit_rect.collidepoint(mouse_pos):  
            draw_text(quit_text, back_font, RED, SCREEN_WIDTH * 0.94, SCREEN_HEIGHT * 0.93)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_rect.collidepoint(mouse_pos):
                    return 0  
                if medium_rect.collidepoint(mouse_pos):
                    return 1  
                if difficult_rect.collidepoint(mouse_pos):
                    return 2  
                if back_rect.collidepoint(mouse_pos):
                    display_menu()
                if quit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
#-----------------------------------------------------------------------------------------------
#User defined player name 
#-----------------------------------------------------------------------------------------------
def get_player_names(game_mode):
    if game_mode == 0:
        game_level = level_menu()
        player1_name = get_user_input("Enter Player Name:", game_mode)
        if player1_name == "":
            player1_name = "PLAYER"
        player2_name = "ALDRYN"
    else:
        player1_name = get_user_input("Enter Player 1 Name:", game_mode)
        if player1_name == "":
            player1_name = "PLAYER 1"
        player2_name = get_user_input("Enter Player 2 Name:", game_mode)
        if player2_name == "":
            player2_name = "PLAYER 2"
        game_level = None

    display_instructions(game_mode, player1_name, player2_name, game_level)
#-----------------------------------------------------------------------------------------------
#Game mode selection menu
#-----------------------------------------------------------------------------------------------
def display_menu():
    menu_font = pygame.font.Font("assets/fonts/turok.ttf", 70)
    option_font = pygame.font.Font("assets/fonts/turok.ttf", 50)
    back_font = pygame.font.Font("assets/fonts/turok.ttf", 40)

    menu_running = True

    single_player_text = "Single Player"
    two_player_text = "Two Player"
    back_text = "Back"
    quit_text = "Quit"

    single_player_rect = pygame.Rect(SCREEN_WIDTH / 2 - option_font.size(single_player_text)[0] / 2, SCREEN_HEIGHT / 2 - 50, 300, 40)
    two_player_rect = pygame.Rect(SCREEN_WIDTH / 2 - option_font.size(two_player_text)[0] / 2, SCREEN_HEIGHT / 2 + 10, 300, 40)

    back_rect = pygame.Rect(SCREEN_WIDTH * 0.01, SCREEN_HEIGHT * 0.93, 300, 40)
    quit_rect = pygame.Rect(SCREEN_WIDTH * 0.94, SCREEN_HEIGHT * 0.93, 300, 40)

    while menu_running:
        scaledbg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaledbg, (0, 0))

        draw_text("Select Game Mode", menu_font, BLUE, SCREEN_WIDTH / 2 - menu_font.size("Select Game Mode")[0] / 2, SCREEN_HEIGHT / 3 - 100)
        draw_text(single_player_text, option_font, BLUE, SCREEN_WIDTH / 2 - option_font.size(single_player_text)[0] / 2, SCREEN_HEIGHT / 2 - 50)
        draw_text(two_player_text, option_font, BLUE, SCREEN_WIDTH / 2 - option_font.size(two_player_text)[0] / 2, SCREEN_HEIGHT / 2 + 10)
        draw_text(back_text, back_font, WHITE, SCREEN_WIDTH * 0.01, SCREEN_HEIGHT * 0.93)
        draw_text(quit_text, back_font, WHITE, SCREEN_WIDTH * 0.94, SCREEN_HEIGHT * 0.93)

        mouse_pos = pygame.mouse.get_pos()

        if single_player_rect.collidepoint(mouse_pos):
            draw_text(single_player_text, option_font, GREEN, SCREEN_WIDTH / 2 - option_font.size(single_player_text)[0] / 2, SCREEN_HEIGHT / 2 - 50)
        if two_player_rect.collidepoint(mouse_pos):
            draw_text(two_player_text, option_font, GREEN, SCREEN_WIDTH / 2 - option_font.size(two_player_text)[0] / 2, SCREEN_HEIGHT / 2 + 10)
        if back_rect.collidepoint(mouse_pos):  
            draw_text(back_text, back_font, YELLOW, SCREEN_WIDTH * 0.01, SCREEN_HEIGHT * 0.93)
        if quit_rect.collidepoint(mouse_pos):  
            draw_text(quit_text, back_font, RED, SCREEN_WIDTH * 0.94, SCREEN_HEIGHT * 0.93)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if single_player_rect.collidepoint(mouse_pos):
                    get_player_names(0) 
                if two_player_rect.collidepoint(mouse_pos):
                    get_player_names(1)  
                if back_rect.collidepoint(mouse_pos):
                    main_menu()
                if quit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
#-----------------------------------------------------------------------------------------------
#Read and search for player data in text file
#-----------------------------------------------------------------------------------------------
def read_scores():
    with open('score.txt', 'r') as file:
        return file.readlines()

def search_achievements_by_name(player_name):
    lines = read_scores()
    matching_lines = []
    
    player_name_lower = player_name.lower()  
    
    for i in range(len(lines)):
        try:
            if "SINGLE PLAYER" in lines[i] or "TWO PLAYER" in lines[i]:
                mode_line = lines[i].strip()
                level_line = ""
                
                if "SINGLE PLAYER" in mode_line:
                    level_line = lines[i + 1].strip()
                    player1_line = lines[i + 2].strip()
                    player2_line = lines[i + 3].strip()
                    timestamp = lines[i + 4].strip()
                else:
                    player1_line = lines[i + 1].strip()
                    player2_line = lines[i + 2].strip()
                    timestamp = lines[i + 3].strip()

                if player_name_lower in player1_line.lower() or player_name_lower in player2_line.lower():
                    matching_lines.append(mode_line)
                    if level_line:
                        matching_lines.append(level_line)
                    matching_lines.append(player1_line)
                    matching_lines.append(player2_line)
                    matching_lines.append(timestamp)
                    matching_lines.append("-------------------------------")
                    
        except IndexError:
            continue  
            
    return matching_lines

def search_player_name(lines, player1_query, player2_query):
    player1_query = player1_query.lower()
    player2_query = player2_query.lower()
    
    return [line for line in lines if player1_query in line.lower() or player2_query in line.lower()]
#-----------------------------------------------------------------------------------------------
#Display text file contents in achievements menu
#-----------------------------------------------------------------------------------------------
def achievements():
    clock = pygame.time.Clock()
    font = pygame.font.Font("assets/fonts/turok.ttf", 30)
    small_font = pygame.font.Font("assets/fonts/turok.ttf", 25)

    back_image = pygame.image.load("assets/images/icons/quit.png").convert_alpha()
    back_rect = back_image.get_rect(center=(SCREEN_WIDTH * 0.95, SCREEN_HEIGHT * 0.93))

    lines = read_scores()

    player1_name = ""
    player2_name = ""

    active_input1 = False
    active_input2 = False

    input1_rect = pygame.Rect(SCREEN_WIDTH - 350, 150, 300, 30)
    input2_rect = pygame.Rect(SCREEN_WIDTH - 350, 210, 300, 30)

    game_mode = "both"
    mode_options = ["Single Player", "Two Player"]
    selected_mode = None

    mode_buttons = {
        "single": pygame.Rect(SCREEN_WIDTH - 450, 50, 180, 50),
        "two": pygame.Rect(SCREEN_WIDTH - 250, 50, 180, 50),
    }

    scroll_y = 0
    max_scroll = max(0, len(lines) * font.get_height() - SCREEN_HEIGHT)
    visible_ratio = SCREEN_HEIGHT / (len(lines) * font.get_height()) if len(lines) > 0 else 1
    scrollbar_height = max(int(SCREEN_HEIGHT * visible_ratio), 20)
    scrollbar_x = SCREEN_WIDTH - 20
    scrollbar_y = 0

    dragging = False
    mouse_y_offset = 0

    no_content_message = font.render("No records available.", True, BLACK)

    running = True
    while running:
        screen.fill(WHITE)

        screen.blit(back_image, back_rect.topleft)

        filtered_lines = []
        if game_mode == "single":


            for i, line in enumerate(lines):
                line = line.strip()
                if line.startswith("SINGLE PLAYER"):
                    level_line = lines[i + 1].strip()
                    player1_line = lines[i + 2].strip()  
                    player2_line = lines[i + 3].strip()
                    score1 = player1_line.split(":")[1].strip()  
                    score2 = player2_line.split(":")[1].strip()


                    if (player1_line.lower()).startswith(player1_name.lower()):
                        filtered_lines.append(line)  
                        filtered_lines.append(level_line)  
                        filtered_lines.append(player1_line)  
                        filtered_lines.append(player2_line)
                        filtered_lines.append(lines[i + 4].strip()) 
                        filtered_lines.append("-------------------------------")
        
        elif game_mode == "two":
            for i, line in enumerate(lines):
                line = line.strip()
                if line.startswith("TWO PLAYER"):
                    player1_line = lines[i + 1].strip() 
                    player2_line = lines[i + 2].strip()  
                    score1 = player1_line.split(":")[1].strip()  
                    score2 = player2_line.split(":")[1].strip()  

                    if (player1_line.lower()).startswith(player1_name.lower()) and (player2_line.lower()).startswith(player2_name.lower()):
                        filtered_lines.append(line)  
                        filtered_lines.append(player1_line)  
                        filtered_lines.append(player2_line)  
                        filtered_lines.append(lines[i + 3].strip())  
                        filtered_lines.append("-------------------------------")

        else:
            for i, line in enumerate(lines):
                line = line.strip()

                filtered_lines.append(line)

        rendered_lines = [font.render(line.strip(), True, BLACK) for line in filtered_lines]

        if len(rendered_lines) > 0:
            max_scroll = max(0, len(rendered_lines) * font.get_height() - SCREEN_HEIGHT)
            visible_ratio = SCREEN_HEIGHT / (len(rendered_lines) * font.get_height())
            scrollbar_height = max(int(SCREEN_HEIGHT * visible_ratio), 20)
        else:
            max_scroll = 0
            scrollbar_height = SCREEN_HEIGHT

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if game_mode != "single" and active_input2:
                    if event.key == pygame.K_BACKSPACE:
                        player2_name = player2_name[:-1]
                    elif len(player2_name) < 8:
                        player2_name += event.unicode

                    scroll_y = 0
                    scrollbar_y = 0

                if active_input1:
                    if event.key == pygame.K_BACKSPACE:
                        player1_name = player1_name[:-1]
                    elif len(player1_name) < 8:
                        player1_name += event.unicode

                    scroll_y = 0
                    scrollbar_y = 0

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(event.pos):
                    main_menu()
                    
                if input1_rect.collidepoint(event.pos):
                    active_input1 = True
                    active_input2 = False
                elif input2_rect.collidepoint(event.pos) and game_mode != "single":
                    active_input1 = False
                    active_input2 = True
                else:
                    active_input1 = False
                    active_input2 = False

                if mode_buttons["single"].collidepoint(event.pos):
                    if game_mode == "single":
                        game_mode = "both"
                        selected_mode = None
                        player1_name = ""
                        player2_name = ""  
                    else:
                        game_mode = "single"
                        selected_mode = "single"
                        player1_name = ""
                        player2_name = "ALDRYN"  
                        scroll_y = 0  
                        scrollbar_y = 0  

                elif mode_buttons["two"].collidepoint(event.pos):
                    if game_mode == "two":
                        game_mode = "both"
                        selected_mode = None
                        player1_name = ""
                        player2_name = ""
                    else:
                        game_mode = "two"
                        selected_mode = "two"
                        player1_name = ""
                        player2_name = ""  
                        scroll_y = 0  
                        scrollbar_y = 0  

                mouse_x, mouse_y = event.pos
                if scrollbar_x <= mouse_x <= scrollbar_x + 20 and scrollbar_y <= mouse_y <= scrollbar_y + scrollbar_height:
                    dragging = True
                    mouse_y_offset = mouse_y - scrollbar_y

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False

            elif event.type == pygame.MOUSEMOTION and dragging:
                mouse_x, mouse_y = event.pos
                scrollbar_y = max(0, min(mouse_y - mouse_y_offset, SCREEN_HEIGHT - scrollbar_height))
                scroll_y = int((scrollbar_y / (SCREEN_HEIGHT - scrollbar_height)) * max_scroll)

            elif event.type == pygame.MOUSEWHEEL:
                scroll_y = min(max(scroll_y - event.y * 50, 0), max_scroll)

        if max_scroll > 0:
            scrollbar_y = int((scroll_y / max_scroll) * (SCREEN_HEIGHT - scrollbar_height))

        if len(filtered_lines) == 0:
            screen.blit(no_content_message, (SCREEN_WIDTH // 2 - no_content_message.get_width() // 2, SCREEN_HEIGHT // 2))

        for mode, rect in mode_buttons.items():
            if selected_mode is None:
                color = (200, 200, 200)
            else:
                color = (0, 255, 0) if game_mode == mode else (200, 200, 200)
            pygame.draw.rect(screen, color, rect)
            mode_label = small_font.render(mode_options[list(mode_buttons.keys()).index(mode)], True, BLACK)
            screen.blit(mode_label, (rect.x + 20, rect.y + 10))

        if game_mode != "both":
            label1 = small_font.render("Player 1 Name:", True, BLACK)
            label2 = small_font.render("Player 2 Name:", True, BLACK)
            screen.blit(label1, (input1_rect.x, input1_rect.y - 25))
            if game_mode != "single":
                screen.blit(label2, (input2_rect.x, input2_rect.y - 25))

            pygame.draw.rect(screen, (200, 200, 200), input1_rect, 0 if active_input1 else 2)
            if game_mode != "single":
                pygame.draw.rect(screen, (200, 200, 200), input2_rect, 0 if active_input2 else 2)

            if player1_name == "":
                input1_text = small_font.render("Enter Player 1 Name", True, (150, 150, 150))
            else:
                input1_text = small_font.render(player1_name, True, BLACK)

            if game_mode == "single":
                input2_text = small_font.render("", True, (150, 150, 150))
            elif player2_name == "":
                input2_text = small_font.render("Enter Player 2 Name", True, (150, 150, 150))
            else:
                input2_text = small_font.render(player2_name, True, BLACK)

            screen.blit(input1_text, (input1_rect.x + 5, input1_rect.y + 5))
            if game_mode != "single":
                screen.blit(input2_text, (input2_rect.x + 5, input2_rect.y + 5))

        y_offset = -scroll_y
        for line in rendered_lines:
            screen.blit(line, (50, y_offset))
            y_offset += font.get_height()

        pygame.draw.rect(screen, (200, 200, 200), (scrollbar_x, 0, 20, SCREEN_HEIGHT))
        pygame.draw.rect(screen, (100, 100, 100), (scrollbar_x, scrollbar_y, 20, scrollbar_height))

        pygame.display.flip()
        clock.tick(60)
#-----------------------------------------------------------------------------------------------
#Main menu
#---------------------------------------------------------------------------------------------   
def main_menu():
    menu_font = pygame.font.Font("assets/fonts/turok.ttf", 100)
    option_font = pygame.font.Font("assets/fonts/turok.ttf", 50)

    menu_running = True

    play_text = option_font.render("Play", True, BLUE)
    achievements_text = option_font.render("Achievements", True, BLUE)
    quit_text = option_font.render("Quit", True, BLUE)

  
    play_x = SCREEN_WIDTH / 2 - play_text.get_width() / 2
    achievements_x = SCREEN_WIDTH / 2 - achievements_text.get_width() / 2
    quit_x = SCREEN_WIDTH / 2 - quit_text.get_width() / 2


    play_rect = pygame.Rect(play_x, SCREEN_HEIGHT / 2 - 50, play_text.get_width(), play_text.get_height())
    achievements_rect = pygame.Rect(achievements_x, SCREEN_HEIGHT / 2 + 10, achievements_text.get_width(), achievements_text.get_height())
    quit_rect = pygame.Rect(quit_x, SCREEN_HEIGHT / 2 + 70, quit_text.get_width(), quit_text.get_height())

    while menu_running:
        scaledbg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaledbg, (0, 0))

        mouse_pos = pygame.mouse.get_pos()
        
        draw_text("RIVAL REIGN", menu_font, BLUE, SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 3 - 100)
        draw_text("Play", option_font, BLUE, play_x, SCREEN_HEIGHT / 2 - 50)
        draw_text("Achievements", option_font, BLUE, achievements_x, SCREEN_HEIGHT / 2 + 10)
        draw_text("Quit", option_font, BLUE, quit_x, SCREEN_HEIGHT / 2 + 70)

        if play_rect.collidepoint(mouse_pos):
            draw_text("Play", option_font, GREEN, play_x, SCREEN_HEIGHT / 2 - 50)
        if achievements_rect.collidepoint(mouse_pos):
            draw_text("Achievements", option_font, GREEN, achievements_x, SCREEN_HEIGHT / 2 + 10)
        if quit_rect.collidepoint(mouse_pos):
            draw_text("Quit", option_font, RED, quit_x, SCREEN_HEIGHT / 2 + 70)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
           
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(mouse_pos):
                    display_menu()  
                if achievements_rect.collidepoint(mouse_pos):
                    achievements()
                if quit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
#-----------------------------------------------------------------------------------------------
#Display game logo
#-----------------------------------------------------------------------------------------------
def display_logo(duration=5000):
    logo_rect = logo_image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    start_time = pygame.time.get_ticks()

    while True:
        screen.fill((0, 0, 0))
        screen.blit(logo_image, logo_rect)

        pygame.display.update()

        current_time = pygame.time.get_ticks()
        if current_time - start_time >= duration:
            break
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

logo_image = pygame.image.load("assets/images/icons/Rival logo.png").convert_alpha()  
bg = pygame.image.load("assets/images/background/bg.jpg").convert_alpha()
display_logo()

while True:
    main_menu()
