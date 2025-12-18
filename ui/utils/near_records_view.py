from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QPushButton, QScrollArea
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont
from config import FONT_FAMILY, COLOR_BUTTON_ADMIN, rgb_to_hex
from datetime import datetime

class NearRecordsView(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

        # 🔁 Таймер автообновления: каждые 30 секунд
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(30_000)  # 30 секунд

        # Останавливаем таймер при удалении виджета (защита от утечек)
        self.destroyed.connect(lambda: self.refresh_timer.stop())

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Заголовок
        title = QLabel("📅 Ближайшие записи")
        title.setFont(QFont(FONT_FAMILY, 18, QFont.Weight.Bold))
        main_layout.addWidget(title)

        # Область прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        main_layout.addWidget(scroll_area)

        # Контейнер для карточек
        self.scroll_content = QWidget()
        self.records_layout = QVBoxLayout(self.scroll_content)
        self.records_layout.setContentsMargins(0, 0, 0, 0)
        self.records_layout.setSpacing(16)
        self.records_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        scroll_area.setWidget(self.scroll_content)

        # Первичная загрузка записей
        self.refresh()

        # Кнопка "Назад" — фиксированная внизу
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
        back_btn.clicked.connect(self.back_requested.emit)
        main_layout.addWidget(back_btn)
        main_layout.addStretch()

    def refresh(self):
        """Полное обновление списка записей: очистка + перезагрузка из БД + перерисовка."""
        # Очистка текущих карточек
        while self.records_layout.count():
            item = self.records_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Загрузка данных
        records = self.load_near_records()

        if not records:
            label = QLabel("📭 Нет ближайших записей.")
            label.setFont(QFont(FONT_FAMILY, 12))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setWordWrap(True)
            label.setMinimumHeight(60)
            self.records_layout.addWidget(label)
        else:
            for rec in records:
                card = self.create_record_card(rec)
                self.records_layout.addWidget(card)

    def load_near_records(self):
        """Загружает актуальные записи из БД."""
        now = datetime.now()
        query = """
            SELECT 
                cs.ID,
                cs.StartTime,
                cs.Comment,
                s.Title AS ServiceTitle,
                c.FirstName,
                c.LastName,
                c.Patronymic,
                c.Email,
                c.Phone
            FROM ClientService cs
            JOIN Service s ON cs.ServiceID = s.ID
            JOIN Client c ON cs.ClientID = c.ID
            WHERE cs.StartTime >= %s
            ORDER BY cs.StartTime ASC
        """
        try:
            cursor = self.db.conn.cursor(dictionary=True)
            cursor.execute(query, (now,))
            records = cursor.fetchall()
            cursor.close()
            return records
        except Exception as e:
            print(f"❌ Ошибка загрузки записей: {e}")
            return []

    def format_fio(self, first, last, patronymic=None):
        parts = [last, first]
        if patronymic:
            parts.append(patronymic)
        return " ".join(parts)

    def format_time_until(self, start_time):
        now = datetime.now()
        delta = start_time - now
        total_seconds = int(delta.total_seconds())

        if total_seconds < 0:
            return "Началось", False

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        parts = []
        if hours > 0:
            if hours % 10 == 1 and hours % 100 != 11:
                suffix = "час"
            elif 2 <= hours % 10 <= 4 and not (10 <= hours % 100 <= 20):
                suffix = "часа"
            else:
                suffix = "часов"
            parts.append(f"{hours} {suffix}")
        if minutes > 0:
            if minutes % 10 == 1 and minutes % 100 != 11:
                suffix = "минута"
            elif 2 <= minutes % 10 <= 4 and not (10 <= minutes % 100 <= 20):
                suffix = "минуты"
            else:
                suffix = "минут"
            parts.append(f"{minutes} {suffix}")

        if not parts:
            return "Менее минуты", True

        text = " ".join(parts)
        urgent = hours == 0 and minutes < 60
        return text, urgent

    def create_record_card(self, record):
        card = QFrame()
        # 💡 Ширина: до 800 px, но не меньше 350 — центрируется в scroll_content
        card.setMinimumWidth(550)
        card.setMaximumWidth(800)
        card.setSizePolicy(
            card.sizePolicy().horizontalPolicy(),
            card.sizePolicy().verticalPolicy()
        )
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                padding: 16px;
                border: 1px solid #e0e0e0;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(6)

        # ФИО
        fio = self.format_fio(record["FirstName"], record["LastName"], record.get("Patronymic"))
        fio_label = QLabel(f"<b>👤 {fio}</b>")
        fio_label.setFont(QFont(FONT_FAMILY, 12))

        # Email и телефон
        contact = f"📧 {record['Email']} | 📞 {record['Phone']}"
        contact_label = QLabel(contact)
        contact_label.setFont(QFont(FONT_FAMILY, 10))
        contact_label.setStyleSheet("color: #555;")

        # Услуга
        service_label = QLabel(f"💅 Услуга: <b>{record['ServiceTitle']}</b>")
        service_label.setFont(QFont(FONT_FAMILY, 11))

        # Дата и время
        dt_str = record["StartTime"].strftime("%d %b %Y, %H:%M")
        dt_label = QLabel(f"🕗 Начало: {dt_str}")
        dt_label.setFont(QFont(FONT_FAMILY, 10))

        # Оставшееся время
        time_until, urgent = self.format_time_until(record["StartTime"])
        time_label = QLabel(f"⏳ До начала: <b>{time_until}</b>")
        time_label.setFont(QFont(FONT_FAMILY, 10))
        if urgent:
            time_label.setStyleSheet("color: red; font-weight: bold;")

        # Комментарий
        if record.get("Comment"):
            comm = QLabel(f"💬 {record['Comment']}")
            comm.setFont(QFont(FONT_FAMILY, 10))
            comm.setStyleSheet("color: #777; font-style: italic;")
            comm.setWordWrap(True)
            layout.addWidget(comm)

        layout.addWidget(fio_label)
        layout.addWidget(contact_label)
        layout.addWidget(service_label)
        layout.addWidget(dt_label)
        layout.addWidget(time_label)

        return card