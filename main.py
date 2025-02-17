import random
import sys
import time
import sqlite3

from check_database import check_db

check_db()
from loot.chest import InfinityChest, ArmorChest
from monsters.monster_logic import *
from player_logic import *
import pygame

from potions.potion_logic import Potion


class Board:
    def __init__(self, width, height, padding=10):
        self.play = None
        self.width = width
        self.height = height
        self.padding = padding

        self.window_size = pygame.display.get_window_size()

        self.grass = pygame.image.load('sprites/map/floor.png').convert_alpha()
        self.box = pygame.image.load('sprites/map/box.png').convert_alpha()
        self.count_box = random.randint(5, 10)

        # Вычисляем размер ячейки с учетом отступов
        self.cell_size = (self.window_size[0] - 2 * padding) // self.width
        if (self.cell_size * self.height + 2 * padding) > self.window_size[1]:
            self.cell_size = (self.window_size[1] - 2 * padding) // self.height

        # Инициализация доски
        self.board = [[0] * width for _ in range(height)]
        self.set_box()
        self.left = padding
        self.top = padding

    def set_box(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.board[y][x] == 'box':
                    self.board[y][x] = 0
        for i in range(self.count_box):
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            if self.board[x][y] == 0:
                self.board[x][y] = 'box'

    def get_play(self):
        return self.play

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        color = ["white", "#403a3a", (255, 255, 255)]
        for x in range(self.width):
            for y in range(self.height):

                if self.grass:
                    sprite = self.grass
                    sprite = pygame.transform.scale(sprite, (self.cell_size, self.cell_size))
                    screen.blit(sprite, (x * self.cell_size + self.left, y * self.cell_size + self.top))

                if self.box and self.board[y][x] == 'box':
                    sprite = self.box
                    sprite = pygame.transform.scale(sprite, (self.cell_size, self.cell_size))
                    screen.blit(sprite, (x * self.cell_size + self.left, y * self.cell_size + self.top))

                pygame.draw.rect(
                    screen, color[1],
                    (x * self.cell_size + self.left, y * self.cell_size + self.top,
                     self.cell_size, self.cell_size), 1
                )

    def get_cell(self, mouse_pos):
        player = self.get_player()
        cell_x = (mouse_pos[0] - self.left) // self.cell_size
        cell_y = (mouse_pos[1] - self.top) // self.cell_size
        if 0 <= cell_x <= self.width and 0 <= cell_y <= self.height:
            if player.fight_mode and isinstance(self.board[cell_y][cell_x], (Monster,)) and self.board[cell_y][
                cell_x] in player.radar_list:
                player.get_damage(self.board[cell_y][cell_x])

            return cell_x, cell_y
        return None

    def fight_click(self, mouse_pos):
        player = self.get_player()
        cell_x = (mouse_pos[0] - self.left) // self.cell_size
        cell_y = (mouse_pos[1] - self.top) // self.cell_size
        if 0 <= cell_x <= self.width and 0 <= cell_y <= self.height:
            if player.fight_mode and isinstance(self.board[cell_y][cell_x], (Monster,)) and self.board[cell_y][
                cell_x] in player.radar_list:
                text = player.get_damage(self.board[cell_y][cell_x])
                return text

    def on_click(self, cell_coords):
        print(cell_coords)

    def get_player(self):
        for x in range(self.width):
            for y in range(self.height):
                if isinstance(self.board[y][x], Player):
                    return self.board[y][x]


class Play:
    def __init__(self):
        pygame.init()
        check_db()
        self.SIZE = width, height = 1200, 800
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Unnamed Game")
        icon = pygame.image.load('misc/icon.png')
        pygame.display.set_icon(icon)

        self.screen = screen
        self.board = None
        self.player = None

        self.width, self.height = 1200, 800

        self.font = pygame.font.Font(None, 36)
        self.und_font = pygame.font.Font('misc/font_ttf/Undertale-Battle-Font.ttf', 46)
        self.und_large_font = pygame.font.Font('misc/font_ttf/Undertale-Battle-Font.ttf', 80)

        self.amplitude = 20  # Максимальное смещение от центра
        self.speed = 0.0015  # Скорость анимации
        self.start_time = pygame.time.get_ticks()

        # Посхалка Owl
        self.owl_sound_last = 0
        self.sound_cooldown = 60000

        # button menu
        self.btn_image = pygame.image.load('sprites/menu/green_btn.png').convert_alpha()
        self.btn_rect = self.btn_image.get_rect(center=(self.width // 2, self.height // 2))

        self.exit_btn = pygame.image.load('sprites/menu/red_btn.png').convert_alpha()
        self.exit_btn_rect = self.exit_btn.get_rect(center=(self.width // 2, self.height // 2 + 130))

        # Параметры для наклона текста
        self.amplitude_name_game = 10  # Максимальный угол наклона
        self.speed_name_game = 0.0015  # Скорость анимации

        self.name_game_surface = self.und_large_font.render('UNNAMED GAME', True, (255, 255, 255))
        self.name_game_surface_rect = self.name_game_surface.get_rect(center=(self.width // 2, self.height // 2 - 200))

        # StartPlay
        self.wave = 0
        self.old_chest = []
        self.all_monster = []
        self.chest_sps = []
        self.backend_sound = pygame.mixer.Sound('misc/menu_music/undertale_core.mp3')
        self.backend_sound.set_volume(0.1)
        self.end_game = False

    def render_wave(self):
        count_wave = self.und_font.render(f'Волна {self.board.play.wave}', True, 'WHITE')
        self.screen.blit(count_wave, (920, 10, 20, 10))

    def new_wave(self, use_anim=False):
        pygame.mixer.pause()
        for i in self.chest_sps:
            i.delete()
        self.chest_sps = []
        self.wave += 1
        self.get_monsters()
        self.get_chest()
        if use_anim:
            self.animate_wave_text()
        self.board.set_box()
        self.player.hp = self.player.max_hp
        pygame.mixer.unpause()

    def animate_wave_text(self):
        text = self.font.render(f"Волна {self.wave}", True, (255, 255, 255))
        text_scale = 1.0
        scale_speed = 0.02
        max_scale = 4.5
        clock = pygame.time.Clock()

        background_image = pygame.image.load('sprites/map/wave_change.jpg').convert_alpha()
        background_image = pygame.transform.scale(background_image, (self.width, self.height))
        background_image_rect = background_image.get_rect()

        wave_sound = pygame.mixer.Sound('misc/sound_effect/wave_change_3.wav')
        wave_sound.set_volume(0.1)
        wave_sound.play()

        running = True
        while running:

            text_scale += scale_speed

            if text_scale >= max_scale:
                text_scale = max_scale
                running = False

            self.screen.blit(background_image, background_image_rect)

            scaled_text = pygame.transform.scale(text,
                                                 (int(text.get_width() * text_scale),
                                                  int(text.get_height() * text_scale)))

            text_rect = scaled_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(scaled_text, text_rect)

            pygame.display.flip()
            clock.tick(60)

        wave_sound.stop()

    def random_pos(self):
        x = random.randint(0, self.board.width - 1)
        y = random.randint(0, self.board.height - 1)
        if self.board.board[y][x] != 0:
            return self.random_pos()
        return y, x

    def get_monsters(self):
        count = random.randint(2, self.wave + 1)
        monsteres_list = [Slime, Bee, Bat]

        for i in range(count):
            random.shuffle(monsteres_list)
            monster = random.choice(monsteres_list)
            y, x = self.random_pos()
            damage = random.randint(4, 6 * self.wave + self.player.lvl)
            armor = random.randint(4, 6 * self.wave + self.player.lvl)
            hp = random.randint(10, 7 * self.wave + self.player.lvl + 2)
            xp_cost = random.randint(1, 6 + self.player.lvl)
            result_monster = monster(board=self.board,
                                     hp=hp,
                                     xp_cost=xp_cost,
                                     x=x,
                                     y=y,
                                     default_damage=damage,
                                     default_armor=armor)
            result_monster.random_move_chance = random.uniform(0.0, 0.5)
            self.all_monster.append(result_monster)

    def get_chest(self):
        count = len(self.all_monster)
        chest_list = [LootChest]

        for i in range(count):
            random.shuffle(chest_list)
            chest = random.choice(chest_list)
            y, x = self.random_pos()
            rarity = random.randint(1, 3)
            self.chest_sps.append(chest(board=self.board,
                                        x=x,
                                        y=y,
                                        rarity=rarity))

    def load_menu(self):
        current_time = pygame.time.get_ticks()
        sound = pygame.mixer.Sound('misc/menu_music/owl.wav')
        sound.set_volume(0.1)

        if random.random() < 0.001 and (current_time - self.owl_sound_last) > self.sound_cooldown:
            sound.play()
            self.owl_sound_last = current_time

        background_image = pygame.image.load('sprites/menu/background.png').convert_alpha()
        background_image = pygame.transform.scale(background_image, (self.width, self.height))
        background_image_rect = background_image.get_rect()

        elapsed_time = pygame.time.get_ticks() - self.start_time
        offset = self.amplitude * math.sin(elapsed_time * self.speed)

        text_surface = self.und_font.render('Играть', True, (255, 255, 255))  # Белый цвет текста
        text_rect = text_surface.get_rect(center=self.btn_rect.center)  # Центрируем текст на кнопке
        new_rect = self.btn_rect.move(0, offset)
        text_rect.center = new_rect.center

        exit_btn_surface = self.und_font.render('Выход', True, (255, 255, 255))  # Белый цвет текста
        exit_btn_text_rect = exit_btn_surface.get_rect(center=self.exit_btn_rect.center)  # Центрируем текст на кнопке
        exit_btn_new_rect = self.exit_btn_rect.move(0, offset)
        exit_btn_text_rect.center = exit_btn_new_rect.center

        # Наклон текста
        angle = self.amplitude_name_game * math.sin(elapsed_time * self.speed_name_game)
        rotated_new_text_surface = pygame.transform.rotate(self.name_game_surface, angle)
        rotated_new_text_rect = rotated_new_text_surface.get_rect(center=self.name_game_surface_rect.center)

        best_wave_text = self.font.render(f'Лучшая волна: {self.get_best_wave()}', True, 'WHITE')
        best_wave_text_rect = pygame.Rect((600, 620, 70, 70))
        self.screen.blit(background_image, background_image_rect)

        # Играть
        self.screen.blit(self.btn_image, new_rect)
        self.screen.blit(text_surface, text_rect)
        # Выйти
        self.screen.blit(self.exit_btn, exit_btn_new_rect)
        self.screen.blit(exit_btn_surface, exit_btn_text_rect)
        # Макс Волна
        self.screen.blit(best_wave_text, best_wave_text_rect)

        # Название игры
        self.screen.blit(rotated_new_text_surface, rotated_new_text_rect)

    def fade_out(self, duration):
        fade_surface = pygame.Surface((self.width, self.height))
        fade_surface.fill((0, 0, 0))
        for alpha in range(0, 255):
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(int(duration / 255))

    def get_best_wave(self):
        with sqlite3.connect('database.db') as db:
            cursor = db.cursor()
            cursor.execute('SELECT best_wave FROM player')
            best_wave = cursor.fetchone()[0]
            db.commit()
            return best_wave

    def update_best_wave(self):
        with sqlite3.connect('database.db') as db:
            cursor = db.cursor()
            cursor.execute('SELECT best_wave FROM player')
            best_wave = cursor.fetchone()[0]
            if self.wave > best_wave:
                cursor.execute('UPDATE player SET best_wave = ?', (self.wave,))
                db.commit()

    def end_games(self):
        frame = pygame.image.load("sprites/gui/gui.png")
        frame_2 = pygame.image.load("sprites/gui/gui_2.png")
        frame_rect = pygame.Rect((200, 100, 400, 300))
        frame = pygame.transform.scale(frame, (frame_rect.width, frame_rect.height))
        frame_2 = pygame.transform.scale(frame_2, (frame_rect.width, frame_rect.height))

        continue_button_rect = pygame.Rect(220, 250, 350, 50)
        exit_button_rect = pygame.Rect(220, 320, 350, 50)
        continue_button = pygame.image.load("sprites/menu/green_btn.png")
        exit_button = pygame.image.load("sprites/menu/red_btn.png")
        continue_button = pygame.transform.scale(continue_button,
                                                 (continue_button_rect.width, continue_button_rect.height))
        exit_button = pygame.transform.scale(exit_button, (exit_button_rect.width, exit_button_rect.height))

        pause_text = self.font.render("Вы погибли", True, 'WHITE')
        wave_text = self.font.render(f"Волна: {self.wave}", True, 'WHITE')

        self.screen.blit(frame, frame_rect)
        self.screen.blit(frame_2, frame_rect)

        self.screen.blit(continue_button, continue_button_rect)
        self.screen.blit(exit_button, exit_button_rect)

        self.screen.blit(pause_text, pygame.Rect(285, 140, 350, 50))
        self.screen.blit(wave_text, pygame.Rect(285, 160, 350, 50))

        continue_text = self.font.render('В меню', True, (255, 255, 255))
        exit_text = self.font.render('Выйти', True, (255, 255, 255))

        text_width, text_height = continue_text.get_size()
        text_x = continue_button_rect.x + (continue_button_rect.width - text_width) // 2
        text_y = continue_button_rect.y + (continue_button_rect.height - text_height) // 2
        self.screen.blit(continue_text, (text_x, text_y))

        text_width, text_height = exit_text.get_size()
        text_x = exit_button_rect.x + (exit_button_rect.width - text_width) // 2
        text_y = exit_button_rect.y + (exit_button_rect.height - text_height) // 2
        self.screen.blit(exit_text, (text_x, text_y))

        self.update_best_wave()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos

                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    if continue_button_rect.collidepoint(mouse_pos):
                        return True

                    if exit_button_rect.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

            pygame.display.flip()

    def pause(self):
        frame = pygame.image.load("sprites/gui/gui.png")
        frame_2 = pygame.image.load("sprites/gui/gui_2.png")
        frame_rect = pygame.Rect((200, 100, 400, 300))
        frame = pygame.transform.scale(frame, (frame_rect.width, frame_rect.height))
        frame_2 = pygame.transform.scale(frame_2, (frame_rect.width, frame_rect.height))

        continue_button_rect = pygame.Rect(220, 250, 350, 50)
        exit_button_rect = pygame.Rect(220, 320, 350, 50)
        continue_button = pygame.image.load("sprites/menu/green_btn.png")
        exit_button = pygame.image.load("sprites/menu/red_btn.png")
        continue_button = pygame.transform.scale(continue_button,
                                                 (continue_button_rect.width, continue_button_rect.height))
        exit_button = pygame.transform.scale(exit_button, (exit_button_rect.width, exit_button_rect.height))

        pause_text = self.und_large_font.render("Пауза", True, 'WHITE')

        self.screen.blit(frame, frame_rect)
        self.screen.blit(frame_2, frame_rect)

        self.screen.blit(continue_button, continue_button_rect)
        self.screen.blit(exit_button, exit_button_rect)

        self.screen.blit(pause_text, pygame.Rect(285, 140, 350, 50))

        continue_text = self.font.render('Продолжить', True, (255, 255, 255))
        exit_text = self.font.render('Выйти', True, (255, 255, 255))

        text_width, text_height = continue_text.get_size()
        text_x = continue_button_rect.x + (continue_button_rect.width - text_width) // 2
        text_y = continue_button_rect.y + (continue_button_rect.height - text_height) // 2
        self.screen.blit(continue_text, (text_x, text_y))

        text_width, text_height = exit_text.get_size()
        text_x = exit_button_rect.x + (exit_button_rect.width - text_width) // 2
        text_y = exit_button_rect.y + (exit_button_rect.height - text_height) // 2
        self.screen.blit(exit_text, (text_x, text_y))

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_ESCAPE]:
                        return False

                if continue_button_rect.collidepoint(mouse_pos):
                    return False

                if exit_button_rect.collidepoint(mouse_pos):
                    return True

    def main_game(self):
        screen = self.screen
        board = self.board
        board.play = self
        player = self.player
        self.new_wave()
        self.backend_sound.play(-1)
        damage_texts = []
        clock = pygame.time.Clock()
        running = True
        pause = False
        while running:
            if self.end_game is True:
                break
            dt = clock.tick(60) / 1000
            self.all_monster = [monster for monster in self.all_monster if not monster.is_dead]

            if not self.all_monster and all([ch.is_open for ch in self.chest_sps]):
                self.new_wave(use_anim=True)

            if player.action_count <= 0:
                [i.attack_damage(player) for i in self.all_monster]
                player.action_count = player.action_const

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and not pause:
                    if event.button == 1 and not player.inventory.is_open:
                        new_text_damage = board.fight_click(event.pos)
                        if new_text_damage:
                            damage_texts.append(new_text_damage)
                    elif event.button == 1 and player.inventory.is_open:
                        for slot in player.inventory.slots + player.inventory.unic_slot:
                            item = slot.item
                            if item is not None and item.rect.topleft[0] >= 0 and item.rect.topleft[1] >= 0:
                                if item.rect.collidepoint(event.pos):
                                    item.on_click(player)
                                elif item.button_rect.collidepoint(event.pos) and item.open_stats and not item.is_equip:
                                    player.inventory.equip_item(slot)
                                elif not isinstance(item, Potion) and not item.is_equip:
                                    if item.drop_button_rect.collidepoint(
                                            event.pos) and item.open_stats and not item.is_equip:
                                        player.inventory.drop(slot)
                                elif item.button_rect.collidepoint(event.pos) and item.open_stats and item.is_equip:
                                    player.inventory.un_equip_item(slot)

                if event.type == pygame.KEYDOWN and not player.inventory.is_open and player.action_count and not pause:
                    keys = pygame.key.get_pressed()
                    player.update(keys, screen)

                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_ESCAPE]:
                        pause = not pause

                if event.type == pygame.KEYDOWN and not pause:
                    if event.key == pygame.K_i:  # Открытие инвентаря по нажатию клавиши 'I'
                        player.open_inventory()

            self.screen.fill('#32221a')
            board.render(screen)

            if player.fight_mode:
                player.fight_cell(screen)

            screen.blit(player.image, player.rect)
            for chest in self.chest_sps:
                screen.blit(chest.image, chest.rect)

            if self.all_monster:
                for i in self.all_monster:
                    i.update(screen)
                for i in self.all_monster:
                    if not i.is_dead:
                        screen.blit(i.image, i.rect)
                        i.render_stats(screen)

            for text in damage_texts[:]:
                text.update(dt)
                text.draw(screen)
                if text.alpha <= 0:
                    damage_texts.remove(text)

            player.render_stats(screen)
            player.inventory.draw(screen, player)
            self.render_wave()

            if player.inventory.is_open:
                for slot in player.inventory.slots + player.inventory.unic_slot:
                    item = slot.item
                    if item is not None:
                        item.stats_update(screen)

            self.all_monster = [monster for monster in self.all_monster if not monster.is_dead]

            if pause:
                res = self.pause()
                if res is False:
                    pause = False
                if res is True:
                    running = False
            pygame.display.flip()

        if pause:
            pygame.mixer.stop()
            self.menu()
        if self.end_game:
            res = self.end_games()
            if res is True:
                pygame.mixer.stop()
                self.menu()

    def menu(self):
        running = True
        self.end_game = False
        self.all_monster = []
        self.chest_sps = []
        self.wave = 0

        self.board = Board(10, 10)
        self.player = Player(self.board)

        pygame.mixer.music.load('misc/menu_music/undertale_once.mp3')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.1)

        start_play = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if play.btn_rect.collidepoint(mouse_pos):
                        start_play = True
                        running = False
                        pygame.mixer.music.stop()
                        play.fade_out(2000)
                        break
                    if play.exit_btn_rect.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

            play.load_menu()

            pygame.display.flip()
        if start_play:
            self.main_game()


if __name__ == '__main__':
    play = Play()
    play.menu()
