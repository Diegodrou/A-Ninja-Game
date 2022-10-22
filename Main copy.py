import pygame , sys , time
from pygame.locals import *
from levelloader import World
from settings import*
from player import Player
from buttons import *
from Tile import*

#Initialize Pygame and create window
pygame.init()
pygame.display.set_caption('platformer')

#Creation of instances
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
display = pygame.Surface(DISPLAY_SIZE)
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 18)
player=Player(50,0)
player_speed = player.speed
#Creation of button instances for menu
resume_b = Button(10, 10, resume_b_img, 0.50)
options_b = Button(10, 60, options_b_img,0.50)
quit_b = Button(10, 110, quit_b_img, 0.50)
level_1_b = Button(250, 10, lvl_1_b_img, 0.50)
back_b = Button(10, 360, back_b_img, 0.50)

#Creation of button instances for paused menu
quit_b_p = Button(270, 120, quit_b_img, 0.50)

#Sprite group creation
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
#functions for the game

def debug_stats():#Shows stats useful for debugging
    #Avg fps
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps,1,pygame.Color('white'))
    #player.rect.x(left corner up)
    player_pos_x = 'x =' + str(player.rect.x)
    player_pos_x_text = font.render(player_pos_x,1,pygame.Color('white'))
    #player.rect.y(left corner up)
    player_pos_y = 'y =' + str(player.rect.y)
    player_pos_y_text = font.render(player_pos_y,1,pygame.Color('white'))
    #player's direction.y (vertical direction)
    player_y_direction ='vector_y =' + str(player.direction.y)
    player_y_direction_text = font.render(player_y_direction,1,pygame.Color('white'))
    #player's direction.x(horizontal direction)
    player_x_direction = 'vector_x ='+ str(player.direction.x * player.speed)
    player_x_direction_text = font.render(player_x_direction,1,pygame.Color('white'))
    #pos of the center of the player
    player_center_x = 'vector_center_x ='+ str(player.rect.centerx)
    player_center_x_text = font.render(player_x_direction,1,pygame.Color('white'))

    window.blit(fps_text,(10,0))
    window.blit(player_pos_x_text,(10,20))
    window.blit(player_pos_y_text,(70,20))
    window.blit(player_x_direction_text,(10,40))
    window.blit(player_y_direction_text,(10,60))
    window.blit(player_center_x_text,(10,80))


def level_selection_menu():
    #Menu variables
    lvl_selector = True
    anim_index = 0
    BACKGROUND_ANIM = menu_bimages
    print(len(BACKGROUND_ANIM))
    MAIN_MENU_ANIM_COOLDOWN = 150
    update_time_m =pygame.time.get_ticks()
    #Menu_Loop
    while lvl_selector:
        
        #Pygame input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        #All Draws, and button instances
        display.blit(pygame.transform.scale(BACKGROUND_ANIM[anim_index],DISPLAY_SIZE),(0,0))
        window.blit(pygame.transform.scale(display, WINDOW_SIZE), (0,0))
        if level_1_b.draw(window):
            lvl_selector = False
            Game(lvls[0])

        if back_b.draw(window):
            lvl_selector = False
            main_menu()

        pygame.display.update()
        if pygame.time.get_ticks() - update_time_m > MAIN_MENU_ANIM_COOLDOWN:
            update_time_m = pygame.time.get_ticks()
            if anim_index >= len(BACKGROUND_ANIM)-1 :#24 frames in the animation
                anim_index = 0
            else:
                anim_index += 1

def main_menu():
    #Menu variables
    game_menu = True
    anim_index = 0
    BACKGROUND_ANIM = menu_bimages
    print(len(BACKGROUND_ANIM))
    MAIN_MENU_ANIM_COOLDOWN = 150
    update_time_m =pygame.time.get_ticks()
    #Menu_Loop
    while game_menu:
        
        #Pygame input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        #All Draws, and button instances
        display.blit(pygame.transform.scale(BACKGROUND_ANIM[anim_index],DISPLAY_SIZE),(0,0))
        window.blit(pygame.transform.scale(display, WINDOW_SIZE), (0,0))
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
            if anim_index >= len(BACKGROUND_ANIM)-1 :#24 frames in the animation
                anim_index = 0
            else:
                anim_index += 1

def Game(lvl):
    #Game Variables
    game_pause = False
    fps_toggle = False
    game_run = True 
    SCROLL_TRESH = 550
    bg_scroll = 0
    #game instances
    world=World(lvl)

    #Game functions
    def scroll_hndler():#Handles world scrolling
        if player.rect.centerx > 210 and player.direction.x > 0:
            world.scroll_x(-player_speed)
            player.speed = 0
        elif player.rect.centerx < 50 and player.direction.x < 0:
            world.scroll_x(player_speed)
            player.speed = 0
        else:
            world.scroll_x(0)
            player.speed = 2
    
    #Game Loop
    while game_run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSLASH:
                    fps_toggle = not fps_toggle
                if event.key == pygame.K_ESCAPE:
                    if game_pause:
                        game_pause = False
                    else:
                        game_pause = True

                if event.key == pygame.K_RIGHT:
                    player.moving_right = True
                if event.key == pygame.K_LEFT:
                    player.moving_left = True
                if event.key in [K_SPACE,K_UP] :
                    if player.air_timer < 6 :
                        player.jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    player.moving_right = False
                if event.key == pygame.K_LEFT:
                    player.moving_left = False
            
        #all_sprite updates
        scroll_hndler()
        tile_rects = world.run()
        player.update(tile_rects)
        player.update_anim()

        # - all draws -

        display.blit(pygame.transform.scale(city_background,DISPLAY_SIZE),(0,0))
        world.draw(display)

        for item in all_sprites:
            item.draw(display)


        window.blit(pygame.transform.scale(display, WINDOW_SIZE), (0,0))
        
        if fps_toggle:
            debug_stats()


        #check if game is paused
        if game_pause :
            pygame.draw.rect(window, (255,120,219),pygame.Rect(150, 30, 300 , 300), 0, 3)
            #paused menu buttons

            if quit_b_p.draw(window) :
                main_menu()

        pygame.display.update()
    
    pygame.quit()
    exit()


main_menu()
pygame.quit()
exit()