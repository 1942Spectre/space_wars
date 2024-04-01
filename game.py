import pygame
import sys
import random
import math
class ResourceManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}

    def load_image(self, image_file):
        if image_file not in self.images:
            self.images[image_file] = pygame.image.load(image_file).convert_alpha()
        return self.images[image_file]
    
    def load_sound(self, sound_file):
        if sound_file not in self.sounds:
            self.sounds[sound_file] = pygame.mixer.Sound(Game.PROJECTILE_SOUND_FILE)
        return self.sounds[sound_file]
    


# Now you can use 'image' wherever you need it in your game

class Object(pygame.sprite.Sprite):
    def __init__(self,
                 posx,
                 posy,
                 _width,
                 _height
                ):
        super().__init__()
        self._width = _width
        self._height = _height

        if self._image_file is None:
            self.image = pygame.Surface((_width, _height)) 
            self.image.fill(self._color) 

        else:
            self.image = game.resource_manager.load_image(self._image_file)
            self.image = pygame.transform.scale(self.image,(self._width,self._height))
        self.rect = self.image.get_rect(center =(posx,posy)) 

    def move(self,game,direction):
        if direction == "l":
            self.rect.x -= self.speed_x
        
        elif direction == "r":
            self.rect.x += self.speed_x

        elif direction == "u":
            self.rect.y -= self.speed_y

        elif direction == "d":
            self.rect.y += self.speed_y

    def draw_bounding_box(self, screen):
            pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)  # Draw a red rectangle around the bounding box

    def remove(self):
        self.kill()
    
    def draw(self,screen):
        screen.blit(self.image, self.rect)


class Boost(Object):
    SPEED = 5
    WIDTH = 50
    HEIGHT = 50

    def __init__(self,posx,posy):
        super().__init__(
            posx,
            posy,
            50,
            50,
        )
        self.speed_y = Boost.SPEED
        self.speed_x = 0
        self.rect.centerx = posx
        self.rect.top = posy
    
    def move(self,game):
        super().move(game,"d")

    def update(self,game):
        self.move(game)
        if pygame.sprite.collide_rect(game.player,self):
            self.consume(game)
        elif self.rect.top  > game.HEIGHT  :
            self.remove()

class Projectile(Object):
    SPEED = 10
    WIDTH = 5
    HEIGHT = 30

    def __init__(self,owner,gun_pos): 
         
        self.owner = owner
        self.speed_y = Projectile.SPEED

        if owner.is_enemy:
            self._color = (255,0,0)
        else:
            damage_ratio = min(max(owner.damage / 5, 0), 1)
            self._color = self.interpolate_color((0, 100, 0),(144, 238, 144),damage_ratio)
        self._image_file = None

        super().__init__(
            owner.rect.centerx,
            owner.rect.centery,
            Projectile.WIDTH,
            Projectile.HEIGHT
        )

        if gun_pos == "center":
            self.rect.centerx = owner.rect.centerx

        elif gun_pos == "left":
            self.rect.centerx = owner.rect.left

        elif gun_pos == "right": 
            self.rect.centerx = owner.rect.right

        if owner.is_enemy:
            self.rect.top = owner.rect.bottom
        else:
            self.rect.bottom = owner.rect.top

    def interpolate_color(self, color1, color2, ratio):
        # Interpolate between two colors based on the ratio
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        return r, g, b
                          
    
    def move(self):
        if self.owner.is_enemy:
            super().move(game,"d")
        else:
            super().move(game,"u")

    def update(self):
        self.move()
        if self.rect.bottom < 0 or self.rect.top > Game.HEIGHT:  # Check if projectile goes out of screen
            self.remove()




class Ship(Object):
    SPEED = 5

    def __init__(self,
                 posx,
                 posy,
                 _width,
                 _height,
                 is_enemy):
        
        width = _width
        height = _height
        self.is_enemy = is_enemy
        self.speed_x = Ship.SPEED
        super().__init__(
                         posx,
                         posy,
                         width,
                         height)
        self.rect.centerx = posx
        self.rect.top = posy

        self.shield = None
        
    def fire(self,game,gun_pos = "center"):
        return Projectile(self,gun_pos)
    
    def check_collision(self,game):
        projectile_collisions = pygame.sprite.spritecollide(self,game.projectiles,dokill = False)
        for projectile in projectile_collisions:
            if self != game.player:
                if not projectile.owner.is_enemy:
                    self.lives -= 1 * game.player.damage
                    projectile.remove()
                    if self.lives <= 0:
                        self.remove()
                    game.score += 50
            else:
                self.lives -= 5
                projectile.remove()
                if self.lives <= 0:
                    self.remove()
                game.score -= 100

        ## Ship collisions will be handled in the game object.

    def update_opacity(self):
        # Calculate and set opacity based on current lives
        opacity_step = 255 // self.max_lives
        alpha_value = max(0, 255 - opacity_step * (self.max_lives - self.lives)) 
        self.image.set_alpha(alpha_value)

class EnemyShip(Ship):
    def __init__(self,
                 posx ,
                 posy,
                 width,
                 height):
         
        self.is_moving_left = random.random() > 0.5
        self.lives = self.max_lives

        super().__init__(posx,posy,width,height,True)
    
    def move(self,game):
        if self.is_moving_left:
            super().move(game,"l")
        else:
            super().move(game,"r")

    
    def change_direction(self):
        self.is_moving_left = not self.is_moving_left
    
    def should_change_direction(self):
        return random.random() < self.cd_probability
    
    def should_triple_fire(self):
        if self.should_fire:
            return random.random () < self.triple_fire_proba
        
    def should_double_fire(self):
        if self.should_fire:
            return random.random () < self.double_fire_proba

    def should_fire(self):
        return random.random() < self.fire_probability
    
    def stay_in_screen(self):
        if self.rect.left <= 0:
            self.rect.left = 0
            self.is_moving_left = False
        elif self.rect.right >= Game.WIDTH:
            self.rect.right = Game.WIDTH
            self.is_moving_left = True
     
    def update(self,game): 
        self.move(game)
        self.stay_in_screen()
        self.check_collision(game) 

        if self.should_fire():
            if self.should_triple_fire():
                Factory.spawn_projectile(game,self,3)
            elif self.should_double_fire():
                Factory.spawn_projectile(game,self,2)
            else:
                Factory.spawn_projectile(game,self,1)

        if self.should_change_direction():
            self.change_direction()
        self.update_opacity()

        def remove(self,game):
            game.player.score += self.max_lives
            super().remove()

    

    
class PlayerShip(Ship):
    IMAGE_FILE = "player_ship.png"
    MAX_LIVES = 50
    HEIGHT = 80
    WIDTH = 60


    def __init__(self):
        self._image_file = PlayerShip.IMAGE_FILE 
        self.max_lives = PlayerShip.MAX_LIVES
        self.lives = self.max_lives

        posx = Game.WIDTH // 2
        posy = Game.HEIGHT - 100

        self.shield = None
        self.double_firing = False
        self.damage = 1

        super().__init__(
                         posx,
                         posy,
                         PlayerShip.WIDTH,
                         PlayerShip.HEIGHT,
                         False)

    def draw(self,screen):
        if self.shield != None:
            self.shield.draw(screen)
        super().draw(screen)



class TieFighter(EnemyShip):
    MAX_LIVES = 5
    HEIGHT = 120
    WIDTH = 90
    FIRE_PROBA = 0.05
    CD_PROBA = 0.0001
    IMAGE_FILE = "enemy_tie_fighter.png"
    DOUBLE_GUN_FIRE_PROBA = 0
    TRIPLE_GUN_FIRE_PROBA = 0
    
    
    def __init__(self,game,posx,posy):
        self._image_file = TieFighter.IMAGE_FILE
        self.max_lives = TieFighter.MAX_LIVES 

        super().__init__(posx,
                         posy,
                         TieFighter.WIDTH,
                         TieFighter.HEIGHT)
        
        self.triple_fire_proba = TieFighter.TRIPLE_GUN_FIRE_PROBA
        self.double_fire_proba = TieFighter.DOUBLE_GUN_FIRE_PROBA
        self.cd_probability = TieFighter.CD_PROBA
        self.fire_probability = TieFighter.FIRE_PROBA
        self.max_lives = TieFighter.MAX_LIVES 
    

class StarDestroyer(EnemyShip):
    MAX_LIVES = 20
    HEIGHT = 120
    WIDTH = 360
    FIRE_PROBA = 0.1
    CD_PROBA = 0.0001
    IMAGE_FILE = "star_destroyer.png"
    DOUBLE_GUN_FIRE_PROBA = 0.2
    TRIPLE_GUN_FIRE_PROBA = 0.1

    def __init__(self,game,posx,posy):
        self._image_file = StarDestroyer.IMAGE_FILE
        self.max_lives = StarDestroyer.MAX_LIVES 

        super().__init__(posx,
                         posy,
                         StarDestroyer.WIDTH, 
                         StarDestroyer.HEIGHT)
        
        

        self.triple_fire_proba = StarDestroyer.TRIPLE_GUN_FIRE_PROBA
        self.double_fire_proba = StarDestroyer.DOUBLE_GUN_FIRE_PROBA
        self.cd_probability = TieFighter.CD_PROBA
        self.fire_probability = TieFighter.FIRE_PROBA



class HP_Boost(Boost):
    def __init__(self,posx,posy):
        self._image_file = "heart.png"
        super().__init__(posx,posy)

    def consume(self,game):
        print("Health Consumed")
        game.player.lives = min(game.player.lives + 50,game.player.max_lives)
        self.remove()

class Shield(Boost):
    def __init__(self,posx,posy):
        self._image_file = "shield.png"
        super().__init__(posx,posy)
        self.hitpoints = 5
        self.activated = False

    def activate(self, game):
        self.activated = True
        self.image = pygame.Surface((160, 160), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=game.player.rect.center)
        self.rect.center = game.player.rect.center  
        self.speed_y = 0
        self.speed_x = 0

    def consume(self,game):
        print("Shield Consumed")
        self.activate(game)
        game.player.shield = self

    def update(self,game):
        if not self.activated:
            super().update(game)
        else:
            self.rect.center = game.player.rect.center
            self.check_collision(game)

    def draw(self, screen):
        if self.activated:
            circle_pos = self.rect.center
            pygame.draw.circle(screen, (0, 255, 255), circle_pos, 80, 2)  # Draw a cyan circle

        else:
            super().draw(screen)
    def check_collision(self,game):
        if self.activated:
            projectile_collisions = pygame.sprite.spritecollide(self,game.projectiles,dokill = False)
            for projectile in projectile_collisions:
                if projectile.owner != game.player:
                    self.hitpoints -= 1 
                    projectile.remove()
                    if self.hitpoints <= 0:
                        self.remove()
                        game.player.shield = None
                    game.score += 50

class Damage_Boost(Boost):
    def __init__(self,posx,posy):
        self._image_file = "fist_up.png"
        super().__init__(posx,posy)

    def consume(self,game):
        print("damage boost consumed")
        game.player.damage += 1 
        self.remove()
 
class Double_Guns(Boost):  
    
    def __init__(self,posx,posy):
        self._image_file = "double.png"
        super().__init__(posx,posy)

    def consume(self,game):
        game.player.double_firing = True
        if "Double_Guns" in Factory.AVAILABLE_BOOSTS:
            Factory.AVAILABLE_BOOSTS.remove("Double_Guns")
        self.remove()






class Factory:  
    AVAILABLE_BOOSTS = ["HP",
                        "Shield",
                        "Damage_Boost",
                        "Double_Guns"] 
    @staticmethod
    def spawn_enemy(game):
        will_spawn_star_destroyer = random.random() <= game.difficulty.STAR_DESTROYER_SPAWN_PROBA
        if  not (game.difficulty.MAX_CURRENT_STAR_DESTROYERS > len(game.star_destroyers)):
            will_spawn_star_destroyer = False
        while True:
            posx = random.choice(range(0, Game.N_COLS)) * Game.CELL_WIDTH
            posy = random.choice(range(1, 5)) * Game.CELL_HEIGHT 
            
            
            if not will_spawn_star_destroyer:
                enemy = TieFighter(game, posx, posy)
            else:
                enemy = StarDestroyer(game, posx, posy)
            
            # Check for collisions with other enemies
            collision = pygame.sprite.spritecollideany(enemy, game.enemies)
            
            # If no collision, add the enemy to sprite groups and break the loop
            if not collision:
                game.enemies.add(enemy)
                game.all_sprites.add(enemy)
                if will_spawn_star_destroyer:
                    game.star_destroyers.add(enemy)
                break

    
    @staticmethod
    def spawn_projectile(game,owner,style):
        if style == 1:
            projectile = owner.fire(game,"center")
            game.projectiles.add(projectile)
            game.all_sprites.add(projectile)

        elif style == 2:
            projectile = owner.fire(game,"right")
            game.projectiles.add(projectile)
            game.all_sprites.add(projectile)
            
            projectile = owner.fire(game,"left")
            game.projectiles.add(projectile)
            game.all_sprites.add(projectile)

        elif style == 3:
            projectile = owner.fire(game,"center")
            game.projectiles.add(projectile)
            game.all_sprites.add(projectile)
            
            projectile = owner.fire(game,"right")
            game.projectiles.add(projectile)
            game.all_sprites.add(projectile)

            projectile = owner.fire(game,"left")
            game.projectiles.add(projectile)
            game.all_sprites.add(projectile)

    @staticmethod
    def spawn_boost(game):
        posx = random.choice(range(0, Game.N_COLS)) * Game.CELL_WIDTH
        posy = random.choice(range(1, 3)) * Game.CELL_HEIGHT
        selected_boost = random.choice(Factory.AVAILABLE_BOOSTS)

        if selected_boost == "HP":  
            boost = HP_Boost(posx,posy)

        elif selected_boost == "Shield":
            boost = Shield(posx,posy)

        elif selected_boost == "Damage_Boost":
            boost = Damage_Boost(posx,posy)

        if selected_boost == "Double_Guns":
            boost = Double_Guns(posx,posy)


        game.boosts.add(boost)
        game.all_sprites.add(boost)

    @staticmethod
    def check_spawns(game):
        if len(game.boosts) < game.difficulty.MAX_CURRENT_BOOSTS and random.random() < game.difficulty.BOOST_SPAWN_PROBA:
            Factory.spawn_boost(game)

        ## Should I Spawn Enemy?
        if random.random() <= game.difficulty.ENEMY_SPAWN_PROBA and len(game.enemies) < game.difficulty.MAX_ENEMIES:
            Factory.spawn_enemy(game)



class Difficulty:
    def __init__(self):
        self.BASE_MAX_ENEMIES = 2
        self.BASE_MAX_CURRENT_STAR_DESTROYERS = 0
        self.BASE_ENEMY_SPAWN_PROBA = 0.005
        self.BASE_STAR_DESTROYER_SPAWN_PROBA = 0.1
        self.BASE_BOOST_SPAWN_PROBA = 0.1
        self.BASE_MAX_CURRENT_BOOSTS = 0

        self.MAX_ENEMIES = 2
        self.MAX_CURRENT_STAR_DESTROYERS = 0
        self.ENEMY_SPAWN_PROBA = 0.005
        self.STAR_DESTROYER_SPAWN_PROBA = 0.1
        self.BOOST_SPAWN_PROBA = 0.1
        self.MAX_CURRENT_BOOSTS = 0
        self.difficulty_level = 1

    def calculate_difficulty(self, max_value, min_value, elapsed_time):
        # Use a modified logarithmic function to adjust difficulty based on elapsed time
        max_time = 180  # 3 minutes in seconds
        min_difficulty = min_value  # Minimum value
        max_difficulty = max_value  # Maximum value
        # Modify the logarithmic function to peak quickly and then slope down gradually
        return min_difficulty + (max_difficulty - min_difficulty) * (1 - math.exp(-elapsed_time / max_time))
    

    def set_difficulty(self,seconds_passed):
        # Adjust parameters based on difficulty level and score
        # I want to adjust those parameters based on the self.difficulty_level
        self.difficulty_level = self.calculate_difficulty(30,1,seconds_passed)
        self.MAX_ENEMIES = self.calculate_difficulty(15, 1,seconds_passed)
        self.MAX_CURRENT_STAR_DESTROYERS = self.calculate_difficulty(5,0,seconds_passed)
        self.ENEMY_SPAWN_PROBA = self.calculate_difficulty(0,0.5,seconds_passed)
        self.STAR_DESTROYER_SPAWN_PROBA = self.calculate_difficulty(0,0.5,seconds_passed)
        self.BOOST_SPAWN_PROBA = self.calculate_difficulty(0.3,0.0001,seconds_passed)
        self.MAX_CURRENT_BOOSTS = self.calculate_difficulty(10,1,seconds_passed)

class Background:
    def __init__(self,image):
        self.background_speed = 3
        self.background_image = image
        self.num_tiles = Game.HEIGHT // self.background_image.get_height() + 2
        self.background_y_positions = [i * self.background_image.get_height() for i in range(self.num_tiles)]


    def scroll(self,game):
        for i, pos in enumerate(self.background_y_positions):
            self.background_y_positions[i] += self.background_speed
            # If a background tile goes off-screen, reset its position to the start of the screen
            if pos >= Game.HEIGHT:
                self.background_y_positions[i] = -self.background_image.get_height()

        game.screen.fill(Game.BACKGROUND_COLOR)

        for pos in self.background_y_positions:
            game.screen.blit(self.background_image, (0, pos))

class Hud:
    HUD_COLOR = (2,48,71,128)

    def __init__(self,game):
        self.bg_color = Hud.HUD_COLOR
        self.rect = pygame.Rect(0,0,Game.WIDTH,Game.CELL_HEIGHT)

    def render(self,game):
        pygame.draw.rect(game.screen, self.bg_color, self.rect)

        ### HP
        font = pygame.font.Font(None, 36)  # Choose a font and size for the HUD text
        hud_text = font.render(f"Lives: {game.player.lives}", True, Game.HUD_TEXT_COLOR)  # White color
        text_rect = hud_text.get_rect()
        text_rect.left = self.rect.width // 10  # Center the text within the HUD background
        text_rect.centery = self.rect.centery

        ## Score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {game.score}", True, Game.HUD_TEXT_COLOR)
        score_rect = score_text.get_rect()
        score_rect.left  = (self.rect.width // 10) * 9
        score_rect.centery = self.rect.centery

        game.screen.blit(score_text, score_rect)
        game.screen.blit(hud_text, text_rect)

        # Render each text

        texts = [
            f"Difficulty Level: {game.difficulty.difficulty_level}",
            f"MAX_ENEMIES: {game.difficulty.MAX_ENEMIES}",
            f"MAX_CURRENT_STAR_DESTROYERS: {game.difficulty.MAX_CURRENT_STAR_DESTROYERS}",
            f"ENEMY_SPAWN_PROBA: {game.difficulty.ENEMY_SPAWN_PROBA}",
            f"STAR_DESTROYER_SPAWN_PROBA: {game.difficulty.STAR_DESTROYER_SPAWN_PROBA}",
            f"BOOST_SPAWN_PROBA: {game.difficulty.BOOST_SPAWN_PROBA}",
            f"MAX_CURRENT_BOOSTS: {game.difficulty.MAX_CURRENT_BOOSTS}"
        ]
        
        font = pygame.font.Font(None,(Game.HEIGHT // Game.N_ROWS)//len(texts) )
        # Calculate the total height of all rendered texts
        total_height = sum(font.size(text)[1] for text in texts)

        # Calculate the vertical position for the first text
        initial_y = int((self.rect.height - total_height) / 2)  # Center vertically within the HUD background        initial_y = int(0)  # Center vertically within the HUD background

        # Blit each text onto the screen with vertical alignment
        for text in texts:
            hud_text = font.render(text, True, Game.HUD_TEXT_COLOR)  # White color
            text_rect = hud_text.get_rect()
            text_rect.left = (self.rect.width // 10) * 6 # Center horizontally within the HUD background
            text_rect.top = initial_y
            game.screen.blit(hud_text, text_rect)
            initial_y += text_rect.height  # Move down for the next text

class Game():

    WIDTH = 1960
    HEIGHT = 1080
    BACKGROUND_COLOR = (0,0,0)
    N_ROWS = 8 
    N_COLS = 12
    CELL_WIDTH = WIDTH / N_COLS
    CELL_HEIGHT = HEIGHT / N_ROWS

    
    HUD_TEXT_COLOR = (255,183,3)

    PROJECTILE_SOUND_FILE = "laser_blast_sound.wav"
    BACKGROUND_IMAGE_FILE = "space_background.jpg"
    


    def __init__(self):
        
        self.resource_manager = ResourceManager()
        self.projectiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.player_group = pygame.sprite.GroupSingle()
        self.boosts = pygame.sprite.Group()
        self.star_destroyers = pygame.sprite.Group()

        self.running = False
        self.difficulty = Difficulty()

        
        self.clock = pygame.time.Clock()
        self._seconds_passed = 0

        self.start_time = 0
        self.score = 0
        self.player = None

        pygame.init()
        self.screen = pygame.display.set_mode((Game.WIDTH,Game.HEIGHT))
        self.background_speed = 3
        self.background_image = self.resource_manager.load_image("space_background.jpg")
        
        pygame.display.set_caption("GALACTIC MAYHEM")
        self.hud = Hud(self)
        self.background = Background(self.background_image)
        pygame.mixer.init()  # Initialize the mixer module for sound playback
        self.projectile_sound = self.resource_manager.load_sound("laser_blast_sound.wav")  # Load the sound effect
        
    
    def handle_ship_collision(self,ship1,ship2):
        if ship1.rect.left <= ship2.rect.left:
            ship1.rect.right = ship2.rect.left - 10
            ship1.is_moving_left = True
            ship2.is_moving_left = False
        else:
            ship1.rect.left = ship2.rect.right + 10
            ship1.is_moving_left = False
            ship2.is_moving_left = True

    @staticmethod
    def _ship_collisions_helper(collision_dict):
        new_ship_collisions = {}
        for ship, collided_ships in collision_dict.items():
            new_collided_ships = list(collided_ships)
            if ship in new_collided_ships:
                new_collided_ships.remove(ship)
            new_ship_collisions[ship] = new_collided_ships
        return new_ship_collisions


    def handle_ship_collisions(self):
        ship_collisions = pygame.sprite.groupcollide(self.enemies, self.enemies, dokilla=False, dokillb=False)
        ship_collisions = Game._ship_collisions_helper(ship_collisions)
        while any(collided_ships for collided_ships in ship_collisions.values()):
            ship_collisions = pygame.sprite.groupcollide(self.enemies, self.enemies, dokilla=False, dokillb=False)
            ship_collisions = Game._ship_collisions_helper(ship_collisions)
            for ship in list(ship_collisions.keys()):  # Create a copy of the keys
                collided_ships = ship_collisions[ship]
                for collided_ship in collided_ships:
                    self.handle_ship_collision(ship,collided_ship)
                    break
            
            ship_collisions = pygame.sprite.groupcollide(self.enemies, self.enemies, dokilla=False, dokillb=False)
            ship_collisions = Game._ship_collisions_helper(ship_collisions)





    def play(self):
        self.running = True
        self.player = PlayerShip()
        self.player_group.add(self.player)
        x = 0
        self.start_time = pygame.time.get_ticks()
        while self.running: #and self.player.lives >= 0:

            self.background.scroll(self)
            self.hud.render(self)
            

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False 

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if not self.player.double_firing: 
                            Factory.spawn_projectile(self,self.player,1)
                        else:
                            Factory.spawn_projectile(self,self.player,2)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: 
                self.player.move(self,"l")
            if keys[pygame.K_RIGHT]:
                self.player.move(self,"r")

            Factory.check_spawns(self)

            self.enemies.update(game)
            self.projectiles.update()
            self.player_group.update()
            self.boosts.update(game)
            self.all_sprites.draw(self.screen)
            self.player.draw(self.screen)

            self.handle_ship_collisions()
            self.player.check_collision(self)

            if pygame.time.get_ticks() - self.start_time >= 1000:  # 1000 milliseconds = 1 second
                self.update_score()
                self._seconds_passed += 1
                self.start_time = pygame.time.get_ticks()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def update_score(self):
            time_bonus = 100  # Award 1 point per second survived
            self.score += time_bonus
            self.difficulty.set_difficulty(self._seconds_passed)




game = Game()
game.play()
            
            
        
        
