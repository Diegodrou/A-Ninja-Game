import pygame
import sys
import time
from pygame.locals import *
from levelloader import World
from settings import *
from player import Player
from buttons import *
from Enemy import Enemy

# Initialize Pygame and create window
pygame.init()
pygame.display.set_caption('A ninja game')

# Creation of instances
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
display = pygame.Surface(DISPLAY_SIZE)
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 18)
font2 = pygame.font.SysFont('Arial', 60)
# Creation of button instances for menu
resume_b = Button(10, 10, resume_b_img, 0.50)
options_b = Button(10, 60, options_b_img, 0.50)
quit_b = Button(10, 110, quit_b_img, 0.50)
level_1_b = Button(250, 10, lvl_1_b_img, 0.50)
back_b = Button(10, 360, back_b_img, 0.50)

# Creation of button instances for paused menu
quit_b_p = Button(270, 120, quit_b_img, 0.50)
# Creation of button instances for dead menu
resume_b_d = Button(150, 200, resume_b_img, 0.50)
quit_b_d = Button(200, 240, quit_b_img, 0.50)

# functions for the game


def level_selection_menu():
    # Menu variables
    lvl_selector = True
    anim_index = 0
    BACKGROUND_ANIM = menu_bimages
    MAIN_MENU_ANIM_COOLDOWN = 150
    update_time_m = pygame.time.get_ticks()
    # Menu_Loop
    while lvl_selector:

        # Pygame input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # All Draws, and button instances
        display.blit(pygame.transform.scale(
            BACKGROUND_ANIM[anim_index], DISPLAY_SIZE), (0, 0))
        window.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
        if level_1_b.draw(window):
            lvl_selector = False
            Game(lvls[0])

        if back_b.draw(window):
            lvl_selector = False
            main_menu()

        pygame.display.update()
        if pygame.time.get_ticks() - update_time_m > MAIN_MENU_ANIM_COOLDOWN:
            update_time_m = pygame.time.get_ticks()
            if anim_index >= len(BACKGROUND_ANIM)-1:  # 24 frames in the animation
                anim_index = 0
            else:
                anim_index += 1


def main_menu():
    # Menu variables
    game_menu = True
    anim_index = 0
    BACKGROUND_ANIM = menu_bimages
    MAIN_MENU_ANIM_COOLDOWN = 150
    update_time_m = pygame.time.get_ticks()
    # Menu_Loop
    while game_menu:

        # Pygame input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # All Draws, and button instances
        display.blit(pygame.transform.scale(
            BACKGROUND_ANIM[anim_index], DISPLAY_SIZE), (0, 0))
        window.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
        if resume_b.draw(window):
            level_selection_menu()
        if options_b.draw(window):
            pass
        if quit_b.draw(window):
            pygame.quit
            exit()
        pygame.display.update()
        if pygame.time.get_ticks() - update_time_m > MAIN_MENU_ANIM_COOLDOWN:
            update_time_m = pygame.time.get_ticks()
            if anim_index >= len(BACKGROUND_ANIM)-1:  # 24 frames in the animation
                anim_index = 0
            else:
                anim_index += 1


def Game(lvl):
    # Game Variables & Objetcs
    game_pause = False
    fps_toggle = False
    game_run = True
    DEAD_MESSAGE = 'Sry Bruh U Dead'
    DEAD_MESSAGE_TEXT = font2.render(DEAD_MESSAGE, 1, pygame.Color('Red'))
    # game instances
    world = World(lvl)
    player = Player(world.spawnpoint(lvl))
    # enemy = Enemy(world.enemy_spawn(lvl))
    player_speed = player.speed

    # Puts enemy objects inside a sprite group object
    def load_enemies(enemy_spawns):
        enemy_sprites = pygame.sprite.Group()
        for spawn in enemy_spawns:
            enemy_sprites.add(Enemy(spawn))
        return enemy_sprites

    # Gets rects of oll the enemies of the current level
    def get_enemy_rects(enemy_sprites): 
        enemy_rects = []
        for enemy in enemy_sprites:
            enemy_rects.append(enemy.rect)
        return enemy_rects

    # Sprite group creation
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    enemy_sprites = load_enemies(world.enemy_spawn(lvl))
    bullet_group = pygame.sprite.Group()

    # Game functions
    def debug_stats(color):  # Shows stats useful for debugging
        # Avg fps
        fps = str(int(clock.get_fps()))
        fps_text = font.render(fps, 1, pygame.Color(color))

        # player.rect.x(left corner up)
        player_pos_x = 'x =' + str(player.rect.x)
        player_pos_x_text = font.render(player_pos_x, 1, pygame.Color(color))

        # player.rect.y(left corner up)
        player_pos_y = 'y =' + str(player.rect.y)
        player_pos_y_text = font.render(player_pos_y, 1, pygame.Color(color))

        # player's direction.y (vertical direction)
        player_y_direction = 'vector_y =' + str(player.direction.y)
        player_y_direction_text = font.render(
            player_y_direction, 1, pygame.Color(color))

        # player's direction.x(horizontal direction)
        player_x_direction = 'vector_x =' + \
            str(player.direction.x * player.speed)
        player_x_direction_text = font.render(
            player_x_direction, 1, pygame.Color(color))

        # pos of the center of the player
        player_center = 'center =' + str(player.rect.center)
        player_center_x_text = font.render(
            player_center, 1, pygame.Color(color))

        # air timer values
        player_air_timer = "air_timer = " + str(player.air_timer)
        player_air_timer_text = font.render(
            player_air_timer, 1, pygame.Color(color))

        # on_ground value
        on_ground = "on_ground = " + str(player.on_ground)
        on_ground_text = font.render(on_ground, 1, pygame.Color(color))

        window.blit(fps_text, (10, 0))
        window.blit(player_pos_x_text, (10, 20))
        window.blit(player_pos_y_text, (70, 20))
        window.blit(player_x_direction_text, (10, 40))
        window.blit(player_y_direction_text, (10, 60))
        window.blit(player_center_x_text, (10, 80))
        window.blit(player_air_timer_text, (10, 100))
        window.blit(on_ground_text, (10, 120))

    def update_bullet_pos(tiles, player_rect, scroll):
        for item in bullet_group:
            item.update(tiles, player_rect, scroll)

    # Game Loop
    while game_run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSLASH:
                    fps_toggle = not fps_toggle
                    player.t_rect = not player.t_rect
                    for enemy in enemy_sprites:
                        enemy.debug = not enemy.debug

                if event.key == pygame.K_ESCAPE:
                    if game_pause:
                        game_pause = False
                    else:
                        game_pause = True

                if event.key == pygame.K_f:
                    player.attack = True

                if event.key == pygame.K_RIGHT:
                    player.moving_right = True
                if event.key == pygame.K_LEFT:
                    player.moving_left = True
                if event.key in [K_SPACE, K_UP]:
                    if player.air_timer < 7:
                        # player.is_jumping = True
                        player.jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    player.moving_right = False
                if event.key == pygame.K_LEFT:
                    player.moving_left = False
                # if event.key in [K_SPACE, K_UP]:
                #    player.air_timer = 0

        # all_sprite updates
        tile_rects = world.run()
        enemy_rects = get_enemy_rects(enemy_sprites)
        screen_scroll,attack_rect = player.movementANDcollisions(tile_rects, enemy_rects)
        player.update()
        for enemy in enemy_sprites:
            enemy.AI(player.rect, player.dead, tile_rects, screen_scroll)
            if enemy.Shoot:
                Bullet = enemy.shoot()
                bullet_group.add(Bullet)
            enemy.update(attack_rect, player.hit_enemy)
        player.hit_enemy = False
        update_bullet_pos(tile_rects, player.rect, screen_scroll)
        # enemy.update(player)

        # - all draws -

        display.blit(pygame.transform.scale(
            city_background, DISPLAY_SIZE), (0, 0))
        world.draw(display, screen_scroll)

        # for item in all_sprites:
        #     item.draw(display)
        player.draw(display)

        for bullet in bullet_group:
            bullet.draw(display)

        for item in enemy_sprites:
            item.draw(display)

        window.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))

        if fps_toggle:
            debug_stats("Red")

        # check if game is paused
        if game_pause:
            pygame.draw.rect(window, (255, 120, 219),
                             pygame.Rect(150, 30, 300, 300), 0, 3)
            # paused menu buttons

            if quit_b_p.draw(window):
                main_menu()
        if player.dead:
            pygame.draw.rect(window, (255, 120, 219),
                             pygame.Rect(0, 0, 600, 500), 0, 3)
            window.blit(DEAD_MESSAGE_TEXT, (80, 60))
            if resume_b_d.draw(window):
                Game(lvl)
            if quit_b_d.draw(window):
                main_menu()

        pygame.display.update()

    pygame.quit()
    exit()


main_menu()
pygame.quit()
exit()
