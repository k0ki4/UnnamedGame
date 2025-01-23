import pygame


class Monster(pygame.sprite.Sprite):
    def __init__(self, board, *groups, x, y, hp=10, default_damage=1, default_armor=1):
        super().__init__(*groups)

        self.board = board

        self.damaged = False
        self.default_damage = default_damage
        self.default_armor = default_armor
        self.weapon = None
        self.armor = None
        self.damage = None
        self.hp = hp
        self.calc_stats()

        self.take_radus_cell = 1

        self.image = pygame.Surface((board.cell_size - 20, board.cell_size - 20))
        self.image.fill("GREEN")
        self.rect = self.image.get_rect()  # Получаем прямоугольник для спрайта
        self.set_rect(x, y)

        self.last_move_time = 0  # Время последнего движения
        self.move_delay = 0.5  # Задержка в секундах

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 15)


    def set_rect(self, x, y):
        self.rect.x, self.rect.y = (x * self.board.cell_size + self.board.left,
                                    y * self.board.cell_size + self.board.top)
        self.board.board[y][x] = self
        for i in self.board.board:
            print(i)
        print()

    def calc_stats(self):
        if self.weapon:
            pass
        else:
            self.armor = self.default_armor
            self.damage = self.default_damage

    def calc_cell(self, cell, action_step):
        pass

    def render_stats(self, screen):
        pass

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


        self.last_update = pygame.time.get_ticks()  # Время последнего обновления кадра
        self.frame_rate = 100  # Задержка между кадрами в миллисекундах
        self.damaged = False  # Состояние получения урона
        self.damage_animation_duration = 500  # Длительность анимации получения урона в миллисекундах
        self.damage_start_time = None  # Время начала анимации получения урона

        self.damaged = False

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(self.rect.x, self.rect.y, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frame = sheet.subsurface(pygame.Rect(frame_location, self.rect.size))
                scaled_frame = pygame.transform.scale(frame, (self.board.cell_size, self.board.cell_size))
                self.frames.append(scaled_frame)


    def get_damage(self):
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

        else:
            # Логика для обычной анимации (если есть)
            if current_time - self.last_update > self.frame_rate:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
                self.last_update = current_time