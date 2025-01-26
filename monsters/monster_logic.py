import os

import pygame

monster_id = 0


class Monster(pygame.sprite.Sprite):
    def __init__(self, board, *groups, x, y, hp=10, default_damage=1, default_armor=1, xp_cost=10):
        super().__init__(*groups)

        self.id = None
        self.set_id()

        # wave_alg
        self.start, self.goal = False, False

        self.xp_cost = xp_cost

        self.board = board

        self.damaged = False
        self.default_damage = default_damage
        self.default_armor = default_armor
        self.weapon = None
        self.armor = None
        self.damage = None

        self.first_hp = hp
        self.hp = hp
        self.calc_stats()

        self.take_radus_cell = 1

        self.image = pygame.Surface((board.cell_size - 20, board.cell_size - 20))
        self.image.fill("GREEN")
        self.rect = self.image.get_rect()
        self.set_rect(x, y)

        self.last_move_time = 0
        self.move_delay = 0.5

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 13)

        self.is_dead = False

        self.last_update = pygame.time.get_ticks()  # Время последнего обновления кадра
        self.frame_rate = 100  # Задержка между кадрами в миллисекундах
        self.damaged = False  # Состояние получения урона
        self.damage_animation_duration = 500  # Длительность анимации получения урона в миллисекундах
        self.damage_start_time = None  # Время начала анимации получения урона

        self.damaged = False

    def set_id(self):
        global monster_id
        monster_id += 1
        self.id = monster_id
        print(monster_id)

    def is_valid(self, y, x, player):
        # Проверяем, находится ли клетка в пределах поля
        if not (0 <= y < self.board.height and 0 <= x < self.board.width):
            return False

        # Проверяем, является ли клетка проходимой (равна 0) или это клетка с игроком
        return self.board.board[y][x] == 0 or isinstance(self.board.board[y][x], type(player))

    def find_shortest_path(self, start, end, player):

        import heapq
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        # Инициализация
        distances = [[float('inf')] * self.board.width for _ in range(self.board.height)]
        distances[start[0]][start[1]] = 0
        priority_queue = [(0, start)]  # (расстояние, координаты)

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            current_y, current_x = current_node

            print(f"Текущая клетка: {(current_y, current_x)}, расстояние: {current_distance}")

            if current_node == end:
                return distances[end[0]][end[1]]

            if current_distance > distances[current_y][current_x]:
                continue

            for direction in directions:
                neighbor_y = current_y + direction[0]
                neighbor_x = current_x + direction[1]

                if self.is_valid(neighbor_y, neighbor_x, player):
                    new_distance = current_distance + 1

                    if new_distance < distances[neighbor_y][neighbor_x]:
                        distances[neighbor_y][neighbor_x] = new_distance
                        heapq.heappush(priority_queue, (new_distance, (neighbor_y, neighbor_x)))
                        print(f"Добавлено в очередь: {(neighbor_y, neighbor_x)} с расстоянием {new_distance}")
        print("#" * 10)
        return float('inf')  # Если путь не найден

    def set_rect(self, x, y):
        self.rect.x, self.rect.y = (x * self.board.cell_size + self.board.left,
                                    y * self.board.cell_size + self.board.top)
        for i in range(self.board.width):
            for j in range(self.board.height):
                if isinstance(self.board.board[j][i], Monster):
                    if self.board.board[j][i].id == self.id:
                        self.board.board[j][i] = 0
        self.board.board[y][x] = self

    def fight_cell(self, player):
        x, y = self.board.get_cell((self.rect.x, self.rect.y))
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

        for dx, dy in direction:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board.width and 0 <= ny < self.board.height:
                if isinstance(self.board.board[ny][nx], player.get_self()):
                    return True
        return False

    def attack_damage(self, player):
        search_close_player = self.fight_cell(player)

        if search_close_player:
            player.taking_damage(self.damage)
        else:
            x, y = self.board.get_cell((self.rect.x, self.rect.y))
            player_x, player_y = self.board.get_cell((player.rect.x, player.rect.y))
            print(y, x)
            print(player_y, player_x)
            path_to_player = self.find_shortest_path((y, x), (player_y, player_x), player)
            print(1111, path_to_player)
            print(f"Текущая позиция монстра: {(y, x)}, Позиция игрока: {(player_y, player_x)}")
            print(f"Найденный путь: {path_to_player}")
            print("Monster", {self.__repr__()})

            # if path_to_player:
            #     x, y = path_to_player[1]
            #     self.set_rect(x, y)

    def calc_stats(self):
        if self.weapon:
            pass
        else:
            self.armor = self.default_armor
            self.damage = self.default_damage

    def calc_cell(self, cell, action_step):
        pass

    def render_stats(self, screen):
        image = pygame.Surface((150, 20))
        image.fill("BLACK")

        # Вычисляем процент оставшегося здоровья
        health_percentage = self.hp / self.first_hp
        hp_width = int(140 * health_percentage)

        hp_image = pygame.Surface((hp_width, 10))
        hp_image.fill('RED')

        # Отображение текста HP
        hp_text = self.font.render(f'HP: {self.hp}/{self.first_hp}', True, (255, 255, 255))

        # Центрируем элементы на экране
        center_x = self.rect.centerx - 53
        center_y = self.rect.centery - 35

        image_rect = pygame.Rect((center_x, center_y, 150, 20))
        hp_image_rect = pygame.Rect((center_x + 5,
                                     center_y + 5, hp_width, 10))  # Используем hp_width для высоты
        text_width, text_height = hp_text.get_size()
        text_x = image_rect.x + (image_rect.width - text_width) // 2
        text_y = image_rect.y + (image_rect.height - text_height) // 2

        screen.blit(image, image_rect)
        screen.blit(hp_image, hp_image_rect)
        screen.blit(hp_text, (text_x, text_y))

    def get_damage(self, player):
        if self.damaged:
            return
        self.hp -= player.damage
        if self.hp <= 0:
            self.dead(player)
            return

    def dead(self, player):
        self.kill()
        self.is_dead = True
        player.get_xp(self.xp_cost)
        for x in range(len(self.board.board)):
            for y in range(len(self.board.board[x])):
                if self.board.board[x][y] == self:
                    self.board.board[x][y] = 0
                    print('Монстр убит')
                    return True
        return False

    def update(self, keys):
        pass

    def __repr__(self):
        return f'{self.__class__.__name__}'


class Dummy(Monster):
    def __init__(self, board, x, y, sheet=None, columns=None, rows=None, *groups, hp=10, default_damage=1,
                 default_armor=1):
        super().__init__(board, x=x, y=y, *groups, hp=hp, default_damage=default_damage, default_armor=default_armor)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(self.rect.x, self.rect.y, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frame = sheet.subsurface(pygame.Rect(frame_location, self.rect.size))
                scaled_frame = pygame.transform.scale(frame, (self.board.cell_size, self.board.cell_size))
                self.frames.append(scaled_frame)

    def get_damage(self, player):
        if self.damaged:
            return
        self.hp -= player.damage
        if self.hp <= 0:
            self.dead(player)
            return

        if not self.damaged:  # Если не в состоянии получения урона
            self.damaged = True  # Устанавливаем флаг получения урона
            self.damage_start_time = pygame.time.get_ticks()  # Запоминаем время начала анимации

    def update(self, screen):
        current_time = pygame.time.get_ticks()

        if self.damaged:
            # Проверяем, не закончилась ли анимация получения урона
            if current_time - self.damage_start_time < self.damage_animation_duration:
                if current_time - self.last_update > self.frame_rate:  # Проверяем задержку между кадрами
                    self.cur_frame = (self.cur_frame + 1) % len(self.frames)  # Переключаем кадр
                    self.image = self.frames[self.cur_frame]
                    self.last_update = current_time
            else:
                # Заканчиваем анимацию получения урона
                self.damaged = False
                self.cur_frame = 0  # Возвращаемся к первому кадру или другому состоянию
                self.image = self.frames[self.cur_frame]  # Обновляем изображение


class Animated:
    def __init__(self):
        self.frames = []

    def load_frames(self, image_folder):
        # Получаем список всех файлов в папке и сортируем их для правильного порядка
        image_files = sorted(os.listdir(image_folder))

        for image_file in image_files:
            if image_file.endswith('.png'):
                image_path = os.path.join(image_folder, image_file)
                frame = pygame.image.load(image_path).convert_alpha()  # Загружаем изображение
                scaled_frame = pygame.transform.scale(frame, (self.board.cell_size, self.board.cell_size))
                self.frames.append(scaled_frame)  # Добавляем кадр в список


class Slime(Monster, Animated):
    up = './sprites/slime/up'
    right = './spites/slime/right'
    left = './sprites/slime/left'
    down = './sprites/slime/down'

    def __init__(self, board, *groups, x, y):
        super().__init__(board, *groups, x=x, y=y)
        self.frames = []
        self.load_frames(self.down)

        self.frame_rate = 255
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]

    def update(self, screen):
        current_time = pygame.time.get_ticks()
        # Логика для обычной анимации (если есть)
        if current_time - self.last_update > self.frame_rate:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.last_update = current_time
