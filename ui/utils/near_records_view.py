from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
    QLabel, QPushButton
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from config import FONT_FAMILY, COLOR_BUTTON_ADMIN, rgb_to_hex

class NearRecordsView(QWidget):
    back_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("📅 Ближайшие записи")
        title.setFont(QFont(FONT_FAMILY, 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Здесь можно загружать реальные данные из БД
        records = self.load_near_records()
        
        for rec in records:
            card = self.create_record_card(rec)
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
        back_btn.clicked.connect(self.back_requested.emit)
        layout.addWidget(back_btn)
        layout.addStretch()
    
    def load_near_records(self):
        """Загрузка ближайших записей из БД"""
        # Временные данные для примера
        return [
            {"user": "Анна", "service": "Маникюр", "time": "15 дек, 14:30"},
            {"user": "Мария", "service": "Стрижка", "time": "15 дек, 16:00"},
            {"user": "Елена", "service": "Окрашивание", "time": "16 дек, 10:15"},
        ]
    
    def create_record_card(self, record):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                padding: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        card_layout = QHBoxLayout(card)
        
        name_label = QLabel(f"<b>{record['user']}</b>")
        name_label.setFont(QFont(FONT_FAMILY, 11))
        
        service_label = QLabel(record["service"])
        service_label.setFont(QFont(FONT_FAMILY, 11))
        
        time_label = QLabel(f"<i>{record['time']}</i>")
        time_label.setFont(QFont(FONT_FAMILY, 10))
        time_label.setStyleSheet("color: #666;")
        
        card_layout.addWidget(name_label)
        card_layout.addWidget(service_label)
        card_layout.addStretch()
        card_layout.addWidget(time_label)
        
        return card