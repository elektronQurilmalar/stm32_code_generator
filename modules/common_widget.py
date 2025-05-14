from PyQt5.QtWidgets import QComboBox

class YesNoComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.addItems(["No", "Yes"])

    def is_yes(self):
        return self.currentIndex() == 1

    def set_yes(self, yes_bool):
        self.setCurrentIndex(1 if yes_bool else 0)

# Можно добавить другие общие элементы, например, для ввода чисел с ограничениями и т.д.