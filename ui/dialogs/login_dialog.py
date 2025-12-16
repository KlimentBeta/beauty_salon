# ui/login_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from config import FONT_FAMILY, COLOR_SECONDARY, COLOR_ATTENTION, rgb_to_hex


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация")
        self.setFixedSize(320, 180)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("🔐 Введите PIN-код")
        title.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.pin_input = QLineEdit()
        self.pin_input.setFont(QFont(FONT_FAMILY, 14))
        self.pin_input.setPlaceholderText("0000")
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setMaxLength(4)
        self.pin_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pin_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
            }
        """)
        layout.addWidget(self.pin_input)

        self.submit_btn = QPushButton("Войти")
        self.submit_btn.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        self.submit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {rgb_to_hex(COLOR_ATTENTION)};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {rgb_to_hex((220, 50, 90))};
            }}
        """)
        self.submit_btn.clicked.connect(self.check_pin)
        layout.addWidget(self.submit_btn)

        self.setLayout(layout)
        self.pin_input.returnPressed.connect(self.check_pin)

    def check_pin(self):
        if self.pin_input.text() == "0000":
            self.accept()  # закрыть с результатом OK
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный PIN-код.\nПопробуйте снова.")
            self.pin_input.clear()
            self.pin_input.setFocus()