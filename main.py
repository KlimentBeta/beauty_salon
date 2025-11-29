# main.py
import sys
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QScrollArea, QFrame,
    QPushButton, QHBoxLayout, QLabel, QDialog, QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from config import (
    COLOR_BUTTON_ADMIN, LOGO_PATH, FONT_FAMILY, COLOR_SECONDARY, COLOR_ATTENTION, rgb_to_hex
)
from ui.service_card import ServiceCard
from ui.login_dialog import LoginDialog
from ui.utils.sort_services import sort_services_by_cost, filter_services_by_discount, DISCOUNT_RANGES, search_services
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
        self.current_sort_order = None

        self.discount_filter_value = "Все"  # текущий фильтр
        self.current_sort_order = None      # 'asc', 'desc', None

        self.search_query = "" 
        
        self.total_service_count = db.fetch_one("SELECT COUNT(*) AS cnt FROM Service")[0]["cnt"]
      
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


        # === Панель управления: сортировка + фильтр ===
                
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(30, 10, 30, 10)

        # === Поле поиска ===
        search_label = QLabel("🔍 Поиск:")
        search_label.setFont(QFont(FONT_FAMILY, 10))
        control_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setFont(QFont(FONT_FAMILY, 10))
        self.search_input.setPlaceholderText("Название или описание...")
        self.search_input.setFixedHeight(36)
        self.search_input.setFixedWidth(250)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 0 10px;
                border: 1px solid {rgb_to_hex(COLOR_SECONDARY)};
                border-radius: 6px;
                background: white;
                color: {rgb_to_hex((50, 50, 70))};
            }}
            QLineEdit:focus {{
                border-color: {rgb_to_hex(COLOR_BUTTON_ADMIN)};
            }}
        """)
        self.search_input.textChanged.connect(self.on_search_changed)
        control_layout.addWidget(self.search_input)

        control_layout.addSpacing(15)
        # → дальше идут discount_combo, кнопки и т.д.
        
        # Выпадающий список для скидки
        discount_label = QLabel("Скидка:")
        discount_label.setFont(QFont(FONT_FAMILY, 10))
        control_layout.addWidget(discount_label)

        self.discount_combo = QComboBox()
        self.discount_combo.setFont(QFont(FONT_FAMILY, 10))
        self.discount_combo.setFixedHeight(36)
        self.discount_combo.setFixedWidth(180)

        # Заполняем варианты
        for label, _, _ in DISCOUNT_RANGES:
            self.discount_combo.addItem(label)

        # Стилизация через шаблон (можно чуть упростить)
        combo_style = f"""
            QComboBox {{
                background-color: white;
                border: 1px solid {rgb_to_hex(COLOR_SECONDARY)};
                border-radius: 6px;
                padding: 0 10px;
                color: {rgb_to_hex((50, 50, 70))};
            }}
            QComboBox::drop-down {{
                width: 24px;
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                selection-background-color: {rgb_to_hex(COLOR_BUTTON_ADMIN)};
            }}
        """
        self.discount_combo.setStyleSheet(combo_style)
        self.discount_combo.currentTextChanged.connect(self.on_discount_filter_changed)
        control_layout.addWidget(self.discount_combo)

        # Разделитель
        control_layout.addSpacing(20)

        # Кнопки сортировки (как раньше, но чуть компактнее)
        self.sort_asc_btn = QPushButton("↑ По возрастанию")
        self.sort_asc_btn.setFont(QFont(FONT_FAMILY, 10))
        self.sort_asc_btn.setFixedHeight(36)
        self.sort_asc_btn.setFixedWidth(140)
        self.sort_asc_btn.clicked.connect(lambda: self.sort_by('asc'))
        
        self.sort_desc_btn = QPushButton("↓ По убыванию")
        self.sort_desc_btn.setFont(QFont(FONT_FAMILY, 10))
        self.sort_desc_btn.setFixedHeight(36)
        self.sort_desc_btn.setFixedWidth(140)
        self.sort_desc_btn.clicked.connect(lambda: self.sort_by('desc'))

        style_btn = f"""
            QPushButton {{
                background-color: {rgb_to_hex((245, 247, 255))};
                color: {rgb_to_hex((50, 50, 70))};
                border: 1px solid {rgb_to_hex(COLOR_SECONDARY)};
                border-radius: 6px;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background-color: {rgb_to_hex(COLOR_SECONDARY)};
                color: white;
            }}
        """
        self.sort_asc_btn.setStyleSheet(style_btn)
        self.sort_desc_btn.setStyleSheet(style_btn)

        control_layout.addWidget(self.sort_asc_btn)
        control_layout.addWidget(self.sort_desc_btn)
        control_layout.addStretch()

        main_layout.addLayout(control_layout)

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


        # === Строка статуса внизу ===
        footer = QFrame()
        footer.setFixedHeight(40)
        footer.setStyleSheet(f"background-color: {rgb_to_hex((240, 242, 250))}; border-top: 1px solid {rgb_to_hex(COLOR_SECONDARY)};")
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(30, 0, 30, 0)

        self.count_label = QLabel()
        self.count_label.setFont(QFont(FONT_FAMILY, 10))
        self.count_label.setStyleSheet(f"color: {rgb_to_hex((80, 80, 100))};")
        footer_layout.addWidget(self.count_label)
        footer_layout.addStretch()

        footer.setLayout(footer_layout)
        main_layout.addWidget(footer)
        
        # Инициализация счётчика
        self._update_count_label(len(self.services))

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
        # res = db.delete_service(service_id)
        # print(res)

    def on_add_service(self, service_id: int):
        print(f"[Admin] Добавить услугу")

    def on_search_changed(self, text: str):
        self.search_query = text
        self.apply_all_filters()

    def on_discount_filter_changed(self, text: str):
        self.discount_filter_value = text
        self.apply_all_filters()

    def sort_by(self, order: Optional[str]):
        self.current_sort_order = order
        self.apply_all_filters()

    def apply_all_filters(self):
        """
        Применяет: 
        1. Фильтр по скидке 
        2. Поиск по Title/Description 
        3. Сортировку по цене (если задана)
        """
        # 1. Фильтр по скидке
        filtered = filter_services_by_discount(self.services, self.discount_filter_value)

        # 2. Поиск по запросу
        searched = search_services(filtered, self.search_query)

        # 3. Сортировка (если нужна)
        if self.current_sort_order in ('asc', 'desc'):
            reverse = (self.current_sort_order == 'desc')
            searched = sort_services_by_cost(searched, reverse=reverse)

        # 4. Обновление UI
        self._update_service_cards(searched)

        # 5 Обновить счётчик
        self._update_count_label(len(searched))


    def _update_service_cards(self, services_list):
        """Обновляет порядок карточек в layout'е на основе нового списка."""
        container_layout = self.findChild(QScrollArea).widget().layout()
        
        # Удаляем все карточки из layout'а (но не уничтожаем объекты)
        while container_layout.count():
            item = container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)  # отсоединяем, но не удаляем
                # widget.deleteLater()  # ← не нужно, если переиспользуем

        self.service_cards.clear()

        # Создаём карточки заново в новом порядке
        for srv in services_list:
            discount_factor = float(srv.get('Discount', 1.0))
            discount_percent = int((1 - discount_factor) * 100) if discount_factor < 1.0 else 0
            base_price = float(srv['Cost'])
            duration_min = srv['DurationInSeconds'] // 60 if srv.get('DurationInSeconds') else 0
            image_path = srv.get('MainImagePath')
            if image_path and not isinstance(image_path, str):
                image_path = None

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

    def _update_count_label(self, displayed_count: int):
        """Обновляет надпись вида '23 из 450'."""
        text = f"{displayed_count} из {self.total_service_count}"
        self.count_label.setText(text)

    
    
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont(FONT_FAMILY, 10))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())