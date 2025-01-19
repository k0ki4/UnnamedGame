import sqlite3

import pygame

weapons_list = [
    {"name": "Меч", "damage": 10, "rarity": 1, "sprite_path": "sprites/weapons_image/sword/sword_r1.png"},
    {"name": "Копьё", "damage": 10, "rarity": 1, "sprite_path": "sprites/weapons_image/spear/spear_r1.png"},
    {"name": "Рапира", "damage": 10, "rarity": 1, "sprite_path": "sprites/weapons_image/rapier/rapier_r1.png"},

    {"name": "Редкий Меч", "damage": 10, "rarity": 2, "sprite_path": "sprites/weapons_image/sword/sword_r2.png"},
    {"name": "Редкое Копьё", "damage": 10, "rarity": 2, "sprite_path": "sprites/weapons_image/spear/spear_r2.png"},
    {"name": "Редкая Рапира", "damage": 10, "rarity": 2, "sprite_path": "sprites/weapons_image/rapier/rapier_r1.png"},

    {"name": "Эпический Меч", "damage": 10, "rarity": 3, "sprite_path": "sprites/weapons_image/sword/sword_r3.png"},
    {"name": "Эпическое Копьё", "damage": 10, "rarity": 3, "sprite_path": "sprites/weapons_image/spear/spear_r3.png"},
    {"name": "Эпическая Рапира", "damage": 10, "rarity": 3,
     "sprite_path": "sprites/weapons_image/rapier/rapier_r1.png"}
]


class Weapon(pygame.sprite.Sprite):
    def __init__(self, name, damage, rarity, sprite_path, *groups):
        super().__init__(*groups)

        self.name = name
        self.damage = damage
        self.rarity = rarity

        self.image = pygame.image.load(sprite_path)
        self.rect = self.image.get_rect()

        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 15)

    def equip(self, player):
        pass

    def on_click(self):
        pass

    def draw(self, screen, slot_rect):
        slot_rect = slot_rect
        self.image = pygame.transform.scale(self.image, (slot_rect[2], slot_rect[3]))
        screen.blit(self.image, slot_rect)


def sort_weapons_by_rarity(weapons):
    return sorted(weapons, key=lambda weapon: weapon.rarity)


def sort_weapons_by_damage(weapons):
    return sorted(weapons, key=lambda weapon: weapon.damage)


def filter_weapons_by_rarity(weapons, rarity):
    return [weapon for weapon in weapons if weapon.rarity == rarity]


def filter_weapons_by_damage(weapons, damage):
    return [weapon for weapon in weapons if weapon.damage == damage]


def randomize_weapons():
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT name, damage, rarity, sprite_path FROM weapons")
        weapons_data = cursor.fetchall()
    return [Weapon(name=name, damage=damage, rarity=rarity, sprite_path=sprite_path) for
            name, damage, rarity, sprite_path in weapons_data]


result_weapon = randomize_weapons()
