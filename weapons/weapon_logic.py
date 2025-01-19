import pygame

weapons_list = [
    {"name": "Пушка", "damage": 50, "rarity": 1, "sprite_path": "elephant_gun.png"},
    {"name": "Меч", "damage": 30, "rarity": 2, "sprite_path": "sword.png"},
    {"name": "Лук", "damage": 20, "rarity": 2, "sprite_path": "bow.png"},
    {"name": "Дробовик", "damage": 40, "rarity": 3, "sprite_path": "shotgun.png"},
    {"name": "Граната", "damage": 100, "rarity": 4, "sprite_path": "grenade.png"},
    {"name": "Кинжал", "damage": 25, "rarity": 2, "sprite_path": "dagger.png"},
    {"name": "Пистолет", "damage": 35, "rarity": 3, "sprite_path": "pistol.png"},
    {"name": "Ружье", "damage": 45, "rarity": 3, "sprite_path": "rifle.png"},
    {"name": "Базука", "damage": 150, "rarity": 5, "sprite_path": "bazooka.png"},
    {"name": "Снайперская винтовка", "damage": 60, "rarity": 4, "sprite_path": "sniper_rifle.png"}
]


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

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 15)

    def take(self, player):
        pass

    def equip(self, player):
        pass