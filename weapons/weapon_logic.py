import sqlite3

import pygame
from Tools.demo.spreadsheet import center

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
     "sprite_path": "sprites/weapons_image/rapier/rapier_r3.png"}
]


class Weapon(pygame.sprite.Sprite):
    def __init__(self, name, damage, rarity, sprite_path, *groups):
        super().__init__(*groups)

        self.name = name
        self.damage = damage
        self.rarity = rarity
        self.sprite_path = sprite_path
        self.bonus = 0
        self.lvl_bonus = 0

        self.button_rect = pygame.Rect((325, 290, 150, 70))
        self.drop_button_rect = pygame.Rect((500, 290, 70, 70))

        self.image = pygame.image.load(self.sprite_path)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = -100, -100

        self.open_stats = False
        self.is_equip = False

        self.color_rarity = {
            1: 'WHITE',
            2: 'ORANGE',
            3: 'VIOLET',
        }

    def equip(self, rect):
        if not self.is_equip:
            self.is_equip = True
            self.rect = rect

    def on_click(self, player):
        print(f'Выбранно оружие: {self.name}' if not self.open_stats else "Выбор снят")
        for slot in player.inventory.slots + player.inventory.unic_slot:
            if slot.item is not None and slot.item != self:
                slot.item.open_stats = False
        self.open_stats = not self.open_stats

    def stats_update(self, screen):
        if self.open_stats:
            frame = pygame.image.load('./sprites/gui/gui.png').convert_alpha()
            frame = pygame.transform.scale(frame, (300, 265))
            rect_frame = frame.get_rect(topleft=(310, 120))
            frame2 = pygame.image.load('./sprites/gui/gui_2.png').convert_alpha()
            frame2 = pygame.transform.scale(frame2, (300, 265))
            rect_frame2 = frame.get_rect(topleft=(310, 120))

            pygame.font.init()
            font_medium = pygame.font.Font('misc/font_ttf/Undertale-Battle-Font.ttf', 20)
            font_large = pygame.font.Font('misc/font_ttf/Undertale-Battle-Font.ttf', 30)

            name = font_large.render(f"{self.name}", True, self.color_rarity[self.rarity])  # Белый текст
            damage_text = font_medium.render(f"Урон: {self.damage}", True, (255, 255, 255))
            bonus_text = font_medium.render(f"Бонус редкости: {self.bonus}", True,
                                            (255, 255, 255))
            lvl_text = font_medium.render(f"Бонус уровня: {self.lvl_bonus}", True, (255, 255, 255))

            button_text = font_medium.render("Выбрать", True, (255, 255, 255))
            text_rect = button_text.get_rect(center=self.button_rect.center)

            frame_button = pygame.image.load('./sprites/inventory/button.png').convert_alpha()
            frame_button = pygame.transform.scale(frame_button, (150, 70))


            screen.blit(frame, rect_frame)
            screen.blit(frame2, rect_frame2)

            cord_text_x = 325
            screen.blit(name, (cord_text_x, 130))
            screen.blit(damage_text, (cord_text_x, 200))
            screen.blit(bonus_text, (cord_text_x, 230))
            screen.blit(lvl_text, (cord_text_x, 260))

            drop_button_text = font_medium.render("Выбросить", True, (255, 255, 255))
            text_width, text_height = drop_button_text.get_size()
            text_x = self.drop_button_rect.x + (self.drop_button_rect.width - text_width) // 2
            text_y = self.drop_button_rect.y + (self.drop_button_rect.height - text_height) // 2
            screen.blit(drop_button_text, (text_x, text_y))

            if not self.is_equip:
                screen.blit(frame_button, self.button_rect)
                screen.blit(button_text, text_rect)

                drop_button_text = font_medium.render("Выбросить", True, (255, 255, 255))
                text_width, text_height = drop_button_text.get_size()
                text_x = self.drop_button_rect.x + (self.drop_button_rect.width - text_width) // 2
                text_y = self.drop_button_rect.y + (self.drop_button_rect.height - text_height) // 2
                screen.blit(drop_button_text, (text_x, text_y))

            else:
                button_text = font_medium.render("Снять", True, (255, 255, 255))
                text_rect = button_text.get_rect(center=self.button_rect.center)
                screen.blit(frame_button, self.button_rect)
                screen.blit(button_text, text_rect)


    def get_bonus(self, bonus):
        self.bonus = bonus
        self.damage += bonus

    def get_lvl_bonus(self, bonus):
        self.lvl_bonus = bonus
        self.damage += bonus

    def set_rect(self, rect):
        self.rect = rect

    def draw(self, screen, slot_rect):
        slot_rect = slot_rect
        self.image = pygame.transform.scale(self.image, (slot_rect[2], slot_rect[3]))
        screen.blit(self.image, slot_rect)

    def return_copy(self):
        return Weapon(self.name, self.damage, self.rarity, self.sprite_path)


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
