import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import QThread, pyqtSignal

class Worker(QThread):
    finished = pyqtSignal(str)

    def run(self):
        time.sleep(5)
        self.finished.emit("Work completed!")

class ThreadedApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        self.status_label = QLabel('Ready', self)
        layout.addWidget(self.status_label)

        start_button = QPushButton('Start Thread', self)
        start_button.clicked.connect(self.start_thread)
        layout.addWidget(start_button)

        self.setLayout(layout)
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Threaded PyQt5 App')
        self.show()

    def start_thread(self):
        self.status_label.setText('Working...')
        self.worker = Worker()
        self.worker.finished.connect(self.on_thread_finish)
        self.worker.start()

    def on_thread_finish(self, result):
        self.status_label.setText(result)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ThreadedApp()
    sys.exit(app.exec_())
