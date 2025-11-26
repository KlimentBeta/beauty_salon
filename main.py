import sys
from PyQt6.QtWidgets import QApplication, QWidget

app = QApplication(sys.argv)
win = QWidget()
win.setWindowTitle("Beauty salon")
win.resize(1200, 800)
win.show()
sys.exit(app.exec())