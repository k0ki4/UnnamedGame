import random

from check_database import check_db
from loot.chest import InfinityChest, ArmorChest
from monsters.monster_logic import *
from player_logic import *
import pygame


class Board:
    def __init__(self, width, height, padding=10):
        self.play = None
        self.width = width
        self.height = height
        self.padding = padding
        # self.background = pygame.image.load('sprites/map/frame.png').convert_alpha()
        # windows_size = pygame.display.get_window_size()
        # self.background = pygame.transform.scale(self.background, (windows_size[0] - 400, windows_size[1]))

        # Вычисляем размер окна
        self.window_size = pygame.display.get_window_size()

        self.grass = pygame.image.load('sprites/map/floor.png').convert_alpha()

        # Вычисляем размер ячейки с учетом отступов
        self.cell_size = (self.window_size[0] - 2 * padding) // self.width
        if (self.cell_size * self.height + 2 * padding) > self.window_size[1]:
            self.cell_size = (self.window_size[1] - 2 * padding) // self.height

        # Инициализация доски
        self.board = [[0] * width for _ in range(height)]
        self.left = padding
        self.top = padding

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

                # Отображаем спрайт, если он существует
                if self.grass:
                    sprite = self.grass
                    sprite = pygame.transform.scale(sprite, (self.cell_size, self.cell_size))  # Изменяем размер спрайта
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

    def on_click(self, cell_coords):
        print(cell_coords)

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    def get_player(self):
        for x in range(self.width):
            for y in range(self.height):
                if isinstance(self.board[y][x], Player):
                    return self.board[y][x]


class Play:
    def __init__(self):
        pygame.init()
        check_db()
        fps = 60
        SIZE = width, height = 1200, 800
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Unnamed Game")
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



    def new_sound(self, path_to_music, duration=None, volume=None):
        music = pygame.mixer.Sound(path_to_music)
        music.set_volume(volume)
        return music

    def new_wave(self):
        self.wave += 1
        self.get_monsters()

    def random_pos(self):
        x = random.randint(0, self.board.width - 1)
        y = random.randint(0, self.board.height - 1)
        if self.board.board[y][x] != 0:
            return self.random_pos()
        return y, x

    def get_monsters(self):
        result_mobs = []
        count = random.randint(2, self.wave + 1)
        monsteres_list = [Slime, Bee, Bat]

        for i in range(count):
            random.shuffle(monsteres_list)
            monster = random.choice(monsteres_list)
            y, x = self.random_pos()
            damage = random.randint(1, 2 * self.wave + self.player.lvl)
            armor = random.randint(1, 2 * self.wave + self.player.lvl)
            hp = random.randint(1, 2 * self.wave + self.player.lvl + 2)
            xp_cost = random.randint(1, 4 + self.player.lvl)
            self.all_monster.append(monster(board=self.board,
                                            hp=hp,
                                            x=x,
                                            y=y,
                                            default_damage=damage,
                                            default_armor=armor))




    def load_menu(self):
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

        self.screen.blit(background_image, background_image_rect)

        # Играть
        self.screen.blit(self.btn_image, new_rect)
        self.screen.blit(text_surface, text_rect)
        # Выйти
        self.screen.blit(self.exit_btn, exit_btn_new_rect)
        self.screen.blit(exit_btn_surface, exit_btn_text_rect)

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

    def fade_in(self, duration):
        fade_surface = pygame.Surface((self.width, self.height))
        fade_surface.fill((0, 0, 0))
        for alpha in range(255, -1, -1):
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(int(duration / 255))

    def old_map(self):
        screen = self.screen
        board = self.board
        board.play = self
        player = self.player

        self.new_wave()

        running = True

        while running:
            self.all_monster = [monster for monster in self.all_monster if not monster.is_dead]
            if player.action_count <= 0:
                [i.attack_damage(player) for i in self.all_monster]
                player.action_count = player.action_const

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not player.inventory.is_open:
                        board.get_cell(event.pos)
                    elif event.button == 1 and player.inventory.is_open:
                        for slot in player.inventory.slots + player.inventory.unic_slot:
                            item = slot.item
                            if item is not None and item.rect.topleft[0] >= 0 and item.rect.topleft[1] >= 0:
                                if item.rect.collidepoint(event.pos):
                                    item.on_click(player)
                                elif item.button_rect.collidepoint(event.pos) and item.open_stats and not item.is_equip:
                                    player.inventory.equip_item(slot)
                                elif item.button_rect.collidepoint(event.pos) and item.open_stats and item.is_equip:
                                    player.inventory.un_equip_item(slot)

                if event.type == pygame.KEYDOWN and not player.inventory.is_open and player.action_count:  # Обработка нажатия клавиш
                    keys = pygame.key.get_pressed()
                    player.update(keys, screen)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_i:  # Открытие инвентаря по нажатию клавиши 'I'
                        player.open_inventory()
            screen.fill((0, 0, 0))
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
            else:
                self.new_wave()

            player.render_stats(screen)  # Рендерим статистику игрока
            player.inventory.draw(screen, player)

            if player.inventory.is_open:
                for slot in player.inventory.slots + player.inventory.unic_slot:
                    item = slot.item
                    if item is not None:
                        item.stats_update(screen)

            self.all_monster = [monster for monster in self.all_monster if not monster.is_dead]



            pygame.display.flip()


        pygame.quit()

    def menu(self):
        running = True

        self.board = Board(10, 10)
        self.player = Player(self.board)

        pygame.mixer.music.load('misc/menu_music/undertale_once.mp3')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.1)

        start_play = False


        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if play.btn_rect.collidepoint(mouse_pos):  # Проверяем, попадает ли курсор в область кнопки
                        start_play = True
                        running = False
                        pygame.mixer.music.stop()
                        play.fade_out(2000)
                        break
                    if play.exit_btn_rect.collidepoint(mouse_pos):  # Проверяем, попадает ли курсор в область кнопки
                        exit()
            play.load_menu()

            pygame.display.flip()
        if start_play:
            self.old_map()


if __name__ == '__main__':
    play = Play()
    play.menu()