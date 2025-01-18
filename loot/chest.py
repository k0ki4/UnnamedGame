import pygame.sprite


class LootChest(pygame.sprite.Sprite):

    def __init__(self, board, *groups, x, y, rarity=1):
        base_path = './sprites/chest/'

        self.sprites = [
            pygame.image.load(base_path + 'chest_r1.png').convert_alpha(),
            pygame.image.load(base_path + 'chest_r2.png').convert_alpha(),
            pygame.image.load(base_path + 'chest_r3.png').convert_alpha(),
            pygame.image.load(base_path + 'chest_r4.png').convert_alpha(),
        ]

        self.open_chest = pygame.image.load(base_path + 'open_chest.png').convert_alpha()
        super().__init__(*groups)
        self.board = board
        self.rarity = rarity
        self.image = None
        self.get_image_by_rarity()
        self.image = pygame.transform.scale(self.image, (self.board.cell_size, self.board.cell_size))
        self.rect = self.image.get_rect()
        self.set_rect(x, y)
        self.is_open = False

    def get_image_by_rarity(self):
        for i in range(1, 5):
            if i == self.rarity:
                self.image = self.sprites[i - 1]

    def set_rect(self, x, y):
        self.rect.x, self.rect.y = x * self.board.cell_size + self.board.left, y * self.board.cell_size + self.board.top
        self.board.board[y][x] = self
        for i in self.board.board:
            print(i)
        print()


    def __repr__(self):
        return f'Chest: {self.rarity}'
