from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton

class DetailsDialog(QDialog):
    def __init__(self, dictation):
        super().__init__()

        self.setWindowTitle('Dictation Details')

        self.subject_label = QLabel(f"Subject: {dictation.subject}")
        self.content_text_edit = QTextEdit()
        self.content_text_edit.setPlainText(dictation.content)
        self.content_text_edit.setReadOnly(True)

        self.close_button = QPushButton('Close')
        self.close_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.subject_label)
        
        # Extract the relevant part of the transcription
        relevant_content = self.extract_relevant_content(dictation.content)
        
        self.content_label = QLabel(relevant_content)
        self.content_label.setWordWrap(True)
        layout.addWidget(self.content_label)
        
        layout.addWidget(self.close_button)

        self.setLayout(layout)
    
    def extract_relevant_content(self, content):
        if "---" in content:
            # Split the content by "---" and return the second part (excluding the dictation type label)
            return content.split("---")[1].strip()
        else:
            # If no "---" separator is found, return the entire content
            return content