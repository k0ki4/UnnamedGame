import math
import random
import time
import pygame

from inventory_logic import Inventory, EquipItemSlot, HelmetSlot, ChestplateSlot, LeggingsSlot, AccessoriesItemSlot
from loot.chest import LootChest
from monsters.monster_logic import Monster


class Player(pygame.sprite.Sprite):
    down = 'sprites/player/frisk_down.png'
    up = 'sprites/player/frisk_up.png'
    left = 'sprites/player/frisk_left.png'
    right = 'sprites/player/frisk_right.png'

    def __init__(self, board, *groups, hp=10, default_damage=1, default_armor=1):
        super().__init__(*groups)
        self.board = board
        self.screen = None

        self.inventory = Inventory(self)

        self.radar_list = []
        self.radar_img = None

        self.lvl = 1
        self.xp = 0
        self.xp_for_next = 10

        self.default_damage = default_damage
        self.default_armor = default_armor
        self.armor = 0
        self.damage = 0
        self.max_hp = hp
        self.hp = hp
        self.action_const = 3
        self.action_count = 3

        self.need_load = self.down
        self.image = pygame.image.load(self.need_load).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.board.cell_size, self.board.cell_size))
        self.rect = self.image.get_rect()

        self.board.board[0][0] = self
        self.rect.x, self.rect.y = 0 * board.cell_size + board.left, 0 * board.cell_size + board.top

        self.fight_mode = False

        self.last_move_time = 0
        self.move_delay = 0.25

        self.pulse_time = 0

        self.last_fight_render_time = 0
        self.fight_render_time_delay = 0.5

        pygame.font.init()
        self.font = pygame.font.Font('misc/font_ttf/Undertale-Battle-Font.ttf', 14)
        self.large_font = pygame.font.Font('misc/font_ttf/Undertale-Battle-Font.ttf', 25)

        self.monster_image = pygame.image.load("sprites/inventory/enemy_cell.png").convert_alpha()
        self.normal_image = pygame.image.load("sprites/inventory/empty_cell.png").convert_alpha()

        self.is_dead = False

        # sound
        self.step = pygame.mixer.Sound('misc/sound_effect/action_move.wav')
        self.step.set_volume(0.05)
        self.level_up = pygame.mixer.Sound('misc/sound_effect/player_lvl_up2.wav')
        self.level_up.set_volume(0.5)
        self.hit_sound = pygame.mixer.Sound('misc/sound_effect/hit_damage.mp3')
        self.hit_sound.set_volume(0.5)
        self.hit_self = pygame.mixer.Sound('misc/sound_effect/Hit_player.wav')
        self.hit_self.set_volume(0.7)

    def get_xp(self, count):
        self.xp += count
        if self.xp >= self.xp_for_next:
            self.xp -= self.xp_for_next
            self.lvl += 1
            self.xp_for_next += 5
            self.level_up.play()

    def calc_stats(self):
        self.damage = 0
        self.armor = 0
        self.max_hp = 10
        self.damage += self.default_damage
        self.armor += self.default_armor
        equip_weapon = [slot.item.damage for slot in self.inventory.unic_slot if
                        slot.item is not None and isinstance(slot, EquipItemSlot)]
        equip_armor = [slot.item.protect for slot in self.inventory.unic_slot if slot.item is not None and
                       isinstance(slot, (HelmetSlot, ChestplateSlot, LeggingsSlot))]
        equip_acs = [slot.item.buff_hp for slot in self.inventory.unic_slot if slot.item is not None and
                     isinstance(slot, AccessoriesItemSlot)]
        if equip_armor:
            self.armor += sum(equip_armor)
        if equip_weapon:
            self.damage += sum(equip_weapon)
        if equip_acs:
            self.max_hp += sum(equip_acs)
        self.damage += self.lvl
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def calc_cell(self, cell, action_step):
        x, y = cell
        if not (0 <= x + action_step[0] < self.board.width and 0 <= y + action_step[1] < self.board.height):
            return x, y
        if self.board.board[y + action_step[1]][x + action_step[0]] != 0:
            return x, y
        self.board.board[y][x] = 0
        self.action_count -= 1
        return x + action_step[0], y + action_step[1]

    def render_health(self, screen):
        health_image = pygame.image.load('sprites/gui/health.png').convert_alpha()
        health_image_rect = pygame.Rect(825, 80, 350, 25)
        health_image = pygame.transform.scale(health_image, (health_image_rect.width, health_image_rect.height))

        health_percentage = self.hp / self.max_hp
        red_health_width = int(300 * health_percentage)

        red_health_surface = pygame.Surface((red_health_width, health_image_rect.height))
        red_health_surface.fill((255, 0, 0))

        health_text = f"ХП: {self.hp}/{self.max_hp}"
        text_surface = self.font.render(health_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(health_image_rect.centerx, health_image_rect.centery))
        screen.blit(red_health_surface, (health_image_rect.x + 25, health_image_rect.y))
        screen.blit(health_image, health_image_rect)
        screen.blit(text_surface, text_rect)

    def render_experience(self, screen):
        experience_image = pygame.image.load('sprites/gui/health.png').convert_alpha()
        experience_image_rect = pygame.Rect(825, 120, 350, 25)
        experience_image = pygame.transform.scale(experience_image,
                                                  (experience_image_rect.width, experience_image_rect.height))

        experience_percentage = self.xp / self.xp_for_next
        if experience_percentage > 1:
            experience_percentage = 1

        green_experience_width = int(300 * experience_percentage)

        green_experience_surface = pygame.Surface((green_experience_width, experience_image_rect.height))
        green_experience_surface.fill((0, 255, 0))

        experience_text = f"Опыт: {self.xp}/{self.xp_for_next}"
        text_surface = self.font.render(experience_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(experience_image_rect.centerx, experience_image_rect.centery))

        screen.blit(green_experience_surface, (experience_image_rect.x + 25, experience_image_rect.y))
        screen.blit(experience_image, experience_image_rect)
        screen.blit(text_surface, text_rect)

    def lvl_render(self, screen):
        lvl_image = pygame.image.load('sprites/gui/stats.png').convert_alpha()
        lvl_image_rect = pygame.Rect(825, 200, 50, 50)
        lvl_image = pygame.transform.scale(lvl_image, (lvl_image_rect.width,
                                                       lvl_image_rect.height))

        lvl_text = self.large_font.render(f'Ур: {self.lvl}', True, 'WHITE')
        screen.blit(lvl_image, lvl_image_rect)
        screen.blit(lvl_text, (880, 210, 50, 50))

        step_image = pygame.image.load('sprites/gui/step_c.png').convert_alpha()
        step_image_rect = pygame.Rect(825, 270, 50, 50)
        step_image = pygame.transform.scale(step_image, (step_image_rect.width,
                                                         step_image_rect.height))

        step_text = self.large_font.render(f'Ходов: {self.action_count}', True, 'WHITE')
        screen.blit(step_image, step_image_rect)
        screen.blit(step_text, (880, 280, 50, 50))

    def damage_protect_render(self, screen):
        damage_image = pygame.image.load('sprites/gui/stats.png').convert_alpha()
        damage_image_rect = pygame.Rect(825, 340, 50, 50)
        damage_image = pygame.transform.scale(damage_image, (damage_image_rect.width,
                                                             damage_image_rect.height))

        protect_image = pygame.image.load('sprites/gui/stats.png').convert_alpha()
        protect_image_rect = pygame.Rect(825, 410, 50, 50)
        protect_image = pygame.transform.scale(protect_image, (protect_image_rect.width,
                                                               protect_image_rect.height))

        damage_text = self.large_font.render(f'Урон: {self.damage}', True, 'WHITE')
        protect_text = self.large_font.render(f'Зщ: {self.armor}', True, 'WHITE')

        screen.blit(damage_image, damage_image_rect)
        screen.blit(protect_image, protect_image_rect)

        screen.blit(damage_text, (880, 350, 50, 50))
        screen.blit(protect_text, (880, 420, 50, 50))

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

        take_img = pygame.image.load("sprites/gui/use.png").convert_alpha()
        take_img = pygame.transform.scale(take_img, (60, 60))
        take_img_rect = pygame.Rect(845, 500, 60, 60)
        screen.blit(take_img, take_img_rect)

        start_fight = pygame.image.load("sprites/gui/use.png").convert_alpha()
        start_fight = pygame.transform.scale(start_fight, (60, 60))
        start_fight_rect = pygame.Rect(845, 600, 60, 60)
        screen.blit(start_fight, start_fight_rect)

        start_fight_text = self.font.render("Провести атаку", True, (255, 255, 255))
        start_fight_text_2 = self.font.render("R", True, (255, 255, 255))
        screen.blit(start_fight_text, (830, 580))

        text_width, text_height = start_fight_text_2.get_size()
        text_x = start_fight_rect.x + (start_fight_rect.width - text_width) // 2
        text_y = start_fight_rect.y + (start_fight_rect.height - text_height) // 2
        screen.blit(start_fight_text_2, (text_x, text_y))

        open_inventory = pygame.image.load("sprites/gui/use.png").convert_alpha()
        open_inventory = pygame.transform.scale(open_inventory, (60, 60))
        open_inventory_rect = pygame.Rect(845, 700, 60, 60)
        screen.blit(open_inventory, open_inventory_rect)

        open_inventory_text = self.font.render("Открыть инвентарь", True, (255, 255, 255))
        open_inventory_text_button = self.font.render("I", True, (255, 255, 255))
        screen.blit(open_inventory_text, (830, 680))

        text_width, text_height = open_inventory_text_button.get_size()
        text_x = open_inventory_rect.x + (open_inventory_rect.width - text_width) // 2
        text_y = open_inventory_rect.y + (open_inventory_rect.height - text_height) // 2
        screen.blit(open_inventory_text_button, (text_x, text_y))

        take_text_take = self.font.render("Взаимодействовать", True, (255, 255, 255))
        take_text = self.font.render("E", True, (255, 255, 255))
        screen.blit(take_text_take, (830, 480))
        if self.radar_list:
            for i in self.radar_list:
                if isinstance(i, LootChest):
                    text_width, text_height = take_text.get_size()
                    text_x = take_img_rect.x + (take_img_rect.width - text_width) // 2
                    text_y = take_img_rect.y + (take_img_rect.height - text_height) // 2
                    screen.blit(take_text, (text_x, text_y))

        self.lvl_render(screen)
        self.damage_protect_render(screen)
        self.render_health(screen)
        self.render_experience(screen)

        self.count_usage()

    def update_direction(self, direction):
        if direction == (-1, 0):  # Вверх
            self.need_load = self.up
        elif direction == (1, 0):  # Вниз
            self.need_load = self.down
        elif direction == (0, -1):  # Влево
            self.need_load = self.left
        elif direction == (0, 1):  # Вправо
            self.need_load = self.right
        self.image = pygame.image.load(self.need_load).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.board.cell_size, self.board.cell_size))

    def update(self, keys, screen):
        self.screen = screen
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
                self.step.play()
                self.update_direction((-1, 0))
            if keys[pygame.K_s]:
                x, y = self.calc_cell((self.rect.x // self.board.cell_size, self.rect.y // self.board.cell_size),
                                      (0, 1))
                self.board.board[y][x] = self
                self.rect.x, self.rect.y = (x * self.board.cell_size + self.board.left,
                                            y * self.board.cell_size + self.board.top)
                self.step.play()
                self.update_direction((1, 0))

            if keys[pygame.K_a]:
                x, y = self.calc_cell((self.rect.x // self.board.cell_size, self.rect.y // self.board.cell_size),
                                      (-1, 0))
                self.board.board[y][x] = self
                self.rect.x, self.rect.y = (x * self.board.cell_size + self.board.left,
                                            y * self.board.cell_size + self.board.top)
                self.step.play()
                self.update_direction((0, -1))

            if keys[pygame.K_d]:
                x, y = self.calc_cell((self.rect.x // self.board.cell_size, self.rect.y // self.board.cell_size),
                                      (1, 0))
                self.board.board[y][x] = self
                self.rect.x, self.rect.y = (x * self.board.cell_size + self.board.left,
                                            y * self.board.cell_size + self.board.top)
                self.step.play()
                self.update_direction((0, 1))

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
        self.radar_list = [monster for monster in self.radar_list if isinstance(monster, Monster)]
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
        base_size = self.board.cell_size - 10
        rect = pygame.Rect(0, 0, base_size, base_size)

        x, y = self.get_cell((self.rect.x, self.rect.y))
        direction = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (1, 0),
            (1, -1),
            (1, 1),
            (0, -1),
            (0, 1)
        ]

        self.pulse_time += 0.05

        for dx, dy in direction:
            nx, ny = x + dx, y + dy
            rect.x, rect.y = self.get_cords(nx, ny)
            rect.x += 5
            rect.y += 5

            pulse_scale = 0.7 + 0.23 * math.sin(self.pulse_time)
            scaled_width = int(base_size * pulse_scale)
            scaled_height = int(base_size * pulse_scale)

            if 0 <= nx < self.board.width and 0 <= ny < self.board.height:
                if isinstance(self.board.board[ny][nx], Monster):
                    scaled_image = pygame.transform.scale(self.monster_image, (scaled_width, scaled_height))
                    pulse_rect = scaled_image.get_rect(center=rect.center)

                    if current_time - self.last_fight_render_time >= self.fight_render_time_delay:
                        pulse_rect.x += 5 - num // 2
                        pulse_rect.y += 5 - num // 2
                    screen.blit(scaled_image, pulse_rect)
                elif (not isinstance(self.board.board[ny][nx], (Monster, LootChest)) and
                      self.board.board[ny][nx] != 'box'):
                    scaled_image = pygame.transform.scale(self.normal_image, (scaled_width, scaled_height))
                    pulse_rect = scaled_image.get_rect(center=rect.center)

                    if current_time - self.last_fight_render_time >= self.fight_render_time_delay:
                        pulse_rect.x += 5 - num // 2
                        pulse_rect.y += 5 - num // 2
                    screen.blit(scaled_image, pulse_rect)

                if self.board.board[ny][nx] != 0:
                    if self.board.board[ny][nx] not in self.radar_list:
                        self.radar_list.append(self.board.board[ny][nx])

        self.last_fight_render_time = current_time

    def get_damage(self, enemy):
        res = enemy.take_damage(self)
        if res is not None:
            self.hit_sound.play()
            self.action_count -= 1
            return res

    def taking_damage(self, damage):
        if damage <= self.armor:
            self.hp -= 1
            self.hit_self.play()
        elif damage > self.armor:
            self.hp -= (damage - self.armor)
            self.hit_self.play()
        if self.hp <= 0:
            self.hp = 0
            self.dead_player()

    def dead_player(self):
        play = self.board.get_play()
        play.end_game = True

    def get_board(self):
        return self.board

    def get_screen(self):
        return self.screen

    def get_self(self):
        return self.__class__

    def __repr__(self):
        return f'{self.__class__.__name__}'
