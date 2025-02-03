import sqlite3


def check_db():
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()

        query = """
        CREATE TABLE IF NOT EXISTS player (
            id INTEGER,
            best_wave INTEGER DEFAULT 0,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
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
            unic INTEGER,
            name TEXT,
            protect INTEGER,
            rarity INTEGER,
            sprite_path TEXT,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
        
        CREATE TABLE IF NOT EXISTS accessories (
            id INTEGER,
            name TEXT,
            unic INTEGER,
            buff_hp INTEGER,
            rarity INTEGER,
            sprite_path TEXT,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
        
        CREATE TABLE IF NOT EXISTS potion (
            id INTEGER,
            name TEXT,
            effect INTEGER,
            rarity INTEGER,
            sprite_path TEXT,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
        """
        cursor.executescript(query)
        print(1)
        db.commit()
        from acss.acss_logic import accessories_list
        from armores.armor_logic import armor_list
        from potions.potion_logic import potion_list
        from weapons.weapon_logic import weapons_list
        # Проверка наличия данных в таблице и добавление, если пусто
        cursor.execute('SELECT best_wave FROM player')
        best_wave = cursor.fetchone()
        if best_wave is None:
            cursor.execute("INSERT INTO player (best_wave) VALUES (0);")

        cursor.execute("SELECT COUNT(*) FROM weapons")
        if cursor.fetchone()[0] == 0:
            for weapon in weapons_list:
                cursor.execute("INSERT INTO weapons (name, damage, rarity, sprite_path) VALUES (?, ?, ?, ?)",
                               (weapon["name"], weapon["damage"], weapon["rarity"], weapon["sprite_path"]))
        cursor.execute("SELECT COUNT(*) FROM armor")
        if cursor.fetchone()[0] == 0:
            for armor in armor_list:
                cursor.execute("INSERT INTO armor (name, unic, protect, rarity, sprite_path) "
                               "VALUES (?, ?, ?, ?, ?)",
                               (armor["name"], armor['unic'], armor["protect"], armor["rarity"],
                                armor["sprite_path"]))
        cursor.execute("SELECT COUNT(*) FROM accessories")
        if cursor.fetchone()[0] == 0:
            for acs in accessories_list:
                cursor.execute(
                    "INSERT INTO accessories (name, unic, buff_hp, rarity, sprite_path) VALUES (?, ?, ?, ?, ?)",
                    (acs["name"], acs['unic'], acs["buff_hp"], acs["rarity"], acs["sprite_path"]))
        cursor.execute("SELECT COUNT(*) FROM potion")
        if cursor.fetchone()[0] == 0:
            for potion in potion_list:
                cursor.execute("INSERT INTO potion (name, effect, rarity, sprite_path) VALUES (?, ?, ?, ?)",
                               (potion["name"], potion['effect'], potion["rarity"], potion["sprite_path"]))
