import sqlite3

from weapons.weapon_logic import weapons_list

def check_db():
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()

        query = """
        CREATE TABLE IF NOT EXISTS weapons (
            id INTEGER,
            name TEXT,
            damage INTEGER,
            rarity INTEGER,
            sprite_path TEXT,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
        
        CREATE TABLE IF NOT EXISTS armor (
            id INTEGER,
            name TEXT,
            protect INTEGER,
            rarity INTEGER,
            sprite_path TEXT,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
        """
        cursor.executescript(query)

        # Проверка наличия данных в таблице и добавление, если пусто
        cursor.execute("SELECT COUNT(*) FROM weapons")
        if cursor.fetchone()[0] == 0:
            for weapon in weapons_list:
                cursor.execute("INSERT INTO weapons (name, damage, rarity, sprite_path) VALUES (?, ?, ?, ?)",
                               (weapon["name"], weapon["damage"], weapon["rarity"], weapon["sprite_path"]))
        # cursor.execute("SELECT COUNT(*) FROM armor")
        # if cursor.fetchone()[0] == 0:
        #     for weapon in weapons_list:
        #         cursor.execute("INSERT INTO weapons (name, damage, rarity, sprite_path) VALUES (?, ?, ?, ?)",
        #                        (weapon["name"], weapon["damage"], weapon["rarity"], weapon["sprite_path"]))
