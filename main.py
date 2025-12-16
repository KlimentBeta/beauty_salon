# main.py
import sys, os
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QScrollArea, QFrame,
    QPushButton, QHBoxLayout, QLabel, QDialog, QComboBox, QLineEdit, QDoubleSpinBox, QSpinBox, QTextEdit, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from config import (
    COLOR_BUTTON_ADMIN, LOGO_PATH, FONT_FAMILY, COLOR_SECONDARY, COLOR_ATTENTION, rgb_to_hex
)
from ui.book_service_dialog import BookServiceDialog
from ui.edit_service_dialog import EditServiceDialog
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

        self.original_central_widget = None  # или self.original_layout
        self.near_view_widget = None         # текущий "ближайший" UI
        self.is_near_view = False

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
                
        # control_layout = QHBoxLayout()
        # control_layout.setContentsMargins(30, 10, 30, 10)
        # === Панель управления: сортировка + фильтр ===
        # === Панель управления: сортировка + фильтр ===
        control_layout = QHBoxLayout()
        # ... настройка ...
        self.control_layout_widget = QFrame()
        self.control_layout_widget.setFixedHeight(60)
        self.control_layout_widget.setStyleSheet("background: transparent;")
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(30, 10, 30, 10)
        # ... (всё как было: search_label, search_input, discount_combo и т.д.) ...
        self.control_layout_widget.setLayout(control_layout)
        main_layout.addWidget(self.control_layout_widget)

        

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

                # === Кнопка "Ближайшие записи" (только для админа) ===
        self.near_service_btn = QPushButton("Ближайшие записи")
        self.near_service_btn.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        self.near_service_btn.setFixedHeight(44)
        self.near_service_btn.setStyleSheet(f"""
    QPushButton {{
background-color: {rgb_to_hex((74, 20, 140))};
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0 24px;
    }}
    QPushButton:hover {{
background-color: {rgb_to_hex((74, 20, 120))};
    }}
""")
        self.near_service_btn.clicked.connect(self.on_nearly_service)
        self.near_service_btn.setVisible(self.is_admin)  # скрыть по умолчанию
        main_layout.addWidget(self.near_service_btn)

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
        self.scroll_area = scroll
        
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
            discount_factor = float(srv.get('Discount') or 1.0)
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
            card.book_requested.connect(self.on_book)
            card.delete_requested.connect(self.on_delete)
            container_layout.addWidget(card)
            self.service_cards.append(card)
        

        container.setLayout(container_layout)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)


        # === Строка статуса внизу ===
        footer = QFrame()
        self.footer = footer
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

    def _return_to_services(self):
        if self.is_near_view and self.near_view_widget:
            # Удаляем временный виджет
            self.near_view_widget.setParent(None)
            self.near_view_widget.deleteLater()
            self.near_view_widget = None

            # Восстанавливаем оригинальный UI
            self.control_layout_widget.setVisible(True)
            self.scroll_area.setVisible(True)
            self.footer.setVisible(True)

            # Кнопки админа — показываем, если is_admin
            self.add_service_btn.setVisible(self.is_admin)
            self.near_service_btn.setVisible(self.is_admin)

            self.is_near_view = False

    def _build_near_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Заголовок
        title = QLabel("📅 Ближайшие записи")
        title.setFont(QFont(FONT_FAMILY, 18, QFont.Weight.Bold))
        layout.addWidget(title)

        # Здесь — ваша логика загрузки ближайших записей (например, SELECT FROM Booking WHERE ...)
        # Для примера — 3 фейковые записи:
        records = [
            {"user": "Анна", "service": "Маникюр", "time": "15 дек, 14:30"},
            {"user": "Мария", "service": "Стрижка", "time": "15 дек, 16:00"},
            {"user": "Елена", "service": "Окрашивание", "time": "16 дек, 10:15"},
        ]

        for rec in records:
            card = QFrame()
            card.setStyleSheet("background: white; border-radius: 10px; padding: 12px;")
            card_layout = QHBoxLayout()

            name_label = QLabel(f"<b>{rec['user']}</b>")
            service_label = QLabel(rec["service"])
            time_label = QLabel(f"<i>{rec['time']}</i>")

            card_layout.addWidget(name_label)
            card_layout.addWidget(service_label)
            card_layout.addStretch()
            card_layout.addWidget(time_label)
            card.setLayout(card_layout)
            layout.addWidget(card)

        # Кнопка "Назад"
        back_btn = QPushButton("← Назад к услугам")
        back_btn.setFont(QFont(FONT_FAMILY, 12))
        back_btn.setFixedHeight(40)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {rgb_to_hex(COLOR_BUTTON_ADMIN)};
                color: white;
                border: none;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: {rgb_to_hex((19, 94, 167))};
            }}
        """)
        back_btn.clicked.connect(self._return_to_services)
        layout.addWidget(back_btn)
        layout.addStretch()

        return widget

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
        self.near_service_btn.setVisible(True)
    
    def on_edit(self, service_id: int):
        print(f"[Admin] Редактирование услуги ID: {service_id}")
        arg = f"SELECT * FROM Service WHERE id = {service_id}"
        res = db.fetch_one(arg)  # предположим, возвращает list[dict] или None

        if not res:
            QMessageBox.warning(self, "Ошибка", f"Услуга с ID {service_id} не найдена.")
            return

        service_data = res[0]  # берем первую запись

        dialog = EditServiceDialog(service_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_data()
            # Пример UPDATE-запроса (рекомендуется использовать параметризованные запросы!)
            try:
                query = """
                    UPDATE Service
                    SET Title = %s, Cost = %s, DurationInSeconds = %s,
                        Discount = %s, MainImagePath = %s
                    WHERE ID = %s
                """
                params = (
                    updated_data['Title'],
                    updated_data['Cost'],
                    updated_data['DurationInSeconds'],
                    updated_data['Discount'],
                    updated_data['MainImagePath'],
                    updated_data['ID']
                )
                db.execute(query, params)  # предполагаем, что у вас есть execute с параметрами
                QMessageBox.information(self, "Успех", "Услуга успешно обновлена.")
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения:\n{e}")
        else:
            print("[Admin] Редактирование отменено.")

    def on_book(self, service_id: int):
        print(f"[Admin] Запись на услугу с ID: {service_id}")

        # ⚠️ Подстановка service_id в строку — только если вы 100% уверены, что service_id — int
        # (иначе — риск SQL-инъекции; но при вызове из UI, где service_id берётся из ID записи — безопасно)
        res = db.fetch_one(f"SELECT * FROM Service WHERE ID = {int(service_id)}")
        if not res:
            QMessageBox.warning(self, "Ошибка", f"Услуга ID {service_id} не найдена.")
            return
        service_data = res[0]  # ← fetch_one возвращает список, берём первый элемент

        # Загрузка клиентов
        client_res = db.fetch_one("SELECT ID, LastName, FirstName, Patronymic FROM Client ORDER BY LastName, FirstName")
        clients = []
        for row in client_res:  # client_res — список, даже если 0 строк
            fio = f"{row['LastName']} {row['FirstName']} {row['Patronymic'] or ''}".strip()
            clients.append((row['ID'], fio))

        if not clients:
            QMessageBox.warning(self, "Внимание", "Нет доступных клиентов.")
            return

        dialog = BookServiceDialog(service_data, clients, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                data = dialog.get_data()
                # Экранируем апострофы в дате (на всякий случай), хотя формат yyyy-MM-dd HH:MM:SS безопасен
                start_escaped = data['StartTime'].replace("'", "''")
                
                query = (
                    f"INSERT INTO ClientService (ClientID, ServiceID, StartTime) "
                    f"VALUES ({int(data['ClientID'])}, {int(data['ServiceID'])}, '{start_escaped}')"
                )
                success = db.execute(query)
                if success:
                    QMessageBox.information(self, "Успех", "Клиент записан.")
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось сохранить запись.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Сбой: {e}")
        else:
            print("[Admin] Запись отменена.")

    def on_delete(self, service_id: int):
        print(f"[Admin] Удаление услуги ID: {service_id}")

        success, message = db.delete_service(service_id)  # ← предполагаем, что возвращает (bool, str)

        if success:
            QMessageBox.information(
                self,
                "✅ Удалено",
                f"Услуга с ID {service_id} успешно удалена."
            )
            print(f"[Admin] Услуга ID {service_id} удалена.")
            self.update_screen()
        else:
            QMessageBox.warning(
                self,
                "⛔ Удаление невозможно",
                f"Не удалось удалить услугу:\n{message}"
            )
            # ❗ Не вызываем self.update_screen(), т.к. данные не изменились
            print(f"[Admin] Удаление отклонено: {message}")

    def on_nearly_service(self, service_id: int):
        print(f"[Admin] Ближайшие записи")
        if not self.is_near_view:
            # Скрываем текущие виджеты: control panel, scroll area, footer, доп.кнопки
            self.control_layout_widget.setVisible(False)  # см. ниже: вынесем control_layout в widget
            self.scroll_area.setVisible(False)
            self.footer.setVisible(False)
            self.add_service_btn.setVisible(False)
            self.near_service_btn.setVisible(False)

            # Создаём новый UI для "Ближайших записей"
            self.near_view_widget = self._build_near_view()
            self.layout().addWidget(self.near_view_widget)
            self.near_view_widget.setVisible(True)

            self.is_near_view = True


    def on_add_service(self):
        print(f"[Admin] Добавить услугу")
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить новую услугу")
        dialog.setModal(True)
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout(dialog)

        # Поля ввода
        title_edit = QLineEdit()
        cost_edit = QDoubleSpinBox()
        cost_edit.setRange(0, 1_000_000)
        cost_edit.setDecimals(2)
        duration_edit = QSpinBox()
        duration_edit.setRange(0, 24 * 3600)  # до 24 часов в секундах
        desc_edit = QTextEdit()
        discount_edit = QDoubleSpinBox()
        discount_edit.setRange(0, 100)
        discount_edit.setSuffix(" %")
        discount_edit.setDecimals(1)
        image_path_edit = QLineEdit()
        image_path_edit.setReadOnly(True)
        browse_btn = QPushButton("Выбрать изображение...")

        # Макеты для строк
        def add_row(label_text, widget):
            row = QHBoxLayout()
            row.addWidget(QLabel(label_text))
            row.addWidget(widget, 1)
            layout.addLayout(row)

        add_row("Название*", title_edit)
        add_row("Стоимость*", cost_edit)
        add_row("Длительность, сек*", duration_edit)
        layout.addWidget(QLabel("Описание"))
        layout.addWidget(desc_edit)
        add_row("Скидка (%)", discount_edit)

        image_row = QHBoxLayout()
        image_row.addWidget(QLabel("Основное изображение"))
        image_row.addWidget(image_path_edit, 1)
        image_row.addWidget(browse_btn)
        layout.addLayout(image_row)

        # Кнопки
        btns = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

        # Обработчик выбора изображения
        def on_browse():
            file_path, _ = QFileDialog.getOpenFileName(
                dialog,
                "Выберите изображение",
                "",
                "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
            )
            if file_path:
                # Можно сразу копировать в assets/ и сохранять относительный путь — здесь просто путь
                image_path_edit.setText(file_path)

        browse_btn.clicked.connect(on_browse)

        # Обработчик сохранения
        def on_save():
            title = title_edit.text().strip()
            cost = cost_edit.value()
            duration = duration_edit.value()
            description = desc_edit.toPlainText().strip() or None
            discount = discount_edit.value() or None
            image_path = image_path_edit.text().strip() or None

            # Валидация обязательных полей
            errors = []
            if not title:
                errors.append("Название не может быть пустым")
            if len(title) > 100:
                errors.append("Название не должно превышать 100 символов")
            if cost <= 0:
                errors.append("Стоимость должна быть положительной")
            if duration <= 0:
                errors.append("Длительность должна быть положительной")

            if errors:
                QMessageBox.warning(dialog, "Ошибка ввода", "\n".join(errors))
                return

            # ⚠️ Опционально: копирование файла в assets и получение относительного пути
            # Например: 'assets/services/logo123.jpg'
            final_image_path = None
            if image_path and os.path.isfile(image_path):
                try:
                    # Генерируем уникальное имя файла или используем title
                    from pathlib import Path
                    filename = f"{Path(title).stem}_{hash(image_path) % 10000}.jpg"
                    dest_dir = "assets/service_photo"
                    os.makedirs(dest_dir, exist_ok=True)
                    dest_path = os.path.join(dest_dir, filename)

                    # Копируем (можно сжать/конвертировать при желании)
                    from shutil import copy2
                    copy2(image_path, dest_path)

                    final_image_path = dest_path.replace("\\", "/")  # для кросс-платформенности
                except Exception as e:
                    QMessageBox.critical(dialog, "Ошибка", f"Не удалось сохранить изображение:\n{e}")
                    return

            # Вызов db.add_service — ожидаем сигнатуру:
            try:
                service_id_new = db.add_service(
                    Title=title,
                    Cost=cost,
                    DurationInSeconds=duration,
                    Description=description,
                    Discount=1 - discount / 100 if discount is not None else None,  
                    MainImagePath=final_image_path
                )
                if service_id_new:
                    QMessageBox.information(dialog, "Успех", f"Услуга '{title}' добавлена")
                    dialog.accept()
                    self.services = db.fetch_all("Service")
                    self.update_screen() 
                else:
                    QMessageBox.critical(dialog, "Ошибка", "Не удалось добавить услугу в базу данных.")
            except Exception as e:
                QMessageBox.critical(dialog, "Исключение", f"Ошибка при добавлении услуги:\n{e}")

        save_btn.clicked.connect(on_save)
        cancel_btn.clicked.connect(dialog.reject)

        dialog.exec()

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


    def update_screen(self):
        # Загрузка данных
        self.services = db.fetch_all("SELECT * FROM Service")  # ← важно: fetch_all, а не "Service"
        if not self.services:
            self.services = []

        count_res = db.fetch_one("SELECT COUNT(*) AS cnt FROM Service")
        self.total_service_count = count_res[0]["cnt"] if count_res else 0

        self.apply_all_filters()

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
            discount_factor = float(srv.get('Discount') or 1.0)
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
            card.book_requested.connect(self.on_book)
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