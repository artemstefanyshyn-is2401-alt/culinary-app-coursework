import random
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QMessageBox, QHeaderView, QFileDialog
)

class MealPlannerDialog(QDialog):
    DAYS = [
        "Понеділок", "Вівторок", "Середа", 
        "Четвер", "П'ятниця", "Субота", "Неділя"
    ]
    MEAL_TYPES = ["Сніданок", "Обід", "Вечеря"]

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setWindowTitle("Планування меню на тиждень (Сніданок, Обід, Вечеря)")
        self.resize(800, 560)
        self.init_ui()
        self.load_meal_plan()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Панель призначення страви
        add_layout = QHBoxLayout()
        
        add_layout.addWidget(QLabel("День:"))
        self.day_combo = QComboBox()
        self.day_combo.addItems(self.DAYS)
        add_layout.addWidget(self.day_combo)

        add_layout.addWidget(QLabel("Прийом їжі:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.MEAL_TYPES)
        add_layout.addWidget(self.type_combo)

        add_layout.addWidget(QLabel("Рецепт:"))
        self.recipe_combo = QComboBox()
        self.load_recipes_into_combo()
        add_layout.addWidget(self.recipe_combo)

        btn_add_plan = QPushButton("Додати")
        btn_add_plan.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        btn_add_plan.clicked.connect(self.assign_recipe)
        add_layout.addWidget(btn_add_plan)

        layout.addLayout(add_layout)

        # Таблиця розкладу
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["День тижня", "Прийом їжі", "Обраний рецепт", "Калорії (ккал)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # Підсумок калорій
        self.total_calories_label = QLabel("Загальна калорійність меню на тиждень: 0 ккал")
        self.total_calories_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(self.total_calories_label)

        # Кнопки
        btn_layout = QHBoxLayout()
        
        btn_auto = QPushButton("🎲 Авто-меню на тиждень")
        btn_auto.setStyleSheet("background-color: #CBA6F7; color: #11111B; font-weight: bold;")
        btn_auto.clicked.connect(self.generate_random_week)
        btn_layout.addWidget(btn_auto)

        btn_export = QPushButton("Зберегти у TXT")
        btn_export.setStyleSheet("background-color: #89B4FA; color: #11111B; font-weight: bold;")
        btn_export.clicked.connect(self.export_to_txt)
        btn_layout.addWidget(btn_export)

        btn_layout.addStretch()

        btn_clear_item = QPushButton("Видалити обране")
        btn_clear_item.setStyleSheet("background-color: #FAB387; color: #11111B; font-weight: bold;")
        btn_clear_item.clicked.connect(self.clear_selected_item)
        btn_layout.addWidget(btn_clear_item)

        btn_clear_all = QPushButton("Очистити все")
        btn_clear_all.setStyleSheet("background-color: #F38BA8; color: #11111B; font-weight: bold;")
        btn_clear_all.clicked.connect(self.clear_all)
        btn_layout.addWidget(btn_clear_all)

        layout.addLayout(btn_layout)

    def load_recipes_into_combo(self):
        recipes = self.db.get_all_recipes()
        self.recipe_combo.clear()
        for r in recipes:
            self.recipe_combo.addItem(r[1], r[0])

    def load_meal_plan(self):
        plans_data = self.db.get_meal_plan()
        plan_dict = {(p[0], p[1]): (p[2], p[3]) for p in plans_data}

        self.table.setRowCount(0)
        total_calories = 0
        row_idx = 0

        for day in self.DAYS:
            for m_type in self.MEAL_TYPES:
                self.table.insertRow(row_idx)
                
                day_item = QTableWidgetItem(day)
                type_item = QTableWidgetItem(m_type)
                
                if (day, m_type) in plan_dict:
                    recipe_name, calories = plan_dict[(day, m_type)]
                    recipe_item = QTableWidgetItem(recipe_name)
                    cals_item = QTableWidgetItem(str(calories))
                    total_calories += int(calories)
                else:
                    recipe_item = QTableWidgetItem("—")
                    cals_item = QTableWidgetItem("0")

                self.table.setItem(row_idx, 0, day_item)
                self.table.setItem(row_idx, 1, type_item)
                self.table.setItem(row_idx, 2, recipe_item)
                self.table.setItem(row_idx, 3, cals_item)
                
                row_idx += 1

        self.total_calories_label.setText(f"Загальна калорійність меню на тиждень: {total_calories} ккал")

    def assign_recipe(self):
        day = self.day_combo.currentText()
        m_type = self.type_combo.currentText()
        recipe_id = self.recipe_combo.currentData()

        if recipe_id is None:
            QMessageBox.warning(self, "Помилка", "Будь ласка, оберіть рецепт зі списку!")
            return

        self.db.set_meal_plan_for_day(day, m_type, recipe_id)
        self.load_meal_plan()

    def generate_random_week(self):
        all_recipes = self.db.get_all_recipes()
        if not all_recipes:
            QMessageBox.warning(self, "Увага", "У базі немає рецептів для генерації!")
            return

        # Групуємо рецепти за відповідністю до прийомів їжі для логічного підбору
        breakfast_candidates = [r for r in all_recipes if r[2] in ["Закуски", "Десерти", "Салати"]]
        lunch_candidates = [r for r in all_recipes if r[2] in ["Перші страви", "Основні страви"]]
        dinner_candidates = [r for r in all_recipes if r[2] in ["Основні страви", "Салати", "Закуски"]]

        # Якщо якась група порожня — використовуємо весь список
        if not breakfast_candidates: breakfast_candidates = all_recipes
        if not lunch_candidates: lunch_candidates = all_recipes
        if not dinner_candidates: dinner_candidates = all_recipes

        for day in self.DAYS:
            # Вибираємо випадкові легкі страви на Сніданок, гарячі на Обід та ситні/легкі на Вечерю
            s_recipe = random.choice(breakfast_candidates)
            l_recipe = random.choice(lunch_candidates)
            d_recipe = random.choice(dinner_candidates)

            self.db.set_meal_plan_for_day(day, "Сніданок", s_recipe[0])
            self.db.set_meal_plan_for_day(day, "Обід", l_recipe[0])
            self.db.set_meal_plan_for_day(day, "Вечеря", d_recipe[0])

        self.load_meal_plan()

    def clear_selected_item(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Увага", "Будь ласка, оберіть рядок у таблиці!")
            return

        day_name = self.table.item(selected_row, 0).text()
        meal_type = self.table.item(selected_row, 1).text()
        self.db.clear_meal_plan_for_day_and_type(day_name, meal_type)
        self.load_meal_plan()

    def clear_all(self):
        self.db.clear_all_meal_plans()
        self.load_meal_plan()

    def export_to_txt(self):
        plans_data = self.db.get_meal_plan()
        if not plans_data:
            QMessageBox.warning(self, "Увага", "План меню порожній!")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Зберегти меню", "meal_plan.txt", "Text Files (*.txt)")
        if file_path:
            plan_dict = {(p[0], p[1]): (p[2], p[3]) for p in plans_data}
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("=== РОЗКЛАД МЕНЮ НА ТИЖДЕНЬ ===\n\n")
                total_cals = 0
                for day in self.DAYS:
                    f.write(f"[{day.upper()}]\n")
                    for m_type in self.MEAL_TYPES:
                        if (day, m_type) in plan_dict:
                            name, cals = plan_dict[(day, m_type)]
                            f.write(f"  • {m_type}: {name} ({cals} ккал)\n")
                            total_cals += int(cals)
                        else:
                            f.write(f"  • {m_type}: —\n")
                    f.write("\n")
                f.write(f"Загальна калорійність на тиждень: {total_cals} ккал\n")
            
            QMessageBox.information(self, "Успіх", "План меню успішно збережено у файл!")