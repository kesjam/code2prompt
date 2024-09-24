import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon

class TestApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Icon Test")
        self.setGeometry(100, 100, 300, 200)
        self.setWindowIcon(QIcon("MyIcon.icns"))  # Ensure this path is correct

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestApp()
    window.show()
    sys.exit(app.exec_())