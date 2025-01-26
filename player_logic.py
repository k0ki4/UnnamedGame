import math
import random
import time
import pygame

from inventory_logic import Inventory, EquipItemSlot, HelmetSlot, ChestplateSlot, LeggingsSlot
from loot.chest import LootChest
from monsters.monster_logic import Monster


class Player(pygame.sprite.Sprite):
    def __init__(self, board, *groups, hp=10, default_damage=1, default_armor=1):
        super().__init__(*groups)
        self.board = board

        self.inventory = Inventory()

        self.radar_list = []
        self.radar_img = None

        self.lvl = 1
        self.xp = 0

        self.default_damage = default_damage
        self.default_armor = default_armor
        self.armor = 0
        self.damage = 0
        self.hp = hp
        self.action_const = 4
        self.action_count = 4

        self.image = pygame.Surface((board.cell_size, board.cell_size))
        self.image.fill("ORANGE")
        self.rect = self.image.get_rect()  # Получаем прямоугольник для спрайта

        self.board.board[0][0] = self
        self.rect.x, self.rect.y = 0 * board.cell_size + board.left, 0 * board.cell_size + board.top

        self.fight_mode = False

        self.last_move_time = 0  # Время последнего движения
        self.move_delay = 0.1  # Задержка в секундах

        self.pulse_time = 0

        self.last_fight_render_time = 0
        self.fight_render_time_delay = 0.5

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 15)

        self.is_dead = False

    def get_xp(self, count):
        self.xp += count
        if self.xp >= 10:
            self.xp -= 10
            self.lvl += 1

    def calc_stats(self):
        self.damage = 0
        self.armor = 0
        self.damage += self.default_damage
        self.armor += self.default_armor
        equip_weapon = [slot.item.damage for slot in self.inventory.unic_slot if
                        slot.item is not None and isinstance(slot, EquipItemSlot)]
        equip_armor = [slot.item.protect for slot in self.inventory.unic_slot if slot.item is not None and
                       isinstance(slot, (HelmetSlot, ChestplateSlot, LeggingsSlot))]
        if equip_armor:
            self.armor += sum(equip_armor)
        if equip_weapon:
            self.damage += sum(equip_weapon)
        self.damage += self.lvl

    def calc_cell(self, cell, action_step):
        x, y = cell
        # Проверяем границы
        if not (0 <= x + action_step[0] < self.board.width and 0 <= y + action_step[1] < self.board.height):
            return x, y  # Возвращаем текущее положение, если движение недопустимо
        if self.board.board[y + action_step[1]][x + action_step[0]] != 0:
            return x, y
        self.board.board[y][x] = 0
        self.action_count -= 1
        return x + action_step[0], y + action_step[1]  # Возвращаем новое положение

    def render_stats(self, screen):
        self.calc_stats()

        stats_img = pygame.image.load('sprites/gui/gui.png').convert_alpha()
        stats_img2 = pygame.image.load('sprites/gui/gui_2.png').convert_alpha()
        stats_rect = pygame.Rect(800, 6, 400, 785)
        stats_rect2 = pygame.Rect(800, 6, 400, 785)
        stats_imp_scaled = pygame.transform.scale(stats_img, (stats_rect.width, stats_rect.height))
        stats_imp_scaled2 = pygame.transform.scale(stats_img2, (stats_rect2.width, stats_rect.height))

        screen.blit(stats_imp_scaled, stats_rect.topleft)
        screen.blit(stats_imp_scaled2, stats_rect2.topleft)

        take_img = pygame.image.load("sprites/take.png").convert_alpha()
        take_img = pygame.transform.scale(take_img, (60, 60))
        take_img_rect = pygame.Rect(845, 500, 60, 60)
        screen.blit(take_img, take_img_rect)

        start_fight = pygame.image.load("sprites/take.png").convert_alpha()
        start_fight = pygame.transform.scale(start_fight, (60, 60))
        start_fight_rect = pygame.Rect(845, 600, 60, 60)
        screen.blit(start_fight, start_fight_rect)

        start_fight_text = self.font.render("Провести атаку", True, (255, 255, 255))  # Белый текст
        start_fight_text_2 = self.font.render("R", True, (255, 255, 255))  # Белый текст
        screen.blit(start_fight_text, (830, 580))

        text_width, text_height = start_fight_text_2.get_size()
        text_x = start_fight_rect.x + (start_fight_rect.width - text_width) // 2
        text_y = start_fight_rect.y + (start_fight_rect.height - text_height) // 2
        screen.blit(start_fight_text_2, (text_x, text_y))

        take_text_take = self.font.render("Взаимодействовать", True, (255, 255, 255))  # Белый текст
        take_text = self.font.render("E", True, (255, 255, 255))  # Белый текст
        screen.blit(take_text_take, (820, 470))
        if self.radar_list:
            text_width, text_height = take_text.get_size()
            text_x = take_img_rect.x + (take_img_rect.width - text_width) // 2
            text_y = take_img_rect.y + (take_img_rect.height - text_height) // 2
            screen.blit(take_text, (text_x, text_y))

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

        self.count_usage()

    def update(self, keys, screen):
        if keys[pygame.K_r]:
            self.fight_mode = not self.fight_mode
            return

        current_time = time.time()
        if current_time - self.last_move_time >= self.move_delay and not self.fight_mode and self.action_count:
            if keys[pygame.K_w]:
                x, y = self.calc_cell((self.rect.x // self.board.cell_size, self.rect.y // self.board.cell_size),
                                      (0, -1))
                self.board.board[y][x] = self
                self.rect.x, self.rect.y = (x * self.board.cell_size + self.board.left,
                                            y * self.board.cell_size + self.board.top)
            if keys[pygame.K_s]:
                x, y = self.calc_cell((self.rect.x // self.board.cell_size, self.rect.y // self.board.cell_size),
                                      (0, 1))
                self.board.board[y][x] = self
                self.rect.x, self.rect.y = (x * self.board.cell_size + self.board.left,
                                            y * self.board.cell_size + self.board.top)
            if keys[pygame.K_a]:
                x, y = self.calc_cell((self.rect.x // self.board.cell_size, self.rect.y // self.board.cell_size),
                                      (-1, 0))
                self.board.board[y][x] = self
                self.rect.x, self.rect.y = (x * self.board.cell_size + self.board.left,
                                            y * self.board.cell_size + self.board.top)
            if keys[pygame.K_d]:
                x, y = self.calc_cell((self.rect.x // self.board.cell_size, self.rect.y // self.board.cell_size),
                                      (1, 0))
                self.board.board[y][x] = self
                self.rect.x, self.rect.y = (x * self.board.cell_size + self.board.left,
                                            y * self.board.cell_size + self.board.top)
            if keys[pygame.K_e]:
                if self.radar_list:
                    for i in self.radar_list:
                        if isinstance(i, LootChest):
                            i.toggle_chest(self)
            if keys[pygame.K_q]:
                for i in self.board.board:
                    print(i)
                print()
            self.last_move_time = current_time
            self.radar_list = []

    def open_inventory(self):
        self.inventory.toggle()

    def get_cell(self, mouse_pos):
        cell_x = (mouse_pos[0] - self.board.left) // self.board.cell_size
        cell_y = (mouse_pos[1] - self.board.top) // self.board.cell_size
        if 0 <= cell_x <= self.board.width and 0 <= cell_y <= self.board.height:
            return cell_x, cell_y
        return None

    def get_cords(self, x, y):
        cord_x, cord_y = (x * self.board.cell_size + self.board.left,
                          y * self.board.cell_size + self.board.top)

        return cord_x, cord_y

    def count_usage(self):
        x, y = self.get_cell((self.rect.x, self.rect.y))
        direction = [
            (-1, 0),  # вверх
            (1, 0),  # вниз
            (0, -1),  # влево
            (0, 1)  # вправо
        ]
        for dx, dy in direction:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board.width and 0 <= ny < self.board.height:
                if self.board.board[ny][nx] != 0:
                    if self.board.board[ny][nx] not in self.radar_list:
                        self.radar_list.append(self.board.board[ny][nx])

    def fight_cell(self, screen):
        num = random.randint(-3, 3)
        current_time = time.time()
        base_size = self.board.cell_size - 10  # Размер куба с учетом отступа
        rect = pygame.Rect(0, 0, base_size, base_size)

        x, y = self.get_cell((self.rect.x, self.rect.y))
        direction = [
            (-1, -1),
            (-1, 0),  # вверх
            (-1, 1),
            (1, 0),  # вниз
            (1, -1),
            (1, 1),
            (0, -1),  # влево
            (0, 1)  # вправо
        ]

        # Изменяем время пульсации
        self.pulse_time += 0.05  # Увеличиваем время (можно настроить скорость)

        for dx, dy in direction:
            nx, ny = x + dx, y + dy
            rect.x, rect.y = self.get_cords(nx, ny)
            rect.x += 5
            rect.y += 5

            # Изменяем размер куба на основе синуса
            pulse_scale = 0.7 + 0.23 * math.sin(self.pulse_time)  # Измените амплитуду по желанию
            scaled_size = int(base_size * pulse_scale)

            # Центрируем пульсирующий прямоугольник
            pulse_rect = pygame.Rect(
                rect.centerx - scaled_size // 2,
                rect.centery - scaled_size // 2,
                scaled_size,
                scaled_size
            )

            if current_time - self.last_fight_render_time >= self.fight_render_time_delay:
                pulse_rect.x += 5 - num // 2
                pulse_rect.y += 5 - num // 2

            if 0 <= nx < self.board.width and 0 <= ny < self.board.height:
                if isinstance(self.board.board[ny][nx], Monster):
                    pygame.draw.rect(screen, "RED", pulse_rect)
                elif not isinstance(self.board.board[ny][nx], (Monster, LootChest)):
                    pygame.draw.rect(screen, "GRAY", pulse_rect)  # Цвет пульсации можно изменить

                if self.board.board[ny][nx] != 0:
                    if self.board.board[ny][nx] not in self.radar_list:
                        self.radar_list.append(self.board.board[ny][nx])

        self.last_fight_render_time = current_time

    def get_damage(self, enemy):
        enemy.get_damage(self)
        print('Урон нанесён')
        self.action_count -= 1

    def taking_damage(self, damage):
        if damage <= self.armor:
            self.hp -= 1
        else:
            self.hp -= damage
        if self.hp <= 0:
            self.dead_player()

    def dead_player(self):
        print('Смерть')
        exit()

    def get_self(self):
        return self.__class__

    def __repr__(self):
        return f'{self.__class__.__name__}'
