import random

import pygame.sprite

from weapons.weapon_logic import filter_weapons_by_rarity, Weapon, result_weapon


class LootChest(pygame.sprite.Sprite):

    def __init__(self, board, *groups, x, y, rarity=1):
        self.board = board
        base_path = './sprites/chest/'

        self.sprites = [
            pygame.image.load(base_path + 'chest_r1.png').convert_alpha(),
            pygame.image.load(base_path + 'chest_r2.png').convert_alpha(),
            pygame.image.load(base_path + 'chest_r3.png').convert_alpha(),
            pygame.image.load(base_path + 'chest_r4.png').convert_alpha(),
        ]

        self.open_chest = pygame.image.load(base_path + 'open_chest.png').convert_alpha()
        self.open_chest = pygame.transform.scale(self.open_chest, (self.board.cell_size, self.board.cell_size))

        super().__init__(*groups)
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

    def get_weapons_for_rarity(self):
        if self.rarity > 1:
            new_list = filter_weapons_by_rarity(result_weapon, self.rarity) + filter_weapons_by_rarity(result_weapon,
                                                                                                       self.rarity - 1)
        else:
            new_list = filter_weapons_by_rarity(result_weapon, self.rarity)
        return random.choice(new_list)

    def toggle_chest(self):
        if not self.is_open:
            self.is_open = True
            self.image = pygame.transform.scale(self.open_chest, (self.board.cell_size, self.board.cell_size))
            player = self.board.get_player()
            item = self.get_weapons_for_rarity()
            player.inventory.add_item(item)
            print(f'Редкость: {self.rarity}')
            print('Сундук открыт')
            print(f'Редкость предмета: {item.rarity}')
            if self.rarity > item.rarity:
                print('Бонус к оружию +5')
                item.damage += 5
        else:
            print('Сундук уже открыт')

    def set_rect(self, x, y):
        self.rect.x, self.rect.y = x * self.board.cell_size + self.board.left, y * self.board.cell_size + self.board.top
        self.board.board[y][x] = self
        for i in self.board.board:
            print(i)
        print()

    def __repr__(self):
        return f'Chest: {self.rarity}'



