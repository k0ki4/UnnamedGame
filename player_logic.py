import time
import pygame
from pygame.examples.go_over_there import screen

from inventory_logic import Inventory
from loot.chest import LootChest


class Player(pygame.sprite.Sprite):
    def __init__(self, board, *groups, hp=10, default_damage=1, default_armor=1):
        super().__init__(*groups)
        self.board = board

        self.inventory = Inventory()

        self.radar_list = []

        self.lvl = 1

        self.default_damage = default_damage
        self.default_armor = default_armor
        self.equip_weapon = None
        self.armor = None
        self.damage = None
        self.hp = hp
        self.action_count = 4
        self.calc_stats()

        self.image = pygame.Surface((board.cell_size, board.cell_size))
        self.image.fill("ORANGE")
        self.rect = self.image.get_rect()  # Получаем прямоугольник для спрайта

        self.board.board[0][0] = 10
        self.rect.x, self.rect.y = 0 * board.cell_size + board.left, 0 * board.cell_size + board.top

        self.last_move_time = 0  # Время последнего движения
        self.move_delay = 0.2  # Задержка в секундах

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 15)

    def calc_stats(self):
        if self.equip_weapon:
            pass
        else:
            self.armor = self.default_armor
            self.damage = self.default_damage

    def calc_cell(self, cell, action_step):
        x, y = cell
        # Проверяем границы
        if not (0 <= x + action_step[0] < self.board.width and 0 <= y + action_step[1] < self.board.height):
            return x, y  # Возвращаем текущее положение, если движение недопустимо
        if self.board.board[y + action_step[1]][x + action_step[0]] != 0:
            return x, y
        self.board.board[y][x] = 0
        return x + action_step[0], y + action_step[1]  # Возвращаем новое положение

    def render_stats(self, screen):
        stats_img = pygame.image.load('sprites/gui/gui.png').convert_alpha()
        stats_img2 = pygame.image.load('sprites/gui/gui_2.png').convert_alpha()
        stats_rect = pygame.Rect(800, 6, 400, 785)
        stats_rect2 = pygame.Rect(800, 6, 400, 785)
        stats_imp_scaled = pygame.transform.scale(stats_img, (stats_rect.width, stats_rect.height))
        stats_imp_scaled2 = pygame.transform.scale(stats_img2, (stats_rect2.width, stats_rect.height))

        screen.blit(stats_imp_scaled, stats_rect.topleft)
        screen.blit(stats_imp_scaled2, stats_rect2.topleft)

        # Отображаем текст статистики
        hp_text = self.font.render(f"HP: {self.hp}", True, (255, 255, 255))  # Белый текст
        damage_text = self.font.render(f"Урон: {self.damage}", True, (255, 255, 255))
        armor_text = self.font.render(f"Защита: {self.armor}", True, (255, 255, 255))
        actions_text = self.font.render(f"Осталось действий: {self.action_count}", True,
                                        (255, 255, 255))
        lvl_text = self.font.render(f"Уровень: {self.lvl}", True, (255, 255, 255))


        cord_text_x = 840
        # Позиции текста
        screen.blit(hp_text, (cord_text_x, 20))
        screen.blit(damage_text, (cord_text_x, 40))
        screen.blit(armor_text, (cord_text_x, 60))
        screen.blit(actions_text, (cord_text_x, 80))
        screen.blit(lvl_text, (cord_text_x, 100))

        self.count_usage(screen)

    def update(self, keys):
        current_time = time.time()
        if current_time - self.last_move_time >= self.move_delay:
            if keys[pygame.K_w]:
                x, y = self.calc_cell((self.rect.x // self.board.cell_size, self.rect.y // self.board.cell_size),
                                      (0, -1))
                self.board.board[y][x] = 10
                self.rect.x, self.rect.y = (x * self.board.cell_size + self.board.left,
                                            y * self.board.cell_size + self.board.top)
            if keys[pygame.K_s]:
                x, y = self.calc_cell((self.rect.x // self.board.cell_size, self.rect.y // self.board.cell_size),
                                      (0, 1))
                self.board.board[y][x] = 10
                self.rect.x, self.rect.y = (x * self.board.cell_size + self.board.left,
                                            y * self.board.cell_size + self.board.top)
            if keys[pygame.K_a]:
                x, y = self.calc_cell((self.rect.x // self.board.cell_size, self.rect.y // self.board.cell_size),
                                      (-1, 0))
                self.board.board[y][x] = 10
                self.rect.x, self.rect.y = (x * self.board.cell_size + self.board.left,
                                            y * self.board.cell_size + self.board.top)
            if keys[pygame.K_d]:
                x, y = self.calc_cell((self.rect.x // self.board.cell_size, self.rect.y // self.board.cell_size),
                                      (1, 0))
                self.board.board[y][x] = 10
                self.rect.x, self.rect.y = (x * self.board.cell_size + self.board.left,
                                            y * self.board.cell_size + self.board.top)
            self.last_move_time = current_time

    def open_inventory(self):
        self.inventory.toggle()

    def count_usage(self, screen):
        x, y = self.board.get_cell((self.rect.x, self.rect.y))
        direction = [
            (-1, 0),  # вверх
            (1, 0),  # вниз
            (0, -1),  # влево
            (0, 1)  # вправо
        ]
        for dx, dy in direction:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board.width and 0 <= ny < self.board.height:
                if isinstance(self.board.board[ny][nx], LootChest):
                    self.radar_list.append(self.board.board[ny][nx])
        take_img = pygame.image.load("sprites/gui/gui_2.png.").convert_alpha()
        take_img = pygame.transform.scale(take_img, (60, 60))
        screen.blit(take_img, (820, 500))
        if self.radar_list:
            pass