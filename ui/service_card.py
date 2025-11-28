# ui/service_card.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtGui import QPixmap, QFont, QColor, QPainter, QPen
from PyQt6.QtCore import Qt, pyqtSignal, QRect
from config import (
    COLOR_ATTENTION, COLOR_MAIN, COLOR_SECONDARY, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_PRICE, COLOR_DISCOUNT, COLOR_BUTTON_BOOK, COLOR_BUTTON_ADMIN,
    COLOR_BUTTON_DANGER, FONT_FAMILY, rgb_to_hex
)


class StrikethroughLabel(QLabel):
    def __init__(self, text=""):
        super().__init__(text)
        self.setFont(QFont(FONT_FAMILY, 12))
        self.setStyleSheet(f"color: {rgb_to_hex(COLOR_TEXT_SECONDARY)};")

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        pen = QPen(QColor(*COLOR_TEXT_SECONDARY), 1.5)
        painter.setPen(pen)
        y = self.height()  // 2
        painter.drawLine(6, y, self.width() - 6, y) # отступы по краям


class ServiceCard(QWidget):
    edit_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    book_requested = pyqtSignal(int)

    def __init__(self, 
                 service_id: int,
                 title: str,
                 base_price: float,
                 discount_percent: int = 0,
                 duration_min: int = 0,
                 image_path: str = None,
                 is_admin_mode: bool = False,
                 parent=None):
        super().__init__(parent)
        self.service_id = service_id
        self.base_price = base_price
        self.discount_percent = discount_percent

        self._admin_mode = is_admin_mode
        self._button_layout = None  # будем переключать кнопки

        self.setup_ui(title, duration_min, image_path)

    def setup_ui(self, title, duration_min, image_path):
        self.setFixedHeight(190)
        self.setStyleSheet(f"""
            background-color: {rgb_to_hex(COLOR_MAIN)};
            border-radius: 16px;
            border: 1px solid {rgb_to_hex((235, 238, 245))};
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(24)

        # Фото
        self.image_label = QLabel()
        self.image_label.setFixedSize(140, 140)
        self.image_label.setStyleSheet(f"background-color: {rgb_to_hex((248, 249, 250))}; border-radius: 12px;")
        if image_path and not QPixmap(image_path).isNull():
            pixmap = QPixmap(image_path).scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("📷")
            self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.image_label.setFont(QFont(FONT_FAMILY, 28))
            self.image_label.setStyleSheet(f"color: {rgb_to_hex((200, 200, 200))};")

        # Правая часть
        right = QVBoxLayout()
        right.setSpacing(10)

        # Название
        title_label = QLabel(title)
        title_label.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {rgb_to_hex(COLOR_TEXT_PRIMARY)};")
        title_label.setWordWrap(True)
        right.addWidget(title_label)

        # Цены — компактно и красиво
        price_layout = QHBoxLayout()
        price_layout.setSpacing(8)

        if self.discount_percent > 0:
            discounted = self.base_price * (1 - self.discount_percent / 100)
            
            # Старая цена — серым, зачёркнутой
            old = StrikethroughLabel(f"{self.base_price:.0f}₽")
            old.setFont(QFont(FONT_FAMILY, 13))
            price_layout.addWidget(old)

            # Новая цена — жирным, цветом внимания
            new = QLabel(f"{discounted:.0f}₽")
            new.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
            new.setStyleSheet(f"color: {rgb_to_hex(COLOR_ATTENTION)};")
            price_layout.addWidget(new)

            # Скидка — маленький бейджик
            badge = QLabel(f"-{self.discount_percent}%")
            badge.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
            badge.setStyleSheet(f"""
                background-color: {rgb_to_hex(COLOR_ATTENTION)};
                color: white;
                border-radius: 8px;
                padding: 2px 8px;
            """)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            price_layout.addWidget(badge)
            price_layout.addStretch()
        else:
            # Обычная цена — серым, но чуть темнее
            price_lbl = QLabel(f"{self.base_price:.0f}₽")
            price_lbl.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.DemiBold))
            price_lbl.setStyleSheet(f"color: {rgb_to_hex((120, 120, 120))};")
            price_layout.addWidget(price_lbl)
            price_layout.addStretch()

        right.addLayout(price_layout)

        # Время
        if duration_min > 0:
            time_lbl = QLabel(f"⏱ {duration_min} мин")
            time_lbl.setFont(QFont(FONT_FAMILY, 11))
            time_lbl.setStyleSheet(f"color: {rgb_to_hex(COLOR_TEXT_SECONDARY)};")
            right.addWidget(time_lbl)

        right.addStretch()

        # Кнопки — отдельный layout, чтобы можно было заменить
        self._button_layout = QHBoxLayout()
        self._button_layout.setSpacing(12)
        self._update_buttons()
        right.addLayout(self._button_layout)

        layout.addWidget(self.image_label)
        layout.addLayout(right)
        self.setLayout(layout)

    def _update_buttons(self):
        # Очистим старые кнопки
        while self._button_layout.count():
            child = self._button_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if self._admin_mode:
            edit_btn = QPushButton("✏ Редактировать")
            edit_btn.setFixedHeight(38)
            edit_btn.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Medium))
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {rgb_to_hex(COLOR_BUTTON_ADMIN)};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 0 18px;
                }}
                QPushButton:hover {{
                    background-color: {rgb_to_hex((19, 94, 167))};
                }}
            """)
            edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.service_id))

            del_btn = QPushButton("🗑 Удалить")
            del_btn.setFixedHeight(38)
            del_btn.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Medium))
            del_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {rgb_to_hex(COLOR_BUTTON_DANGER)};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 0 18px;
                }}
                QPushButton:hover {{
                    background-color: {rgb_to_hex((179, 40, 40))};
                }}
            """)
            del_btn.clicked.connect(lambda: self.delete_requested.emit(self.service_id))

            book_btn = QPushButton("📋 Записать")
            book_btn.setFixedHeight(38)
            book_btn.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Medium))
            book_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {rgb_to_hex(COLOR_BUTTON_BOOK)};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 0 18px;
                }}
                QPushButton:hover {{
                    background-color: {rgb_to_hex((46, 110, 52))};
                }}
            """)
            book_btn.clicked.connect(lambda: self.book_requested.emit(self.service_id))


            self._button_layout.addWidget(edit_btn)
            self._button_layout.addWidget(del_btn)
            self._button_layout.addWidget(book_btn)
        else:
            pass

    def set_admin_mode(self, is_admin: bool):
        """Переключает режим без пересоздания карточки"""
        self._admin_mode = is_admin
        self._update_buttons()