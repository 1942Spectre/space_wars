import pygame
import sys
import random




class Object:
    def move(self,game,direction):
        if direction == "l":
            self.rect.x -= self._speed
        elif direction == "r":
            self.rect.x += self._speed

        elif direction == "u":
            self.rect.y -= self._speed

        elif direction == "d":
            self.rect.y += self._speed
        self.rect.x = max(0, min(self.rect.x, game.width - self.rect.width))
    
    def display(self,screen):
        if self._image:
            screen.blit(self._image,self.rect)
        else:
            pygame.draw.rect(screen,self._color,self.rect)


class EnemyFactory:
    @staticmethod
    def spawn_enemy(game,type):
        posx = random.choice(range(0,game.n_columns)) * game.cell_width
        posy = random.choice(range(1,5)) * game.cell_height 
        # Now you can create an enemy at the selected empty cell
        if type == "TieFighter":
            enemy = TieFighter(game, posx, posy)
            return enemy
        
        elif type == "StarDestroyer":
            enemy = StarDestroyer(game,posx,posy)
            return enemy
        else:
            return None  # No suitable empty cell found for spawning an enemy
        
class AsteroidFactory:
    @staticmethod
    def spawn_asteroid(game):
        column = random.choice(range(0,game.n_columns)) * game.cell_width
        return Asteroid(column)


class Projectile(Object):
    def __init__(self, owner,is_asteroid = False):
        self.owner = owner
        self._width = 5
        self._height = 30 
        self._speed = 10

        if self.owner == "CPU":
            self._color = (255, 0, 0)  # Red color
            self._direction = "d"
            self._image = None
        elif self.owner == "Player":
            self._color = (0, 0, 255)  # Blue color
            self._direction = "u"
            self._image = None

        if not is_asteroid:
            # Create a rect for the projectile
            self.rect = pygame.Rect(0, 0, self._width, self._height)
        
        self.is_asteroid = is_asteroid

    def move(self,game):
        super().move(game,self._direction)

        if self.rect.bottom < 0 or self.rect.top > game.height:
            self.remove(game)

    def remove(self,game):
        game.projectiles.remove(self)



class Asteroid(Projectile):
    def __init__(self,column):
        super().__init__("CPU",True) 
        self._height = 90
        self._width = 90
        self._image = pygame.image.load("asteroid.png")
        self._image = pygame.transform.scale(self._image,(self._width,self._height))
        self.rect = self._image.get_rect()
        posy = 1 * game.cell_height 
        self.rect.top = posy+20
        self.rect.left = column 
        self._speed = 5

    def remove(self,game):
        game.projectiles.remove(self)
        game.num_asteroids -= 1

    def display(self,screen):
        super().display(screen)

    
    

class PlayerShip(Object):
    def __init__(self,game):
        self._image = pygame.image.load("player_ship.png")

        self._height = 80
        self._width = 60
        self.max_lives = 3
        self._image = pygame.transform.scale(self._image,(self._width,self._height))
        self.rect = self._image.get_rect()

        self.rect.centerx = game.width // 2 ## Horizontally center
        self.rect.bottom = game.height -20 ## Vertically 20 pixels above bottom
        self._speed = 5
        self.lives = 3

    def fire(self):
        projectile = Projectile("Player")
        projectile.rect.centerx = self.rect.centerx
        projectile.rect.bottom = self.rect.top
        game.projectile_sound.play(loops=0)
        return projectile
    
    def check_collision(self,game):
        for projectile in game.projectiles:
            if self.rect.colliderect(projectile.rect):
                projectile.remove(game)
                self.lives -= 1
                self.update_opacity()


    def update_opacity(self):
        # Calculate and set opacity based on current lives
        opacity_step = 255 // self.max_lives
        alpha_value = max(0, 255 - opacity_step * (self.max_lives - self.lives))  # Corrected calculation
        print(alpha_value)
        self._image.set_alpha(alpha_value)

                
class Enemy(Object):
    def __init__(self,game,positionx,positiony):
        self.movement_state = 0
        posx = positionx 
        posy = positiony 
        self._image = pygame.transform.scale(self._image,(self._width,self._height))
        self.rect = self._image.get_rect()
        self.rect.top = posy+20
        self.rect.left = posx 
        self.moving_left = random.random() < 0.5

    def fire(self,game):
        projectile = Projectile("CPU")
        projectile.rect.centerx = self.rect.centerx
        projectile.rect.top = self.rect.bottom
        game.projectiles.append(projectile)
        game.projectile_sound.play(loops=0)


    def remove(self,game):
        game.enemies.remove(self)
    
    def update_opacity(self):
        # Calculate and set opacity based on current lives
        opacity_step = 255 // self.max_lives
        alpha_value = max(0, 255 - opacity_step * (self.max_lives - self.lives))  # Corrected calculation
        print(alpha_value)
        self._image.set_alpha(alpha_value)
    
    def check_collision(self,game):
        for projectile in game.projectiles:
            if self.rect.colliderect(projectile.rect) and (projectile.owner == "Player") or (projectile.is_asteroid):
                projectile.remove(game)
                self.lives -= 1
                self.update_opacity()
                if self.lives == 0:  
                    self.remove(game)
                print("Projectile collusion")
        for enemy in game.enemies:
            if enemy != self and self.rect.colliderect(enemy.rect):
                # Teleport enemies to avoid trapping
                if self.moving_left:
                    self.rect.left = enemy.rect.right +1
                else:
                    self.rect.right = enemy.rect.left -1
                # Change direction after teleportation
                self._change_direction()

        if self.rect.right == game.width or self.rect.left == 0:
            self._change_direction()

                    
    def move(self,game):
        if self.moving_left:
            self._move_left(game)
        else:
            self._move_right(game)

    def _move_left(self,game):
        self.rect.x -= self._speed
        if self.rect.left <= 0:
            self.rect.left = 0

    def _move_right(self,game):
        self.rect.x += self._speed
        if self.rect.right >= game.width:
            self.rect.right = game.width

    def _change_direction(self):
        self.moving_left = not self.moving_left

    def should_fire(self):
        return random.random() < self.fire_probability
    
    def should_change_direction(self):
        return random.random() < self.cd_probability
    


class TieFighter(Enemy):
    def __init__(self,game,positionx,positiony):
        self._height = 120
        self._width = 90
        self._image = pygame.image.load("enemy_tie_fighter.png")
        super().__init__(game,positionx,positiony)
        self.max_lives = 3
        self.lives = 3
        self._speed = 2
        self.fire_probability = 0.005
        self.cd_probability = 0.1

    def move(self,game):
        self.check_collision(game)
        if self.should_fire():
            self.fire(game)
        super().move(game)

class StarDestroyer(Enemy): 
    def __init__(self,game,positionx,positiony):
        self._image = pygame.image.load("star_destroyer.png")
        self._height = 120
        self._width = 360
        super().__init__(game,positionx,positiony)
        self.max_lives = 10
        self.lives = 10
        self._speed = 1 
        self.fire_probability = 0.01
        self.cd_probability = 0.1
    
    def move(self,game):
        self.check_collision(game)
        if self.should_fire():
            self.fire(game)
        super().move(game)

    def fire(self,game):
        gun = random.choice(["left","right","center"])

        if gun == "left":
            projectile = Projectile("CPU")
            projectile.rect.centerx = self.rect.left
            projectile.rect.top = self.rect.bottom

        elif gun == "right":
            projectile = Projectile("CPU")
            projectile.rect.centerx = self.rect.right
            projectile.rect.top = self.rect.bottom
        
        elif gun == "center":
            projectile = Projectile("CPU")
            projectile.rect.centerx = self.rect.centerx
            projectile.rect.top = self.rect.bottom

        game.projectiles.append(projectile)
        game.projectile_sound.play(loops=0)
        


    
class Game():

    def __init__(self):
        self.width = 1960
        self.height = 1080
        # Load the background image
        self.background_color = (0, 0, 0)

        self.projectiles = []
        self.enemies = []
        self.background_speed = 3 
        self.clock = pygame.time.Clock()
        

        self.n_rows = 12
        self.n_columns = 12

        self.cell_width = self.width / self.n_columns
        self.cell_height = self.height / self.n_rows

        self.background_image = None

        self.max_enemies = 10
        self.tiefighter_spawn_proba = 0.01

        pygame.mixer.init()  # Initialize the mixer module for sound playback
        self.projectile_sound = pygame.mixer.Sound("laser_blast_sound.wav")  # Load the sound effect
        

        self.star_destroyer_spawn_proba = 0.05 

        self.num_asteroids = 0
        self.asteroid_spawn_proba = 0.002

    def get_available_cells(game):
        available_cells = []
        # Check each cell in the designated rows for emptiness and free spaces on left and right
        for row in range(1, game.num_rows):  # Start from row 1 as row 0 is reserved for HUD
            for col in range(game.num_cols):
                if not game.is_cell_occupied(row, col) and \
                        (col > 0 and not game.is_cell_occupied(row, col - 1)) and \
                        (col < game.num_cols - 1 and not game.is_cell_occupied(row, col + 1)):
                    available_cells.append((row, col))

        return available_cells
    
    def render_hud(self, screen, player):
        # Render HUD
        hud_color = (2,48,71,128)
        hud_text_color = (255,183,3)
        hud_rect = pygame.Rect(0, 0, self.width, self.cell_height)  # HUD spans the entire width of the window        pygame.draw.rect(screen, hud_color, hud_rect)
        pygame.draw.rect(screen, hud_color, hud_rect)

        font = pygame.font.Font(None, 36)  # Choose a font and size for the HUD text
        hud_text = font.render(f"Lives: {player.lives}", True, hud_text_color)  # White color
        text_rect = hud_text.get_rect()
        text_rect.center = hud_rect.center  # Center the text within the HUD background
        screen.blit(hud_text, text_rect)

    def scroll_background(self,background_y_positions,screen):
        for i, pos in enumerate(background_y_positions):
            background_y_positions[i] += self.background_speed
            # If a background tile goes off-screen, reset its position to the start of the screen
            if pos >= self.height:
                background_y_positions[i] = -self.background_image.get_height()

        screen.fill(self.background_color)

        # Draw the background tiles
        for pos in background_y_positions:
            screen.blit(self.background_image, (0, pos))

    def should_spawn_star_destroyer(self):
        if self.should_spawn_enemy():
            return random.random() < self.star_destroyer_spawn_proba
        return False

    def should_spawn_enemy(self):
        return random.random() < self.tiefighter_spawn_proba and len(self.enemies) < self.max_enemies

    def should_spawn_asteroid(self):
        return random.random() < self.asteroid_spawn_proba and self.num_asteroids < 2
    
    def play(self):
        pygame.init()
        screen = pygame.display.set_mode((self.width,self.height))
        self.background_image = pygame.image.load("space_background.jpg").convert()
        pygame.display.set_caption("Space Shooter")

        num_tiles = self.height // self.background_image.get_height() + 2
        background_y_positions = [i * self.background_image.get_height() for i in range(num_tiles)]
        
        
        player = PlayerShip(self)
        running = True
        
        
        while running and player.lives >= 0:
            # Scroll the background
            self.scroll_background(background_y_positions,screen)

            if self.should_spawn_enemy():
                self.enemies.append(EnemyFactory.spawn_enemy(self,"TieFighter"))

            if self.should_spawn_star_destroyer():
                self.enemies.append(EnemyFactory.spawn_enemy(self,"StarDestroyer"))

            if self.should_spawn_asteroid():
                self.projectiles.append(AsteroidFactory.spawn_asteroid(self))
                self.num_asteroids += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        projectile = player.fire()
                        self.projectiles.append(projectile)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.move(self,"l")
            if keys[pygame.K_RIGHT]:
                player.move(self,"r")

            
            for enemy in self.enemies: 
                enemy.move(self)
                enemy.display(screen)

            for projectile in self.projectiles:
                projectile.move(self)
                projectile.display(screen)
            
            player.check_collision(self)
            if player.lives == 0:
                break
            player.display(screen)
            self.render_hud(screen,player)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()



game = Game()
game.play()
            
            
        
        
