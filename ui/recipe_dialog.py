from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QTextEdit, QSpinBox, QPushButton, 
    QMessageBox, QComboBox
)

class RecipeDialog(QDialog):
    CATEGORIES = [
        "Перші страви", 
        "Основні страви", 
        "Салати", 
        "Закуски", 
        "Десерти", 
        "Напої"
    ]

    def __init__(self, parent=None, recipe_data=None, ingredients_str=""):
        super().__init__(parent)
        self.recipe_data = recipe_data
        self.ingredients_str = ingredients_str
        
        if self.recipe_data:
            self.setWindowTitle("Редагувати рецепт")
        else:
            self.setWindowTitle("Додати новий рецепт")

        self.resize(450, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Назва
        layout.addWidget(QLabel("Назва рецепта:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        # Категорія (Спадний список QComboBox)
        layout.addWidget(QLabel("Категорія:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(self.CATEGORIES)
        self.category_combo.setEditable(True)  # Дозволяє вписати власну категорію, якщо потрібної немає у списку
        layout.addWidget(self.category_combo)

        # Час приготування та калорії
        row_layout = QHBoxLayout()
        
        time_layout = QVBoxLayout()
        time_layout.addWidget(QLabel("Час (хв):"))
        self.time_spin = QSpinBox()
        self.time_spin.setRange(1, 1440)
        self.time_spin.setValue(30)
        time_layout.addWidget(self.time_spin)
        row_layout.addLayout(time_layout)

        cal_layout = QVBoxLayout()
        cal_layout.addWidget(QLabel("Калорії (ккал):"))
        self.cal_spin = QSpinBox()
        self.cal_spin.setRange(0, 5000)
        self.cal_spin.setValue(250)
        cal_layout.addWidget(self.cal_spin)
        row_layout.addLayout(cal_layout)

        layout.addLayout(row_layout)

        # Інгредієнти
        layout.addWidget(QLabel("Інгредієнти (через кому):"))
        self.ingredients_input = QLineEdit()
        self.ingredients_input.setPlaceholderText("наприклад: Картопля, М'ясо, Цибуля")
        layout.addWidget(self.ingredients_input)

        # Інструкція
        layout.addWidget(QLabel("Інструкція приготування:"))
        self.instructions_input = QTextEdit()
        layout.addWidget(self.instructions_input)

        # Кнопки збереження/скасування
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Зберегти")
        btn_save.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        btn_save.clicked.connect(self.accept_data)
        
        btn_cancel = QPushButton("Скасувати")
        btn_cancel.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        # Якщо режим редагування — заповнюємо поля
        if self.recipe_data:
            # recipe_data: (id, name, category, prep_time, calories, instructions)
            self.name_input.setText(str(self.recipe_data[1]))
            
            category_val = str(self.recipe_data[2])
            idx = self.category_combo.findText(category_val)
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)
            else:
                self.category_combo.setEditText(category_val)

            self.time_spin.setValue(int(self.recipe_data[3]))
            self.cal_spin.setValue(int(self.recipe_data[4]))
            self.instructions_input.setPlainText(str(self.recipe_data[5]))
            self.ingredients_input.setText(self.ingredients_str)

    def accept_data(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть назву рецепта!")
            return
        self.accept()

    def get_data(self):
        return (
            self.name_input.text().strip(),
            self.category_combo.currentText().strip(),
            self.time_spin.value(),
            self.cal_spin.value(),
            self.instructions_input.toPlainText().strip(),
            self.ingredients_input.text().strip()
        )