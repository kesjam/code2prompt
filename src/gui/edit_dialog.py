from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QTextEdit, QPushButton

class EditDialog(QDialog):
    def __init__(self, dictation):
        super().__init__()

        self.setWindowTitle('Edit Dictation')

        self.subject_line_edit = QLineEdit()
        self.subject_line_edit.setText(dictation.subject)

        self.content_text_edit = QTextEdit()
        self.content_text_edit.setPlainText(dictation.content)

        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.subject_line_edit)
        layout.addWidget(self.content_text_edit)
        layout.addWidget(self.save_button)

        self.setLayout(layout)