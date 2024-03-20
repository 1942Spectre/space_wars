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
        screen.blit(self._image,self.rect)


    

class Projectile(Object):
    def __init__(self, owner):
        self.owner = owner
        self._width = 5
        self._height = 30
        self._speed = 10

        if self.owner == "CPU":
            self._color = (255, 0, 0)  # Red color
            self._direction = "d"
        elif self.owner == "Player":
            self._color = (0, 0, 255)  # Blue color
            self._direction = "u"

        # Create a rect for the projectile
        self.rect = pygame.Rect(0, 0, self._width, self._height)

    def move(self,game):
        super().move(game,self._direction)

        if self.rect.bottom < 0 or self.rect.top > game.height:
            self.remove(game)

    def remove(self,game):
        game.projectiles.remove(self)

    def display(self,screen):
        pygame.draw.rect(screen,self._color,self.      rect)
    

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
        self._height = 120
        self._width = 90
        self.movement_state = 0
        posx = positionx * self._width
        posy = positiony * self._height
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
            if self.rect.colliderect(projectile.rect) and projectile.owner == "Player":
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
        self._image = pygame.image.load("enemy_tie_fighter.png")
        super().__init__(game,positionx,positiony)
        self.max_lives = 3
        self.lives = 3
        self._speed = 2
        self.fire_probability = 0.01
        self.cd_probability = 0.1

    def move(self,game):
        self.check_collision(game)
        if self.should_fire():
            self.fire(game)
        super().move(game)

        


    
class Game():

    def __init__(self):
        self.width = 1024
        self.height = 1024
        self.background_color = (0,0,0)
        self.projectile_color = (255,255,255)
        self.projectiles = []
        self.enemies = []
        self.clock = pygame.time.Clock()
 
        self.tiefighter_spawn_proba = 0.01

    def play(self):
        pygame.init()
        screen = pygame.display.set_mode((self.width,self.height))
        pygame.display.set_caption("Space Shooter")
        player = PlayerShip(self)
        running = True
        while running and player.lives >= 0:
            screen.fill(self.background_color)
            if random.random() < self.tiefighter_spawn_proba and len(self.enemies) < 10:
                positionx = random.choice([i for i in range(0,self.width // 90)])
                positiony = random.choice([i for i in range(0,(self.height//2) // 120)])
                tfighter = TieFighter(self,positionx,positiony)
                self.enemies.append(tfighter)
            # Event Handling
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

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()



game = Game()
game.play()
            
            
        
        
