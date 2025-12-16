import shutil
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDoubleSpinBox,
    QSpinBox, QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from decimal import Decimal
import os

class EditServiceDialog(QDialog):
    def __init__(self, service_data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать услугу")
        self.service_data = service_data
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # ID (неизменяемый)
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("ID:"))
        self.id_label = QLabel()
        self.id_label.setStyleSheet("font-weight: bold;")
        id_layout.addWidget(self.id_label)
        layout.addLayout(id_layout)

        # Название
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Название услуги:"))
        self.title_edit = QLineEdit()
        title_layout.addWidget(self.title_edit)
        layout.addLayout(title_layout)

        # Цена
        cost_layout = QHBoxLayout()
        cost_layout.addWidget(QLabel("Цена:"))
        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0.0, 1_000_000.0)
        self.cost_spin.setDecimals(2)
        cost_layout.addWidget(self.cost_spin)
        layout.addLayout(cost_layout)

        # Скидка (в долях, например 0.1 = 10%)
        discount_layout = QHBoxLayout()
        discount_layout.addWidget(QLabel("Скидка (0.0–1.0):"))
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setRange(0.0, 1.0)
        self.discount_spin.setSingleStep(0.05)
        self.discount_spin.setDecimals(2)
        discount_layout.addWidget(self.discount_spin)
        layout.addLayout(discount_layout)

        # Время оказания (в секундах → минуты для удобства)
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Время оказания (мин):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 1440)  # до 24 ч
        duration_layout.addWidget(self.duration_spin)
        layout.addLayout(duration_layout)

        # Путь к изображению
        image_layout = QHBoxLayout()
        image_layout.addWidget(QLabel("Фото:"))
        self.image_path_edit = QLineEdit()
        self.image_path_edit.setReadOnly(True)
        image_layout.addWidget(self.image_path_edit)

        self.browse_btn = QPushButton("Загрузить...")
        self.browse_btn.clicked.connect(self.select_image)
        image_layout.addWidget(self.browse_btn)
        layout.addLayout(image_layout)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        data = self.service_data
        self.id_label.setText(str(data['ID']))
        self.title_edit.setText(data['Title'] or "")
        self.cost_spin.setValue(float(data['Cost']))
        self.discount_spin.setValue(data['Discount'] if data['Discount'] is not None else 0.0)
        self.duration_spin.setValue(data['DurationInSeconds'] // 60)  # → минуты
        self.image_path_edit.setText(data['MainImagePath'] or "")

    def select_image(self):
        target_dir = "assets/service_photo"
        os.makedirs(target_dir, exist_ok=True)

        # Открываем диалог сразу в нужной папке
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            target_dir,  # ← вот здесь — начальная директория
            "Изображения (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if file_path:
            # Просто используем выбранный путь (без копирования, если файл уже внутри assets)
            full_path = os.path.abspath(file_path).replace("\\", "/")
            # Убеждаемся, что путь начинается с "assets/service_photo/"
            if full_path.startswith(os.path.abspath(target_dir).replace("\\", "/")):
                rel_path = os.path.relpath(full_path, os.path.abspath(".")).replace("\\", "/")
                self.image_path_edit.setText(rel_path)
            else:
                # Если выбрали файл извне — копируем (как раньше)
                filename = os.path.basename(file_path)
                target_path = os.path.join(target_dir, filename)
                shutil.copy(file_path, target_path)
                self.image_path_edit.setText(target_path.replace("\\", "/"))

    def get_data(self):
        """Возвращает обновлённые данные услуги."""
        return {
            'ID': int(self.id_label.text()),
            'Title': self.title_edit.text().strip(),
            'Cost': Decimal(f"{self.cost_spin.value():.4f}"),
            'DurationInSeconds': self.duration_spin.value() * 60,
            'Discount': self.discount_spin.value() or 0.0,
            'MainImagePath': self.image_path_edit.text() or None,
        }

