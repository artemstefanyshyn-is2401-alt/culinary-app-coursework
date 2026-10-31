import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QSpinBox, QMessageBox, QFileDialog
)
from PyQt5.QtGui import QTextDocument
from PyQt5.QtPrintSupport import QPrinter

class RecipeDetailDialog(QDialog):
    def __init__(self, recipe_data, ingredients_str="", parent=None):
        super().__init__(parent)
        # recipe_data: (id, name, category, prep_time, calories, instructions)
        self.recipe_data = recipe_data
        self.original_ingredients = ingredients_str
        self.setWindowTitle(f"Рецепт: {self.recipe_data[1]}")
        self.resize(520, 580)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Назва рецепта
        title_label = QLabel(self.recipe_data[1])
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #89B4FA;")
        layout.addWidget(title_label)

        # Основна інформація та кольоровий індикатор калорій
        calories = int(self.recipe_data[4])
        if calories < 200:
            cal_color = "#A6E3A1"  # Зелений (Низькокалорійне)
            cal_status = "Низька калорійність"
        elif calories <= 350:
            cal_color = "#FAB387"  # Помаранчевий (Середня)
            cal_status = "Середня калорійність"
        else:
            cal_color = "#F38BA8"  # Червоний (Висока)
            cal_status = "Висока калорійність"

        info_text = (
            f"<b>Категорія:</b> {self.recipe_data[2]} | "
            f"<b>Час приготування:</b> {self.recipe_data[3]} хв<br>"
            f"<b>Калорійність:</b> <span style='color: {cal_color}; font-weight: bold;'>{calories} ккал ({cal_status})</span>"
        )
        info_label = QLabel(info_text)
        info_label.setStyleSheet("font-size: 13px;")
        layout.addWidget(info_label)

        # Калькулятор порцій
        portion_layout = QHBoxLayout()
        portion_layout.addWidget(QLabel("<b>Кількість порцій:</b>"))
        self.portion_spin = QSpinBox()
        self.portion_spin.setRange(1, 20)
        self.portion_spin.setValue(1)
        self.portion_spin.valueChanged.connect(self.update_portions)
        portion_layout.addWidget(self.portion_spin)
        portion_layout.addStretch()
        layout.addLayout(portion_layout)

        # Інгредієнти
        layout.addWidget(QLabel("<b>Інгредієнти:</b>"))
        self.ingredients_display = QTextEdit()
        self.ingredients_display.setReadOnly(True)
        self.ingredients_display.setMaximumHeight(100)
        layout.addWidget(self.ingredients_display)

        # Інструкції
        layout.addWidget(QLabel("<b>Інструкція приготування:</b>"))
        self.instructions_display = QTextEdit()
        self.instructions_display.setReadOnly(True)
        self.instructions_display.setPlainText(str(self.recipe_data[5]))
        layout.addWidget(self.instructions_display)

        self.update_portions()

        # Кнопки Друку/PDF та Закриття
        btn_layout = QHBoxLayout()
        
        btn_pdf = QPushButton("📄 Зберегти в PDF")
        btn_pdf.setStyleSheet("background-color: #89B4FA; color: #11111B; font-weight: bold;")
        btn_pdf.clicked.connect(self.export_to_pdf)
        btn_layout.addWidget(btn_pdf)

        btn_close = QPushButton("Закрити")
        btn_close.setStyleSheet("background-color: #45475A; color: white;")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)

    def update_portions(self):
        """Перерахунок кількості інгредієнтів залежно від обраних порцій"""
        portions = self.portion_spin.value()
        if not self.original_ingredients:
            self.ingredients_display.setPlainText("— Не вказано —")
            return

        items = [i.strip() for i in self.original_ingredients.split(",") if i.strip()]
        scaled_items = []

        for item in items:
            match = re.search(r'(\d+)', item)
            if match:
                num = int(match.group(1))
                new_num = num * portions
                scaled_item = item.replace(str(num), str(new_num), 1)
                scaled_items.append(scaled_item)
            else:
                scaled_items.append(f"{item} (х{portions})" if portions > 1 else item)

        self.ingredients_display.setPlainText("\n".join([f"• {i}" for i in scaled_items]))

    def export_to_pdf(self):
        """Експорт рецепта у PDF документ"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Зберегти у PDF", f"{self.recipe_data[1]}.pdf", "PDF Files (*.pdf)")
        if file_path:
            doc = QTextDocument()
            html_content = f"""
            <h1 style='color: #2B2D42;'>{self.recipe_data[1]}</h1>
            <p><b>Категорія:</b> {self.recipe_data[2]} | <b>Час:</b> {self.recipe_data[3]} хв | <b>Калорії:</b> {self.recipe_data[4]} ккал</p>
            <hr>
            <h3>Інгредієнти (порцій: {self.portion_spin.value()}):</h3>
            <p>{self.ingredients_display.toPlainText().replace('\n', '<br>')}</p>
            <h3>Інструкція приготування:</h3>
            <p>{self.recipe_data[5]}</p>
            """
            doc.setHtml(html_content)
            
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)
            doc.print_(printer)

            QMessageBox.information(self, "Успіх", "Рецепт успішно збережено у форматі PDF!") 