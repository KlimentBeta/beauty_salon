# main.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QScrollArea, QFrame,
    QPushButton, QHBoxLayout, QLabel, QDialog  
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from config import (
    COLOR_BUTTON_ADMIN, LOGO_PATH, FONT_FAMILY, COLOR_SECONDARY, COLOR_ATTENTION, rgb_to_hex
)
from ui.service_card import ServiceCard
from ui.login_dialog import LoginDialog
from db import Database


db = Database()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beauty Salon")
        self.resize(1200, 800)
        self.is_admin = False
        self.service_cards = []  

        self.services = db.fetch_all("Service")
        
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        header = QFrame()
        header.setStyleSheet(f"background-color: {rgb_to_hex(COLOR_SECONDARY)};")
        header.setFixedHeight(80)
        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(30, 0, 30, 0)

        logo = QLabel()
        logo.setPixmap(QPixmap(LOGO_PATH).scaled(48, 48))
        logo.setFont(QFont(FONT_FAMILY, 24))  # можно оставить, если нужно fallback-отображение текста при ошибке
        hlayout.addWidget(logo)

        title = QLabel("Beauty Salon")
        title.setFont(QFont(FONT_FAMILY, 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {rgb_to_hex((50, 50, 70))};")
        hlayout.addWidget(title)
        hlayout.addStretch()

        self.login_btn = QPushButton("🔐 Войти как администратор")
        self.login_btn.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Medium))
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {rgb_to_hex(COLOR_ATTENTION)};
                color: white;
                border: none;
                border-radius: 20px;
                padding: 8px 24px;
            }}
            QPushButton:hover {{
                background-color: {rgb_to_hex((220, 50, 90))};
            }}
        """)
        self.login_btn.clicked.connect(self.show_login)
        hlayout.addWidget(self.login_btn)

        header.setLayout(hlayout)
        main_layout.addWidget(header)

                # === Кнопка "Добавить услугу" (только для админа) ===
        self.add_service_btn = QPushButton("➕ Добавить новую услугу")
        self.add_service_btn.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        self.add_service_btn.setFixedHeight(44)
        self.add_service_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {rgb_to_hex(COLOR_BUTTON_ADMIN)};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 0 24px;
            }}
            QPushButton:hover {{
                background-color: {rgb_to_hex((19, 94, 167))};
            }}
        """)
        self.add_service_btn.clicked.connect(self.on_add_service)
        self.add_service_btn.setVisible(self.is_admin)  # скрыть по умолчанию
        main_layout.addWidget(self.add_service_btn)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QFrame()
        container.setStyleSheet(f"background-color: {rgb_to_hex((245, 247, 255))};")
        container_layout = QVBoxLayout()
        container_layout.setSpacing(30)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.service_cards.clear()
        for srv in self.services:
            # Расчёт скидки в %
            discount_factor = float(srv.get('Discount', 1.0))
            discount_percent = 0
            if discount_factor < 1.0:
                discount_percent = int((1 - discount_factor) * 100)

            # Цена до скидки
            base_price = float(srv['Cost'])

            # Время в минутах
            duration_min = srv['DurationInSeconds'] // 60 if srv.get('DurationInSeconds') else 0

            # Путь к фото (защита от None)
            image_path = srv.get('MainImagePath')
            if image_path and not isinstance(image_path, str):
                image_path = None

            # Создаём карточку
            card = ServiceCard(
                service_id=srv['ID'],
                title=srv['Title'],
                base_price=base_price,
                discount_percent=discount_percent,
                duration_min=duration_min,
                image_path=image_path,
                is_admin_mode=self.is_admin
            )
            card.edit_requested.connect(self.on_edit)
            card.delete_requested.connect(self.on_delete)
            container_layout.addWidget(card)
            self.service_cards.append(card)
            
        container.setLayout(container_layout)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def show_login(self):
        dialog = LoginDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.is_admin = True
            self.login_btn.setText("✅ Администратор")
            self.login_btn.setEnabled(False)
            self.login_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 20px;
                    padding: 8px 24px;
                }}
            """)
            self.refresh_cards()

    def refresh_cards(self):
        """Обновляем ТОЛЬКО кнопки в уже существующих карточках"""
        for card in self.service_cards:
            card.set_admin_mode(True)
        self.add_service_btn.setVisible(True)

    def on_edit(self, service_id: int):
        print(f"[Admin] Редактирование услуги ID: {service_id}")

    def on_delete(self, service_id: int):
        print(f"[Admin] Удаление услуги ID: {service_id}")

    def on_add_service(self, service_id: int):
        print(f"[Admin] Добавить услугу")

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont(FONT_FAMILY, 10))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())