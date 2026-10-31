MODERN_STYLE = """
QMainWindow, QDialog {
    background-color: #1E1E2E;
    color: #CDD6F4;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QLabel {
    color: #CDD6F4;
    font-size: 13px;
}

QLineEdit, QTextEdit, QSpinBox, QComboBox {
    background-color: #313244;
    color: #CDD6F4;
    border: 1px solid #45475A;
    border-radius: 6px;
    padding: 6px;
    selection-background-color: #CBA6F7;
}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #89B4FA;
}

QTableWidget {
    background-color: #181825;
    color: #CDD6F4;
    gridline-color: #313244;
    border: 1px solid #45475A;
    border-radius: 6px;
    selection-background-color: #45475A;
    selection-color: #89B4FA;
}

QHeaderView::section {
    background-color: #313244;
    color: #CBA6F7;
    font-weight: bold;
    padding: 6px;
    border: none;
}

QPushButton {
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: bold;
    font-size: 13px;
}

QPushButton:hover {
    opacity: 0.8;
}
"""