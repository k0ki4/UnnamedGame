import random

import pygame

from acss.acss_logic import result_acs
from armores.armor_logic import result_armor
from potions.potion_logic import result_potion, Potion
from weapons.weapon_logic import result_weapon


class LootChest(pygame.sprite.Sprite):
    all_items = result_potion + result_acs + result_armor + result_weapon

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
        for i in range(1, 4):
            if i == self.rarity:
                self.image = self.sprites[i - 1]

    def get_item_for_rarity(self):
        if self.rarity > 1:
            new_list = filter_item_by_rarity(self.all_items, self.rarity) + filter_item_by_rarity(self.all_items,
                                                                                                  self.rarity - 1)
        else:
            new_list = filter_item_by_rarity(self.all_items, self.rarity)

        if new_list:
            random.shuffle(self.all_items)
            item = random.choice(new_list)
            item = item.return_copy()
            return item

    def toggle_chest(self, player):
        if not self.is_open:
            count_loot = random.randint(1, 2)
            for i in range(count_loot):
                item = self.get_item_for_rarity()
                print(f'Редкость: {self.rarity}')
                print('Сундук открыт')
                print(f'Редкость предмета: {item.rarity}')
                if self.rarity > item.rarity and not isinstance(item, Potion):
                    bonus = random.randint(1, 5)
                    item.get_bonus(bonus)
                    print(f'Бонус к оружию +{bonus}')
                    item.get_lvl_bonus(player.lvl)
                    print(f'Бонус от лвл-а {player.lvl}')
                player.inventory.add_item(item)
            self.is_open = True
            self.image = self.open_chest

        else:
            print('Сундук уже открыт')

    def set_rect(self, x, y):
        self.rect.x, self.rect.y = x * self.board.cell_size + self.board.left, y * self.board.cell_size + self.board.top
        self.board.board[y][x] = self

    def __repr__(self):
        return f'Chest: {self.rarity}'


class InfinityChest(LootChest):
    def __init__(self, board, *groups, x, y, rarity=1):
        super().__init__(board, *groups, x=x, y=y, rarity=rarity)

        self.infinity = True

    def toggle_chest(self, player):
        if not self.is_open and self.infinity:
            count_loot = random.randint(1, 2)
            for i in range(count_loot):
                item = self.get_item_for_rarity()
                print(f'Редкость: {self.rarity}')
                print('Сундук открыт')
                print(f'Редкость предмета: {item.rarity}')
                if self.rarity > item.rarity and not isinstance(item, Potion):
                    bonus = random.randint(1, 5)
                    item.get_bonus(bonus)
                    print(f'Бонус к оружию +{bonus}')
                    item.get_lvl_bonus(player.lvl)
                    print(f'Бонус от лвл-а {player.lvl}')
                player.inventory.add_item(item)


class ArmorChest(LootChest):
    def __init__(self, board, *groups, x, y, rarity=1):
        super().__init__(board, *groups, x=x, y=y, rarity=rarity)

    def get_item_for_rarity(self):
        if self.rarity > 1:
            new_list = filter_item_by_rarity(result_armor, self.rarity) + filter_item_by_rarity(result_armor,
                                                                                                  self.rarity - 1)
        else:
            new_list = filter_item_by_rarity(result_armor, self.rarity)

        if new_list:
            item = random.choice(new_list)
            item = item.return_copy()
            return item



def filter_item_by_rarity(items, rarity):
    return [item for item in items if item.rarity == rarity]
