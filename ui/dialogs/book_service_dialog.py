from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QDateEdit, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import QDate, QTime, Qt
from datetime import datetime, timedelta
import re

class BookServiceDialog(QDialog):
    def __init__(self, service_data: dict, clients: list, parent=None):
        super().__init__(parent)
        self.service_data = service_data
        self.clients = clients
        self.setWindowTitle("Запись клиента на услугу")
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Информация об услуге
        layout.addWidget(QLabel("<b>Услуга:</b>"))
        self.title_label = QLabel()
        layout.addWidget(self.title_label)

        self.duration_label = QLabel()
        layout.addWidget(self.duration_label)

        layout.addSpacing(10)

        # Выбор клиента
        client_layout = QHBoxLayout()
        client_layout.addWidget(QLabel("Клиент:"))
        self.client_combo = QComboBox()
        client_layout.addWidget(self.client_combo)
        layout.addLayout(client_layout)

        # Дата
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Дата:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        date_layout.addWidget(self.date_edit)
        layout.addLayout(date_layout)

        # Время начала
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Время начала (ЧЧ:ММ):"))
        self.time_start_edit = QLineEdit()
        self.time_start_edit.setPlaceholderText("10:30")
        self.time_start_edit.setInputMask("99:99")
        self.time_start_edit.textChanged.connect(self.on_time_changed)
        time_layout.addWidget(self.time_start_edit)

        # Время окончания (только для чтения)
        time_layout.addWidget(QLabel("→ Окончание:"))
        self.time_end_label = QLabel("—")
        self.time_end_label.setStyleSheet("font-weight: bold; color: gray;")
        time_layout.addWidget(self.time_end_label)
        layout.addLayout(time_layout)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Записать")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        # Услуга
        self.title_label.setText(self.service_data['Title'])
        duration_min = self.service_data['DurationInSeconds'] // 60
        self.duration_label.setText(f"Длительность: {duration_min} мин")

        # Клиенты: [("ID", "ФИО"), ...]
        self.client_combo.clear()
        for client_id, fio in self.clients:
            self.client_combo.addItem(fio, client_id)

        # По умолчанию — первый клиент
        if self.clients:
            self.client_combo.setCurrentIndex(0)

        # Время по умолчанию — текущее, округлённое вверх до 30 мин
        now = datetime.now()
        rounded = now.replace(minute=(now.minute // 30 + 1) * 30 % 60, second=0, microsecond=0)
        if rounded <= now:
            rounded += timedelta(hours=1)
        self.time_start_edit.setText(rounded.strftime("%H:%M"))

    def on_time_changed(self):
        time_str = self.time_start_edit.text().strip()
        if self.is_valid_time(time_str):
            start = QTime.fromString(time_str, "hh:mm")
            duration_sec = self.service_data['DurationInSeconds']
            end = start.addSecs(duration_sec)
            self.time_end_label.setText(end.toString("HH:mm"))
        else:
            self.time_end_label.setText("—")

    @staticmethod
    def is_valid_time(s: str) -> bool:
        if not re.match(r"^\d{1,2}:\d{2}$", s):
            return False
        try:
            h, m = map(int, s.split(":"))
            return 0 <= h < 24 and 0 <= m < 60
        except ValueError:
            return False

    def get_data(self):
        time_str = self.time_start_edit.text().strip()
        if not self.is_valid_time(time_str):
            raise ValueError("Некорректное время начала")
    
        client_id = self.client_combo.currentData()
        if not client_id:
            raise ValueError("Клиент не выбран")
    
        # Формируем полную дату-время
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        start_datetime = f"{date_str} {time_str}:00"  # секунды = :00
    
        return {
            'ClientID': client_id,
            'ServiceID': self.service_data['ID'],
            'StartTime': start_datetime,
        }