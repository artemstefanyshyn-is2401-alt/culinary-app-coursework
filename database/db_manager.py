import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="data/recipes.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Створення таблиць, якщо вони ще не існують, та оновлення структури"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    category TEXT NOT NULL,
                    prep_time INTEGER,
                    calories INTEGER,
                    instructions TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ingredients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recipe_ingredients (
                    recipe_id INTEGER,
                    ingredient_id INTEGER,
                    amount TEXT,
                    FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE CASCADE,
                    FOREIGN KEY (ingredient_id) REFERENCES ingredients (id) ON DELETE CASCADE,
                    PRIMARY KEY (recipe_id, ingredient_id)
                )
            ''')

            cursor.execute("PRAGMA table_info(meal_plans)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'meal_type' not in columns:
                cursor.execute("DROP TABLE IF EXISTS meal_plans")
                cursor.execute('''
                    CREATE TABLE meal_plans (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        day_of_week TEXT NOT NULL,
                        meal_type TEXT NOT NULL,
                        recipe_id INTEGER,
                        FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE CASCADE,
                        UNIQUE(day_of_week, meal_type)
                    )
                ''')

            conn.commit()
        
        self.seed_initial_data()

    def seed_initial_data(self):
        """Розширене заповнення бази початковими даними"""
        initial_recipes = [
            ("Борщ український", "Перші страви", 90, 350, "Зварити бульйон, додати буряк, капусту, картоплю та зажарку.", "Яловичина, Буряк, Капуста, Картопля, Морква, Цибуля"),
            ("Окрошка", "Перші страви", 20, 210, "Нарізати овочі, відварні яйця та шинку, залити квасом або кефіром.", "Огірки, Редис, Яйця, Шика, Кефір, Зелень"),
            ("Суп-крем з грибів", "Перші страви", 35, 240, "Обсмажити печериці з цибулею, зварити з картоплею та збити блендером зі вершками.", "Печериці, Картопля, Вершки, Цибуля, Вершкове масло"),
            ("Вареники з картоплею", "Основні страви", 45, 280, "Замісити тісто, зробити начинку з відварної картоплі з цибулею, зварити.", "Борошно, Картопля, Цибуля, Олія"),
            ("Плов з куркою", "Основні страви", 50, 380, "Обсмажити курку, цибулю, моркву, засипати рис, залити водою та тушкувати.", "Курка, Рис, Морква, Цибуля, Спеції"),
            ("Стейк із лосося", "Основні страви", 20, 320, "Замаринувати лосось у лимонному соку та спеціях, обсмажити на грилі.", "Лосось, Лимон, Оливкова олія, Спеції"),
            ("Омлет із зеленню", "Закуски", 15, 180, "Збити яйця з молоком, вилити на пательню, посипати зеленню та сиром.", "Яйця, Молоко, Зелень, Сир"),
            ("Деруни", "Закуски", 30, 310, "Натерти картоплю, додати яйце, борошно, спеції та обсмажити з двох боків.", "Картопля, Яйце, Борошно, Цибуля"),
            ("Брускета з томатами", "Закуски", 15, 160, "Підсмажити багет, викласти нарізані томати з базиліком та часником.", "Багет, Томати, Базилік, Часник, Оливкова олія"),
            ("Сирники з ягодами", "Десерти", 25, 260, "Перетерти кисломолочний сир, додати яйце, борошно, сформувати сирники та обсмажити.", "Сир кисломолочний, Яйце, Борошно, Цукор, Ягоди"),
            ("Шарлотка з яблуками", "Десерти", 40, 290, "Збити яйця з цукром, додати борошно, залити нарізані яблука та запекти.", "Яблука, Яйця, Цукор, Борошно"),
            ("Цезар з куркою", "Салати", 25, 220, "Обсмажити курку, нарізати листя салату, додати соус, пармезан та сухарики.", "Куряче філе, Салат Айсберг, Соус Цезар, Пармезан, Сухарики"),
            ("Овочевий салат з тунцем", "Салати", 15, 190, "Змішати листя салату, томати, огірки, оливки та консервований тунець.", "Тунець, Томати, Огірки, Оливки, Оливкова олія"),
            ("Узвар", "Напої", 20, 90, "Залити сухофрукти водою, довести до кипіння та настояти під кришкою.", "Сухофрукти, Вода, Мед"),
            ("Лимонад м'ятний", "Напої", 10, 70, "Вичавити сік лимона, змішати з водою, цукром та розтертою м'ятою.", "Лимон, М'ята, Вода, Цукор")
        ]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            for name, cat, prep, cal, inst, ing_str in initial_recipes:
                cursor.execute("SELECT id FROM recipes WHERE name = ?", (name,))
                exists = cursor.fetchone()
                if not exists:
                    cursor.execute('''
                        INSERT INTO recipes (name, category, prep_time, calories, instructions)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (name, cat, prep, cal, inst))
                    recipe_id = cursor.lastrowid
                    self._save_recipe_ingredients(cursor, recipe_id, ing_str)
            conn.commit()

    def get_all_recipes(self, search_query="", category_filter="Всі категорії", sort_by="id_asc"):
        """Повертає всі рецепти із урахуванням пошуку, фільтрації та сортування"""
        sort_clause = "ORDER BY id ASC"
        if sort_by == "time_asc":
            sort_clause = "ORDER BY prep_time ASC"
        elif sort_by == "time_desc":
            sort_clause = "ORDER BY prep_time DESC"
        elif sort_by == "calories_asc":
            sort_clause = "ORDER BY calories ASC"
        elif sort_by == "calories_desc":
            sort_clause = "ORDER BY calories DESC"

        conditions = []
        params = []

        if search_query:
            conditions.append("(name LIKE ? OR category LIKE ?)")
            params.extend([f"%{search_query}%", f"%{search_query}%"])

        if category_filter and category_filter != "Всі категорії":
            conditions.append("category = ?")
            params.append(category_filter)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = f'''
                SELECT id, name, category, prep_time, calories 
                FROM recipes 
                {where_clause}
                {sort_clause}
            '''
            cursor.execute(query, params)
            return cursor.fetchall()

    def get_recipe_by_id(self, recipe_id):
        """Отримання повної інформації про рецепт за ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, category, prep_time, calories, instructions 
                FROM recipes 
                WHERE id = ?
            ''', (recipe_id,))
            return cursor.fetchone()

    def get_random_recipe(self):
        """Отримання одного випадкового рецепта з бази даних"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, category, prep_time, calories, instructions 
                FROM recipes 
                ORDER BY RANDOM() LIMIT 1
            ''')
            return cursor.fetchone()

    def add_recipe(self, name, category, prep_time, calories, instructions, ingredients_str=""):
        """Додавання нового рецепта та його інгредієнтів"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO recipes (name, category, prep_time, calories, instructions)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, category, prep_time, calories, instructions))
            recipe_id = cursor.lastrowid
            
            if ingredients_str:
                self._save_recipe_ingredients(cursor, recipe_id, ingredients_str)
            conn.commit()

    def update_recipe(self, recipe_id, name, category, prep_time, calories, instructions, ingredients_str=""):
        """Оновлення рецепта та його інгредієнтів"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE recipes
                SET name = ?, category = ?, prep_time = ?, calories = ?, instructions = ?
                WHERE id = ?
            ''', (name, category, prep_time, calories, instructions, recipe_id))
            
            cursor.execute("DELETE FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))
            if ingredients_str:
                self._save_recipe_ingredients(cursor, recipe_id, ingredients_str)
            conn.commit()

    def _save_recipe_ingredients(self, cursor, recipe_id, ingredients_str):
        """Допоміжний метод для збереження інгредієнтів"""
        items = [item.strip() for item in ingredients_str.split(",") if item.strip()]
        for item in items:
            cursor.execute("INSERT OR IGNORE INTO ingredients (name) VALUES (?)", (item,))
            cursor.execute("SELECT id FROM ingredients WHERE name = ?", (item,))
            ing_id = cursor.fetchone()[0]
            cursor.execute('''
                INSERT OR REPLACE INTO recipe_ingredients (recipe_id, ingredient_id, amount)
                VALUES (?, ?, ?)
            ''', (recipe_id, ing_id, ""))

    def get_recipe_ingredients(self, recipe_id):
        """Отримання списку інгредієнтів у вигляді текстового рядка"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT i.name 
                FROM ingredients i
                JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
                WHERE ri.recipe_id = ?
            ''', (recipe_id,))
            rows = cursor.fetchall()
            return ", ".join([r[0] for r in rows])

    def delete_recipe(self, recipe_id):
        """Видалення рецепта за ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
            conn.commit()

    # --- Методи планування меню ---

    def set_meal_plan_for_day(self, day_of_week, meal_type, recipe_id):
        """Встановлення або оновлення страви для конкретного прийому їжі"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO meal_plans (day_of_week, meal_type, recipe_id)
                VALUES (?, ?, ?)
                ON CONFLICT(day_of_week, meal_type) DO UPDATE SET recipe_id = excluded.recipe_id
            ''', (day_of_week, meal_type, recipe_id))
            conn.commit()

    def clear_meal_plan_for_day_and_type(self, day_of_week, meal_type):
        """Видалення конкретного прийому їжі з обраного дня"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM meal_plans WHERE day_of_week = ? AND meal_type = ?", (day_of_week, meal_type))
            conn.commit()

    def get_meal_plan(self):
        """Отримання всього запланованого меню"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT mp.day_of_week, mp.meal_type, r.name, r.calories
                FROM meal_plans mp
                JOIN recipes r ON mp.recipe_id = r.id
            ''')
            return cursor.fetchall()

    def clear_all_meal_plans(self):
        """Повне очищення розкладу"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM meal_plans")
            conn.commit()