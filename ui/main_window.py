from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame,
    QPushButton, QHBoxLayout, QLabel, QDialog, 
    QComboBox, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from config import COLOR_SECONDARY, COLOR_ATTENTION, COLOR_BUTTON_ADMIN, LOGO_PATH, rgb_to_hex, FONT_FAMILY
from ui.dialogs.login_dialog import LoginDialog
from ui.dialogs.add_service_dialog import AddServiceDialog
from ui.dialogs.edit_service_dialog import EditServiceDialog
from ui.dialogs.book_service_dialog import BookServiceDialog
from typing import Optional
from ui.utils.sort_services import sort_services_by_cost, filter_services_by_discount, DISCOUNT_RANGES, search_services
from ui.service_card import ServiceCard
from ui.utils.sort_services import DISCOUNT_RANGES
from ui.utils.near_records_view import NearRecordsView
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
        self.discount_filter_value = "Все"
        self.search_query = ""
        self.total_service_count = db.fetch_one("SELECT COUNT(*) AS cnt FROM Service")[0]["cnt"]
        
        self.is_near_view = False
        self.near_view_widget = None
        
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Создаем основные компоненты
        self.create_header(main_layout)
        self.create_control_panel(main_layout)
        self.create_admin_buttons(main_layout)
        self.create_service_list(main_layout)
        self.create_footer(main_layout)

        self.setLayout(main_layout)
        self._update_count_label(len(self.services))

    def create_header(self, parent_layout):
        header = QFrame()
        header.setStyleSheet(f"background-color: {rgb_to_hex(COLOR_SECONDARY)};")
        header.setFixedHeight(80)
        
        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(30, 0, 30, 0)

        # Логотип
        logo = QLabel()
        logo.setPixmap(QPixmap(LOGO_PATH).scaled(48, 48))
        hlayout.addWidget(logo)

        # Заголовок
        title = QLabel("Beauty Salon")
        title.setFont(QFont(FONT_FAMILY, 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {rgb_to_hex((50, 50, 70))};")
        hlayout.addWidget(title)
        hlayout.addStretch()

        # Кнопка входа
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
        parent_layout.addWidget(header)

    def create_control_panel(self, parent_layout):
        self.control_layout_widget = QFrame()
        self.control_layout_widget.setFixedHeight(60)
        self.control_layout_widget.setStyleSheet("background: transparent;")
        
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(30, 10, 30, 10)

        # Поле поиска
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

        # Фильтр по скидке
        discount_label = QLabel("Скидка:")
        discount_label.setFont(QFont(FONT_FAMILY, 10))
        control_layout.addWidget(discount_label)

        self.discount_combo = QComboBox()
        self.discount_combo.setFont(QFont(FONT_FAMILY, 10))
        self.discount_combo.setFixedHeight(36)
        self.discount_combo.setFixedWidth(180)
        
        for label, _, _ in DISCOUNT_RANGES:
            self.discount_combo.addItem(label)

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

        control_layout.addSpacing(20)

        # Кнопки сортировки
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

        self.control_layout_widget.setLayout(control_layout)
        parent_layout.addWidget(self.control_layout_widget)

    def create_admin_buttons(self, parent_layout):
        # Кнопка "Ближайшие записи"
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
        self.near_service_btn.setVisible(self.is_admin)
        parent_layout.addWidget(self.near_service_btn)

        # Кнопка "Добавить услугу"
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
        self.add_service_btn.setVisible(self.is_admin)
        parent_layout.addWidget(self.add_service_btn)

    def create_service_list(self, parent_layout):
        scroll = QScrollArea()
        self.scroll_area = scroll
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QFrame()
        container.setStyleSheet(f"background-color: {rgb_to_hex((245, 247, 255))};")
        self.container_layout = QVBoxLayout()
        self.container_layout.setSpacing(30)
        self.container_layout.setContentsMargins(30, 30, 30, 30)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._populate_service_cards()
        container.setLayout(self.container_layout)
        scroll.setWidget(container)
        parent_layout.addWidget(scroll)

    def create_footer(self, parent_layout):
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
        parent_layout.addWidget(footer)

    def _populate_service_cards(self):
        self.service_cards.clear()
        for srv in self.services:
            discount_factor = float(srv.get('Discount') or 1.0)
            discount_percent = 0
            if discount_factor < 1.0:
                discount_percent = int((1 - discount_factor) * 100)

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
            self.container_layout.addWidget(card)
            self.service_cards.append(card)

    # Остальные методы (show_login, on_edit, on_book, on_delete, on_add_service, 
    # on_nearly_service, _return_to_services, on_search_changed, on_discount_filter_changed,
    # sort_by, apply_all_filters, update_screen, _update_service_cards, _update_count_label)
    # остаются как были, просто перенесены в этот файл
    
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


    def on_add_service(self):
        print("[Admin] Добавить услугу")
        
        dialog = AddServiceDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Диалог успешно закрыт, обновляем список услуг
            try:
                # Загружаем обновленные данные из БД
                self.services = db.fetch_all("Service")
                
                # Применяем текущие фильтры и сортировку
                self.apply_all_filters()
                
                # Обновляем счетчик
                count_res = db.fetch_one("SELECT COUNT(*) AS cnt FROM Service")
                self.total_service_count = count_res[0]["cnt"] if count_res else 0
                self._update_count_label(len(self.services))
                
                print("[Admin] Услуга успешно добавлена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить список услуг:\n{e}")
        else:
            print("[Admin] Добавление услуги отменено")

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
        self.services = db.fetch_all("Service")  # ← важно: fetch_all, а не "Service"
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

    # Методы управления состоянием
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
        for card in self.service_cards:
            card.set_admin_mode(True)
        self.add_service_btn.setVisible(True)
        self.near_service_btn.setVisible(True)

    def on_nearly_service(self):
        if not self.is_near_view:
            self.control_layout_widget.setVisible(False)
            self.scroll_area.setVisible(False)
            self.footer.setVisible(False)
            self.add_service_btn.setVisible(False)
            self.near_service_btn.setVisible(False)

            self.near_view_widget = NearRecordsView()
            self.near_view_widget.back_requested.connect(self._return_to_services)
            self.layout().addWidget(self.near_view_widget)
            self.is_near_view = True

    def _return_to_services(self):
        if self.is_near_view and self.near_view_widget:
            self.near_view_widget.setParent(None)
            self.near_view_widget.deleteLater()
            self.near_view_widget = None

            self.control_layout_widget.setVisible(True)
            self.scroll_area.setVisible(True)
            self.footer.setVisible(True)
            self.add_service_btn.setVisible(self.is_admin)
            self.near_service_btn.setVisible(self.is_admin)

            self.is_near_view = False