import pygame
import os
import time
import random
import winsound
import playsound
pygame.font.init()

WIDTH, HEIGHT = 950, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Coronski")

# virus
VIRUZ1 = pygame.image.load(os.path.join("assets", "virus1.png"))
VIRUZ2 = pygame.image.load(os.path.join("assets", "virus2.png"))
VIRUZ3 = pygame.image.load(os.path.join("assets", "virus3.png"))

# Player or doctor
DOCTOR = pygame.image.load(os.path.join("assets", "dokter2.png"))

# tembakan
SPREAD = pygame.image.load(os.path.join("assets", "bakteri2.png"))
VAKSIN = pygame.image.load(os.path.join("assets", "vaksin.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "hospitall.png")), (WIDTH, HEIGHT))

INFECTED = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "infected1.jpg")), (WIDTH, HEIGHT))


class Laser:
    def __init__(self, x, y, img):
        self.x = x + 50
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

    def __init__(self, x, y, health=5, score=0):
        self.x = x
        self.y = y
        self.health = health
        self.score = score
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
                obj.health -= 1
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


class Doctor(Ship):
    def __init__(self, x, y, health=5, score=0):
        super().__init__(x, y, health, score)
        self.ship_img = DOCTOR
        self.laser_img = VAKSIN
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.max_score = score

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        self.max_score += 1
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)


class Virus(Ship):
    COLOR_MAP = {
        "virus1": (VIRUZ1, SPREAD),
        "virus2": (VIRUZ2, SPREAD),
        "virus3": (VIRUZ3, SPREAD)
    }

    def __init__(self, x, y, color, health=5):
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
    run = True
    FPS = 100
    main_font = pygame.font.SysFont("comicsans", 40)

    enemies = []
    wave_length = 5
    enemy_vel = 2

    player_vel = 6
    laser_vel = 4

    player = Doctor(350, 450)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    winsound.PlaySound('D:/Coronski/sounds/bg5.wav',
                       winsound.SND_LOOP + winsound.SND_ASYNC)

    def redraw_window():
        WIN.blit(BG, (0, 0))
        # draw text
        health_label = main_font.render(
            f"Health: {player.health}", 1, (53, 118, 134))
        score_label = main_font.render(
            f"Score: {player.max_score}", 1, (243, 58, 58))

        WIN.blit(health_label, (15, 15))
        WIN.blit(score_label, (WIDTH - score_label.get_width() - 15, 15))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if player.health == 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 1:
                run = False
                WIN.blit(INFECTED, (0, 0))
                winsound.PlaySound('D:/Coronski/sounds/gameover.wav',
                                   winsound.SND_LOOP + winsound.SND_ASYNC)
                lost_label = main_font.render(
                    "Oh No, You've been exposed to the coronavirus!!", 1, (50, 50, 50))
                WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 50))
                score_label = main_font.render(
                    f"You're score is : {player.max_score}", 1, (50, 50, 50))
                WIN.blit(score_label, (WIDTH/2 - score_label.get_width()/2, 600))
                pygame.display.update()
                time.sleep(6)
            else:
                continue

        if len(enemies) == 0:
            wave_length += 5
            for i in range(wave_length):
                enemy = Virus(random.randrange(
                    50, WIDTH-100), random.randrange(-1500, -100), random.choice(["virus1", "virus2", "virus3"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:  # right
            player.x += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 1*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render(
            "Press the mouse to START...", 1, (30, 30, 30))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 50))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
