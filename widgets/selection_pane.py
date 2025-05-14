# --- MODIFIED FILE widgets/selection_pane.py ---

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget
from PyQt5.QtCore import pyqtSignal


class SelectionPane(QWidget):
    module_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.module_list = QListWidget()
        # Reordering is usually not desired for a fixed module list.
        # If reordering defines generation order, it should be handled more explicitly.
        # self.module_list.setDragDropMode(QListWidget.InternalMove)
        self.module_list.setSelectionMode(QListWidget.SingleSelection)

        # This list defines the modules available in the UI.
        # The order here is the display order.
        # MainWindow.LOGICAL_MODULE_ORDER defines the processing order.
        self.modules = ["MCU", "RCC", "GPIO", "DMA", "ADC", "DAC", "TIMERS", "I2C", "SPI", "USART", "Delay"]
        self.module_list.addItems(self.modules)

        self.layout.addWidget(self.module_list)
        self.setLayout(self.layout)

        self.module_list.currentItemChanged.connect(self.on_item_changed)

    def on_item_changed(self, current, previous):
        if current:
            self.module_selected.emit(current.text())