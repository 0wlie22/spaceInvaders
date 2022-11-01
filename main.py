import pygame
import os
import time
import random

pygame.init()

WIDTH, HEIGHT = 1280, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space invaders')
icon = pygame.image.load(os.path.join("images", "icon.png"))
pygame.display.set_icon(icon)

RED_SPACE_SHIP = pygame.image.load(os.path.join("images", "enemy_red.png"))         #128x128
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("images", "enemy_green.png"))     #128x128
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("images", "enemy_blue.png"))       #128x128

SPACE_SHIP = pygame.image.load(os.path.join("images", "ship.png"))                  #128x128

RED_LASER = pygame.image.load(os.path.join("images", "pixel_laser_red.png"))        #100x90
GREEN_LASER = pygame.image.load(os.path.join("images", "pixel_laser_green.png"))    #100x90
BLUE_LASER = pygame.image.load(os.path.join("images", "pixel_laser_blue.png"))      #100x90
BULLET = pygame.image.load(os.path.join("images", "bullet.png"))                    #100x90

BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("images", "background.png")), (WIDTH, HEIGHT))

level_limit = random.randrange(5, 10)
enemy_killed = 0
koordinates = []

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 20

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = SPACE_SHIP
        self.laser_img = BULLET
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        global enemy_killed

        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
                enemy_killed -= 1
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        enemy_killed += 1
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    level = 1
    run = True
    FPS = 80
    lives = 3
    main_font = pygame.font.SysFont("arial", 50)
    lost_font = pygame.font.SysFont("arial", 60)
    
    koord_x = random.randrange(100, WIDTH-100)
    enemies = [(Enemy(koord_x, 0, random.choice(["red", "blue", "green"])))]

    wave_length = 2
    enemy_vel = 2

    player_vel = 7
    laser_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    win = False
    lost_count = 0

    def redraw_window():
        global enemy_killed

        WIN.blit(BACKGROUND, (0,0))
        lives_label = main_font.render(f"LIVES LEFT: {lives}", 2, (255, 255, 255))
        level_label = main_font.render(f"LEVEL: {level}", 1, (255, 255, 255))
        score_label = main_font.render(f"SCORE: {enemy_killed}", 1, (255, 255, 255))

        WIN.blit(score_label, ((WIDTH - score_label.get_width())/2, 10))
        WIN.blit(lives_label, (WIDTH - lives_label.get_width() - 10, 10))
        WIN.blit(level_label, (10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)
        score_label = main_font.render(f"YOUR SCORE IS {enemy_killed}", 1, (0, 0, 0))

        if lost:
            lost_label = lost_font.render("GAME OVER!", 1, (0, 0, 0))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        if win:
            win_label = lost_font.render("YOU WON!", 1, (0, 0, 0))
            WIN.blit(win_label, (WIDTH/2 - win_label.get_width()/2, 350))
            WIN.blit(score_label, (WIDTH/2 - score_label.get_width()/2, 450))

        pygame.display.update()

    while run:
        global x
        global y
        global koordinates
        global enemy_killed
        
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0 or enemy_killed < 0:
            lost = True
            lost_count += 1

        if lost: 
            if lost_count >= FPS * 3:
                enemy_killed = 0   
                run = False
            else:
                continue
           
           
        if win:
            if lost_count <= 0:
                enemy_killed = 0
                pygame.time.wait(3000)
                run = False
            else:
                continue     
        
        if level == level_limit + 1:
            win = True

        if len(enemies) == 0:
            level += 1
            wave_length += 5

            for i in range(wave_length): 
                x_koord = random.randrange(0, 8) * 150 + 5
                y_koord = random.randrange(-12,-1) * 100
                koord = str(x_koord) + str(y_koord)

                if koord not in koordinates:
                    koordinates.append(koord)
                    enemy = Enemy(x_koord, y_koord, random.choice(["red", "blue", "green"]))
                    enemies.append(enemy)
                

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: 
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: 
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0: 
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT: 
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    
    title_font = pygame.font.SysFont("arial", 50)
    level_font = pygame.font.SysFont("arial", 40)
    run = True

    while run:
        WIN.blit(BACKGROUND, (0,0))
        title_label = title_font.render("PRESS MOUSE TO BEGIN ", 1, (0, 0, 0))
        level_label = level_font.render(f"TO WIN YOU NEED TO GET TO LEVEL {level_limit + 1}", 1, (0 ,0, 0))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        WIN.blit(level_label, (WIDTH/2 - level_label.get_width()/2, 450))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
            
    pygame.quit()

main_menu()