

def Game(lvl):
    # Game Variables & Objetcs
    game_pause = False
    fps_toggle = False
    game_run = True
    DEAD_MESSAGE = 'Sry Bruh U Dead'
    DEAD_MESSAGE_TEXT = font2.render(DEAD_MESSAGE, 1, pygame.Color('Red'))
    Scroll = 0
    # game instances
    world = World(lvl)
    player = Player(world.spawnpoint(lvl))

    # Puts enemy objects inside a sprite group object
    # @param enemy_spawns a list that holds the spawn coordinates of all enemies in the level
    # @returns enemy_sprites a Group that contains all enemy sprites
    def load_enemies(enemy_spawns):
        enemy_sprites = pygame.sprite.Group()
        for spawn in enemy_spawns:
            enemy_sprites.add(Enemy(spawn))
        return enemy_sprites

    # Gets rects of oll the enemies of the current level
    # @param enemy_sprites a Group thaht contains all enemy sprites
    # @return enemy_rects a list containing all the rect of the enemies that are in the enemy_sprites Group
    def get_enemy_rects(enemy_sprites): 
        enemy_rects = []
        for enemy in enemy_sprites:
            enemy_rects.append(enemy.rect)
        return enemy_rects
   
   # Increments Scroll variable every frame depending on the player's input(side effect)
   # @param Scroll a float variable
   # @return Scroll variable with a bigger or smaller number depending on the player's input
    def scroll_input(Scroll,side_collision):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and Scroll > 0 and player.rect.centerx < 52 and not (side_collision):
            Scroll -= 1.3
        if key[pygame.K_RIGHT] and Scroll <3000 and player.rect.centerx > 208 and (not side_collision):
            Scroll += 1.3

        return Scroll

    # Function draws background images with parallax effect applied(thx to the scroll_var) onto the display Surface(side effect)
    # @param layers a list with the layers that make the background
    # @param scroll_var whith the amount of pixels that the images have to move
    # @return None 
    def draw_background(layers:list[pygame.Surface],scroll_var:float):
        speed = 2
        SUN_SPEED = 0.02
        display.blit(pygame.transform.scale(SKY,DISPLAY_SIZE),(0,0))
        display.blit(pygame.transform.scale(sunCloud,DISPLAY_SIZE),(0 - Scroll*SUN_SPEED,0))
        for i in layers:
            for x in range(23):
                i = pygame.transform.scale(i,DISPLAY_SIZE)
                display.blit(i,((x * DISPLAY_SIZE[0]) - scroll_var * speed ,0))
                speed += 0.01



    # Sprite group creation
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    enemy_sprites = load_enemies(world.enemy_spawn(lvl))
    bullet_group = pygame.sprite.Group()

    # Game functions

    # Shows stats useful for debugging(side effects)
    # @param color a string/or a Tuple containing 3 int values representing a color ex:"WHITE" or (255,255,255)
    # @return None
    def debug_stats(color):
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

    # Updates bullets positions and checks for collisions(side effects)
    # @param tiles a list that contains all of the rects of the collidable tiles on the level
    # @param player_rect the rect of the player
    # @param scroll a flaot varibale
    # @return None  
    def update_bullet(tiles:list[pygame.Rect], player_rect:pygame.Rect, scroll:float):
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
                        player.jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    player.moving_right = False
                if event.key == pygame.K_LEFT:
                    player.moving_left = False

        # - all sprite updates - 

        tile_rects = world.run()
        enemy_rects = get_enemy_rects(enemy_sprites)
        screen_scroll, attack_rect = player.movementANDcollisions(tile_rects, enemy_rects)
        Scroll = scroll_input(Scroll,player.side_collision)
        player.update()

        for enemy in enemy_sprites:
            enemy.AI(player.rect, player.dead, tile_rects, screen_scroll)
            if enemy.Shoot:
                Bullet = enemy.shoot()
                bullet_group.add(Bullet)
            enemy.update(attack_rect, player.hit_enemy)
        player.hit_enemy = False
        
        update_bullet(tile_rects, player.rect, screen_scroll)

        # - all draws -

        draw_background(bg_layers,Scroll)

        world.draw(display, screen_scroll)

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