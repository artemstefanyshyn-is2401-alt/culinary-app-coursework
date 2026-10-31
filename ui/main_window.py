from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QTableWidget, QTableWidgetItem, 
    QPushButton, QMessageBox, QHeaderView, QComboBox, QStatusBar
)
from database.db_manager import DatabaseManager
from ui.recipe_dialog import RecipeDialog
from ui.recipe_detail_dialog import RecipeDetailDialog
from ui.meal_planner_dialog import MealPlannerDialog
from ui.style import MODERN_STYLE

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setStyleSheet(MODERN_STYLE)
        self.init_ui()
        self.load_recipes()

    def init_ui(self):
        self.setWindowTitle("Кулінарні рецепти та планування меню")
        self.resize(1150, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Панель пошуку, фільтрації та сортування
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Пошук:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введіть назву...")
        self.search_input.textChanged.connect(self.load_recipes)
        filter_layout.addWidget(self.search_input)

        filter_layout.addWidget(QLabel("Категорія:"))
        self.category_filter_combo = QComboBox()
        self.category_filter_combo.addItems([
            "Всі категорії",
            "Перші страви", 
            "Основні страви", 
            "Салати", 
            "Закуски", 
            "Десерти", 
            "Напої"
        ])
        self.category_filter_combo.currentIndexChanged.connect(self.load_recipes)
        filter_layout.addWidget(self.category_filter_combo)

        filter_layout.addWidget(QLabel("Сортувати за:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("За ID (за замовчуванням)", "id_asc")
        self.sort_combo.addItem("За часом (спочатку швидкі)", "time_asc")
        self.sort_combo.addItem("За часом (спочатку довгі)", "time_desc")
        self.sort_combo.addItem("За калоріями (зростання)", "calories_asc")
        self.sort_combo.addItem("За калоріями (спадання)", "calories_desc")
        self.sort_combo.currentIndexChanged.connect(self.load_recipes)
        filter_layout.addWidget(self.sort_combo)
        
        main_layout.addLayout(filter_layout)

        # Таблиця
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Назва", "Категорія", "Час (хв)", "Калорії"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemDoubleClicked.connect(self.view_selected_recipe)
        main_layout.addWidget(self.table)

        # Кнопки дії
        btn_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("Додати рецепт")
        self.btn_add.setStyleSheet("background-color: #A6E3A1; color: #11111B;")
        self.btn_add.clicked.connect(self.add_recipe_dialog)
        btn_layout.addWidget(self.btn_add)

        self.btn_view = QPushButton("Переглянути деталі")
        self.btn_view.setStyleSheet("background-color: #89B4FA; color: #11111B;")
        self.btn_view.clicked.connect(self.view_selected_recipe)
        btn_layout.addWidget(self.btn_view)

        self.btn_edit = QPushButton("Редагувати")
        self.btn_edit.setStyleSheet("background-color: #FAB387; color: #11111B;")
        self.btn_edit.clicked.connect(self.edit_selected_recipe)
        btn_layout.addWidget(self.btn_edit)

        self.btn_random = QPushButton("🎲 Що приготувати?")
        self.btn_random.setStyleSheet("background-color: #94E2D5; color: #11111B;")
        self.btn_random.clicked.connect(self.show_random_recipe)
        btn_layout.addWidget(self.btn_random)

        self.btn_planner = QPushButton("Планування меню")
        self.btn_planner.setStyleSheet("background-color: #CBA6F7; color: #11111B;")
        self.btn_planner.clicked.connect(self.open_meal_planner)
        btn_layout.addWidget(self.btn_planner)

        self.btn_delete = QPushButton("Видалити обраний рецепт")
        self.btn_delete.setStyleSheet("background-color: #F38BA8; color: #11111B;")
        self.btn_delete.clicked.connect(self.delete_selected_recipe)
        btn_layout.addWidget(self.btn_delete)

        main_layout.addLayout(btn_layout)

        # Рядок стану (Status Bar)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def load_recipes(self):
        query = self.search_input.text().strip()
        category = self.category_filter_combo.currentText()
        sort_by = self.sort_combo.currentData()
        
        recipes = self.db.get_all_recipes(search_query=query, category_filter=category, sort_by=sort_by)
        
        self.table.setRowCount(0)
        for row_idx, recipe in enumerate(recipes):
            self.table.insertRow(row_idx)
            for col_idx, data in enumerate(recipe):
                item = QTableWidgetItem(str(data))
                self.table.setItem(row_idx, col_idx, item)

        # Оновлення статусу
        count = len(recipes)
        self.status_bar.showMessage(f" Всього рецептів у базі: {count}")

    def add_recipe_dialog(self):
        dialog = RecipeDialog(self)
        dialog.setStyleSheet(MODERN_STYLE)
        if dialog.exec_():
            name, category, prep_time, calories, instructions, ingredients_str = dialog.get_data()
            self.db.add_recipe(name, category, prep_time, calories, instructions, ingredients_str)
            self.load_recipes()

    def view_selected_recipe(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Увага", "Будь ласка, оберіть рецепт для перегляду!")
            return

        recipe_id = int(self.table.item(selected_row, 0).text())
        recipe_data = self.db.get_recipe_by_id(recipe_id)
        ingredients_str = self.db.get_recipe_ingredients(recipe_id)

        if recipe_data:
            dialog = RecipeDetailDialog(recipe_data, ingredients_str, self)
            dialog.setStyleSheet(MODERN_STYLE)
            dialog.exec_()

    def show_random_recipe(self):
        random_recipe = self.db.get_random_recipe()
        if not random_recipe:
            QMessageBox.warning(self, "Увага", "У базі даних немає жодного рецепта!")
            return

        recipe_id = random_recipe[0]
        ingredients_str = self.db.get_recipe_ingredients(recipe_id)

        dialog = RecipeDetailDialog(random_recipe, ingredients_str, self)
        dialog.setStyleSheet(MODERN_STYLE)
        dialog.setWindowTitle(f"🎲 Пропозиція: {random_recipe[1]}")
        dialog.exec_()

    def edit_selected_recipe(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Увага", "Будь ласка, оберіть рецепт для редагування!")
            return

        recipe_id = int(self.table.item(selected_row, 0).text())
        recipe_data = self.db.get_recipe_by_id(recipe_id)
        ingredients_str = self.db.get_recipe_ingredients(recipe_id)

        if recipe_data:
            dialog = RecipeDialog(self, recipe_data=recipe_data, ingredients_str=ingredients_str)
            dialog.setStyleSheet(MODERN_STYLE)
            if dialog.exec_():
                name, category, prep_time, calories, instructions, new_ingredients_str = dialog.get_data()
                self.db.update_recipe(recipe_id, name, category, prep_time, calories, instructions, new_ingredients_str)
                self.load_recipes()

    def open_meal_planner(self):
        dialog = MealPlannerDialog(self.db, self)
        dialog.setStyleSheet(MODERN_STYLE)
        dialog.exec_()

    def delete_selected_recipe(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Увага", "Будь ласка, оберіть рецепт для видалення!")
            return

        recipe_id = int(self.table.item(selected_row, 0).text())
        recipe_name = self.table.item(selected_row, 1).text()

        confirm = QMessageBox.question(
            self, "Підтвердження", 
            f"Ви дійсно бажаєте видалити рецепт '{recipe_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            self.db.delete_recipe(recipe_id)
            self.load_recipes()