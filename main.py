import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget

app = QApplication(sys.argv)
win = QWidget()
win.setWindowTitle("Hello")
label = QLabel("Hello World", win)
win.resize(1200, 800)
win.show()
sys.exit(app.exec())