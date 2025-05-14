from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon, QGuiApplication
from PyQt5.QtCore import Qt


class CodePane(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)

        buttons_layout = QHBoxLayout()

        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.setIcon(QIcon.fromTheme("edit-copy"))
        self.copy_button.clicked.connect(self.copy_code_to_clipboard)
        buttons_layout.addWidget(self.copy_button)

        self.save_button = QPushButton("Save to File (.c)")
        self.save_button.setIcon(QIcon.fromTheme("document-save"))
        self.save_button.clicked.connect(self.save_code_to_file)
        buttons_layout.addWidget(self.save_button)

        buttons_layout.addStretch()
        self.main_layout.addLayout(buttons_layout)

        self.code_edit = QTextEdit()
        self.code_edit.setReadOnly(True)
        self.code_edit.setFontFamily("Courier New") # Or "Monospace"
        self.code_edit.setLineWrapMode(QTextEdit.NoWrap) # Important for code
        self.main_layout.addWidget(self.code_edit)

        self.setLayout(self.main_layout)

    def set_code(self, code_text):
        self.code_edit.setPlainText(code_text)

    def copy_code_to_clipboard(self):
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            clipboard.setText(self.code_edit.toPlainText())
            # Consider a small status message or visual feedback
            # For now, just printing for debug:
            # print("Code copied to clipboard.")
        else:
            QMessageBox.warning(self, "Clipboard Error", "Could not access the clipboard.")

    def save_code_to_file(self):
        code_text = self.code_edit.toPlainText()
        if not code_text:
            QMessageBox.information(self, "No Code", "There is no code to save.")
            return

        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog # Uncomment if native dialog is problematic
        file_name, _ = QFileDialog.getSaveFileName(self,
                                                   "Save Generated Code",
                                                   "generated_main.c",
                                                   "C Files (*.c);;Text Files (*.txt);;All Files (*)",
                                                   options=options)
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(code_text)
                # Optional: QMessageBox.information(self, "File Saved", f"Code saved to {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Could not save file: {e}")