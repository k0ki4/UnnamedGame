import pygame


class Monster(pygame.sprite.Sprite):
    def __init__(self, board, *groups, hp=10, default_damage=1, default_armor=1):
        super().__init__(*groups)
        self.board = board

        self.default_damage = default_damage
        self.default_armor = default_armor
        self.weapon = None
        self.armor = None
        self.damage = None
        self.hp = hp
        self.calc_stats()

        self.image = pygame.Surface((board.cell_size, board.cell_size))
        self.image.fill("RED")
        self.rect = self.image.get_rect()  # Получаем прямоугольник для спрайта
        self.rect.x, self.rect.y = 0 * board.cell_size + board.left, 0 * board.cell_size + board.top

        self.last_move_time = 0  # Время последнего движения
        self.move_delay = 0.5  # Задержка в секундах

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 15)

    def set_rect(self, x, y):
        self.rect.x, self.rect.y = x * self.board.cell_size + self.board.left, y * self.board.cell_size + self.board.top
        self.board.board[y][x] = 11
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


class Dummy(Monster):
    def __init__(self, board, *groups, hp=10, default_damage=1, default_armor=1):
        super().__init__(board, *groups, hp=hp, default_damage=default_damage, default_armor=default_armor)
        self.image = pygame.Surface((board.cell_size, board.cell_size))
        self.image.fill("RED")
        self.rect = self.image.get_rect()  # Получаем прямоугольник для спрайта
        self.set_rect(2, 2)
