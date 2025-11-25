import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget



LOGO_PATH: str = "assets/beauty_logo.png"
FONT_FAMILY: str = "Tahoma"
COLOR_MAIN = (255, 255, 255)
COLOR_SECONDARY = (225, 228, 255)
COLOR_ATTENTION = (255, 74, 109)



app = QApplication(sys.argv)
win = QWidget()
win.setWindowTitle("Hello")
label = QLabel("Hello World", win)
win.resize(1200, 800)
win.show()
sys.exit(app.exec())