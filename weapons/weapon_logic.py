import pygame


class Weapon(pygame.sprite.Sprite):
    def __init__(self, board, *groups, damage=1):
        super().__init__(*groups)
        self.board = board

        self.damage = damage

        self.image = pygame.Surface((board.cell_size, board.cell_size))
        self.image.fill("BLUE")
        self.rect = self.image.get_rect()  # Получаем прямоугольник для спрайта

        self.board.board[0][0] = 10
        self.rect.x, self.rect.y = 0 * board.cell_size + board.left, 0 * board.cell_size + board.top

        self.last_move_time = 0  # Время последнего движения
        self.move_delay = 0.2  # Задержка в секундах

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 15)

    def take(self, player):
        pass

    def equip(self, player):
        pass


class Sword(Weapon):
    def __init__(self, board, *groups, damage):
        self.fall = True
        super().__init__(board, *groups, damage=damage)

    def equip(self, player):
        if self.fall:
            return False
        player.equip_weapon = self
        player.inventory -= [self]
        print('Оружие надето')

    def take(self, player):
        self.fall = False
        player.inventory.appned(self)
        print('Оружие взято')