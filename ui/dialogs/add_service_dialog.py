import os
from pathlib import Path
from shutil import copy2

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QDoubleSpinBox, QSpinBox, QTextEdit,
    QPushButton, QFileDialog, QMessageBox
)
from db import Database

db = Database()

class AddServiceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить новую услугу")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Поля ввода
        self.title_edit = QLineEdit()
        self.cost_edit = QDoubleSpinBox()
        self.cost_edit.setRange(0, 1_000_000)
        self.cost_edit.setDecimals(2)
        self.duration_edit = QSpinBox()
        self.duration_edit.setRange(0, 24 * 3600)
        self.desc_edit = QTextEdit()
        self.discount_edit = QDoubleSpinBox()
        self.discount_edit.setRange(0, 100)
        self.discount_edit.setSuffix(" %")
        self.discount_edit.setDecimals(1)
        self.image_path_edit = QLineEdit()
        self.image_path_edit.setReadOnly(True)
        
        # Макеты для строк
        self.add_row("Название*", self.title_edit, layout)
        self.add_row("Стоимость*", self.cost_edit, layout)
        self.add_row("Длительность, сек*", self.duration_edit, layout)
        layout.addWidget(QLabel("Описание"))
        layout.addWidget(self.desc_edit)
        self.add_row("Скидка (%)", self.discount_edit, layout)
        
        # Выбор изображения
        image_row = QHBoxLayout()
        image_row.addWidget(QLabel("Основное изображение"))
        image_row.addWidget(self.image_path_edit, 1)
        browse_btn = QPushButton("Выбрать...")
        browse_btn.clicked.connect(self.on_browse)
        image_row.addWidget(browse_btn)
        layout.addLayout(image_row)
        
        # Кнопки
        btns = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        save_btn.clicked.connect(self.on_save)
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)
    
    def add_row(self, label_text, widget, parent_layout):
        row = QHBoxLayout()
        row.addWidget(QLabel(label_text))
        row.addWidget(widget, 1)
        parent_layout.addLayout(row)
    
    def on_browse(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if file_path:
            self.image_path_edit.setText(file_path)
    
    def on_save(self):
        title = self.title_edit.text().strip()
        cost = self.cost_edit.value()
        duration = self.duration_edit.value()
        description = self.desc_edit.toPlainText().strip() or None
        discount = self.discount_edit.value() or None
        image_path = self.image_path_edit.text().strip() or None
        
        # Валидация
        errors = self.validate_input(title, cost, duration)
        if errors:
            QMessageBox.warning(self, "Ошибка ввода", "\n".join(errors))
            return
        
        # Обработка изображения
        final_image_path = self.process_image(image_path, title)
        if image_path and not final_image_path:
            return  # Ошибка уже показана в process_image
        
        # Сохранение в БД
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
                QMessageBox.information(self, "Успех", f"Услуга '{title}' добавлена")
                self.accept()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось добавить услугу в базу данных.")
        except Exception as e:
            QMessageBox.critical(self, "Исключение", f"Ошибка при добавлении услуги:\n{e}")
    
    def validate_input(self, title, cost, duration):
        errors = []
        if not title:
            errors.append("Название не может быть пустым")
        if len(title) > 100:
            errors.append("Название не должно превышать 100 символов")
        if cost <= 0:
            errors.append("Стоимость должна быть положительной")
        if duration <= 0:
            errors.append("Длительность должна быть положительной")
        return errors
    
    def process_image(self, image_path, title):
        if not image_path or not os.path.isfile(image_path):
            return None
        
        try:
            # Создаем уникальное имя файла
            filename = f"{Path(title).stem}_{hash(image_path) % 10000}.jpg"
            dest_dir = "assets/service_photo"
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, filename)
            
            copy2(image_path, dest_path)
            return dest_path.replace("\\", "/")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изображение:\n{e}")
            return None
    
    def get_data(self):
        """Возвращает данные формы"""
        return {
            'title': self.title_edit.text().strip(),
            'cost': self.cost_edit.value(),
            'duration': self.duration_edit.value(),
            'description': self.desc_edit.toPlainText().strip() or None,
            'discount': self.discount_edit.value() or None,
            'image_path': self.image_path_edit.text().strip() or None
        }