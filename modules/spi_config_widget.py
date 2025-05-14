from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QComboBox, QLineEdit,
                             QGroupBox, QCheckBox, QLabel, QHBoxLayout)
from PyQt5.QtCore import pyqtSignal

from core.mcu_defines_loader import CURRENT_MCU_DEFINES


class SPIConfigWidget(QWidget):
    config_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_initializing = True
        self.current_target_device = "STM32F407VG"  # Updated by update_for_target_device
        self.current_mcu_family = "STM32F4"  # Updated by update_for_target_device

        self.main_layout = QVBoxLayout(self)
        instance_selection_layout = QHBoxLayout()
        instance_selection_layout.addWidget(QLabel("Configure SPI Instance:"))
        self.spi_instance_combo = QComboBox()
        instance_selection_layout.addWidget(self.spi_instance_combo)
        instance_selection_layout.addStretch()
        self.main_layout.addLayout(instance_selection_layout)

        self.enable_spi_checkbox = QCheckBox("Enable SPI Instance")
        self.main_layout.addWidget(self.enable_spi_checkbox)

        self.params_groupbox = QGroupBox("SPI Parameters")
        self.form_layout = QFormLayout(self.params_groupbox)

        # Populate these combos in update_for_target_device or based on family from CURRENT_MCU_DEFINES
        self.mode_combo = QComboBox()
        self.form_layout.addRow(QLabel("Mode (Master/Slave):"), self.mode_combo)
        self.direction_combo = QComboBox()
        self.form_layout.addRow(QLabel("Direction:"), self.direction_combo)
        self.data_size_combo = QComboBox()
        self.form_layout.addRow(QLabel("Data Size:"), self.data_size_combo)
        self.cpol_combo = QComboBox()
        self.form_layout.addRow(QLabel("Clock Polarity (CPOL):"), self.cpol_combo)
        self.cpha_combo = QComboBox()
        self.form_layout.addRow(QLabel("Clock Phase (CPHA):"), self.cpha_combo)
        self.nss_mode_combo = QComboBox()
        self.form_layout.addRow(QLabel("NSS (Slave Select):"), self.nss_mode_combo)
        self.baud_prescaler_combo = QComboBox()
        self.form_layout.addRow(QLabel("Baud Rate Prescaler (vs APB):"), self.baud_prescaler_combo)
        self.first_bit_combo = QComboBox()
        self.form_layout.addRow(QLabel("First Bit Transmitted:"), self.first_bit_combo)

        self.crc_poly_lineedit = QLineEdit("7")
        self.crc_poly_lineedit.setPlaceholderText("Disabled if 0 or empty")
        self.form_layout.addRow(QLabel("CRC Polynomial (e.g., 7 for CRC8):"), self.crc_poly_lineedit)

        interrupt_group = QGroupBox("Interrupts")
        interrupt_layout = QFormLayout(interrupt_group)
        self.txe_ie_checkbox = QCheckBox("TXE (Transmit Buffer Empty) Interrupt")
        self.rxne_ie_checkbox = QCheckBox("RXNE (Receive Buffer Not Empty) Interrupt")
        self.err_ie_checkbox = QCheckBox("Error Interrupt (CRC, OVR, MODF)")
        interrupt_layout.addRow(self.txe_ie_checkbox);
        interrupt_layout.addRow(self.rxne_ie_checkbox);
        interrupt_layout.addRow(self.err_ie_checkbox)
        self.form_layout.addRow(interrupt_group)

        default_funcs_group = QGroupBox("Default Helper Functions (Blocking)")
        default_funcs_layout = QFormLayout(default_funcs_group)
        self.func_tx_byte_checkbox = QCheckBox("Generate Transmit Byte Function")
        self.func_rx_byte_checkbox = QCheckBox("Generate Receive Byte Function")
        self.func_tx_rx_byte_checkbox = QCheckBox("Generate Transmit/Receive Byte Function")
        default_funcs_layout.addRow(self.func_tx_byte_checkbox);
        default_funcs_layout.addRow(self.func_rx_byte_checkbox);
        default_funcs_layout.addRow(self.func_tx_rx_byte_checkbox)
        self.form_layout.addRow(default_funcs_group)

        self.pin_info_label = QLabel("Pinout: N/A")
        self.pin_info_label.setWordWrap(True)
        self.form_layout.addRow(QLabel("Suggested Pins:"), self.pin_info_label)
        self.main_layout.addWidget(self.params_groupbox)

        self._connect_signals()
        self._is_initializing = False
        # Initial update by ConfigurationPane

    def _connect_signals(self):
        self.spi_instance_combo.currentTextChanged.connect(self.on_current_instance_changed)
        self.enable_spi_checkbox.stateChanged.connect(self.emit_config_and_update_visibility)
        # Connect all param widgets
        for child in self.params_groupbox.findChildren((QComboBox, QLineEdit, QCheckBox)):
            if isinstance(child, QComboBox):
                child.currentTextChanged.connect(self.emit_config_update_slot)
            elif isinstance(child, QLineEdit):
                child.editingFinished.connect(self.emit_config_update_slot)  # Or textChanged
            elif isinstance(child, QCheckBox):
                child.stateChanged.connect(self.emit_config_update_slot)

    def _populate_combo(self, combo_box, define_key, default_map_key=None):
        # Helper to populate combo boxes from CURRENT_MCU_DEFINES
        # define_key might be family specific e.g. "SPI_MODES_STM32F1"
        # default_map_key is the generic key e.g. "SPI_MODES"
        family_specific_key = f"{define_key}_{self.current_mcu_family}"
        options_map = CURRENT_MCU_DEFINES.get(family_specific_key, CURRENT_MCU_DEFINES.get(define_key, {}))
        if default_map_key and not options_map:  # Further fallback for very generic keys
            options_map = CURRENT_MCU_DEFINES.get(default_map_key, {})

        current_text = combo_box.currentText()
        combo_box.blockSignals(True)
        combo_box.clear()
        combo_box.addItems(options_map.keys())
        if current_text in options_map:
            combo_box.setCurrentText(current_text)
        elif options_map:
            combo_box.setCurrentIndex(0)
        combo_box.blockSignals(False)

    def update_for_target_device(self, target_device_name, target_family_name, is_initial_call=False):
        self._is_initializing = True
        self.current_target_device = target_device_name
        self.current_mcu_family = target_family_name

        # Update SPI Instances
        current_instance = self.spi_instance_combo.currentText()
        self.spi_instance_combo.blockSignals(True)
        self.spi_instance_combo.clear()
        available_instances = CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {}).get(target_device_name, {}).get(
            "spi_instances", [])
        spi_info_map_key = f"SPI_PERIPHERALS_INFO_{target_family_name}"
        if not available_instances:  # Fallback
            spi_info_map = CURRENT_MCU_DEFINES.get(spi_info_map_key,
                                                   CURRENT_MCU_DEFINES.get("SPI_PERIPHERALS_INFO", {}))
            available_instances = list(spi_info_map.keys())
        self.spi_instance_combo.addItems(available_instances)
        if current_instance in available_instances:
            self.spi_instance_combo.setCurrentText(current_instance)
        elif available_instances:
            self.spi_instance_combo.setCurrentIndex(0)
        self.spi_instance_combo.blockSignals(False)

        # Populate parameter combos based on (potentially) family-specific defines
        self._populate_combo(self.mode_combo, "SPI_MODES")
        self._populate_combo(self.direction_combo, "SPI_DIRECTIONS")
        self._populate_combo(self.data_size_combo, "SPI_DATA_SIZES")
        self._populate_combo(self.cpol_combo, "SPI_CPOL")
        self._populate_combo(self.cpha_combo, "SPI_CPHA")
        self._populate_combo(self.nss_mode_combo, "SPI_NSS_MODES")
        self._populate_combo(self.baud_prescaler_combo, "SPI_BAUD_PRESCALERS")
        self._populate_combo(self.first_bit_combo, "SPI_FIRST_BIT")

        # CRC is generally available, but visibility could be family-dependent if needed
        # self.crc_poly_lineedit.setVisible(CURRENT_MCU_DEFINES.get("SPI_HAS_CRC", True))

        self._update_pin_info_label()
        self.update_ui_visibility()
        self._is_initializing = False
        if not is_initial_call:
            self.emit_config_update_slot()

    def on_current_instance_changed(self, instance_name):
        if self._is_initializing: return
        self._update_pin_info_label()
        self.emit_config_update_slot()

    def _update_pin_info_label(self):
        instance_name = self.spi_instance_combo.currentText()
        if not instance_name: self.pin_info_label.setText("Pinout: N/A"); return

        pin_sugg_map_key = f"SPI_PIN_CONFIG_SUGGESTIONS_{self.current_mcu_family}"
        pin_sugg_map = CURRENT_MCU_DEFINES.get(pin_sugg_map_key,
                                               CURRENT_MCU_DEFINES.get("SPI_PIN_CONFIG_SUGGESTIONS", {}))
        suggestions = pin_sugg_map.get(self.current_target_device, {}).get(instance_name, {})

        pin_text = []
        if suggestions:
            for pin_type in ["SCK", "MISO", "MOSI", "NSS"]:
                if pin_type in suggestions: pin_text.append(f"{pin_type}: {suggestions[pin_type]}")
            self.pin_info_label.setText("; ".join(pin_text) if pin_text else "No specific pin suggestions.")
        else:
            self.pin_info_label.setText(f"Pinout: No suggestions for {instance_name} on {self.current_target_device}")

    def update_ui_visibility(self):
        enabled = self.enable_spi_checkbox.isChecked()
        self.params_groupbox.setEnabled(enabled)

    def emit_config_and_update_visibility(self, _=None):
        self.update_ui_visibility()
        self.emit_config_update_slot()

    def emit_config_update_slot(self, _=None):
        if self._is_initializing: return
        self.config_updated.emit(self.get_config())

    def get_config(self):
        spi_instance = self.spi_instance_combo.currentText()
        if not spi_instance:
            return {"instance_name": "", "enabled": False, "params": {}, "calculated": {},
                    "mcu_family": self.current_mcu_family, "target_device": self.current_target_device}
        crc_poly_text = self.crc_poly_lineedit.text()
        try:
            crc_poly_val = int(crc_poly_text) if crc_poly_text.strip() else 0
        except ValueError:
            crc_poly_val = 0

        params = {
            "instance_name": spi_instance,
            "enabled": self.enable_spi_checkbox.isChecked(),
            "mode_str": self.mode_combo.currentText(),
            "direction_str": self.direction_combo.currentText(),
            "data_size_str": self.data_size_combo.currentText(),
            "cpol_str": self.cpol_combo.currentText(),
            "cpha_str": self.cpha_combo.currentText(),
            "nss_mode_str": self.nss_mode_combo.currentText(),
            "baud_prescaler_str": self.baud_prescaler_combo.currentText(),
            "first_bit_str": self.first_bit_combo.currentText(),
            "crc_polynomial": crc_poly_val,
            "interrupt_txe": self.txe_ie_checkbox.isChecked(),
            "interrupt_rxne": self.rxne_ie_checkbox.isChecked(),
            "interrupt_err": self.err_ie_checkbox.isChecked(),
            "generate_tx_byte_func": self.func_tx_byte_checkbox.isChecked(),
            "generate_rx_byte_func": self.func_rx_byte_checkbox.isChecked(),
            "generate_tx_rx_byte_func": self.func_tx_rx_byte_checkbox.isChecked(),
            "mcu_family": self.current_mcu_family,
            "target_device": self.current_target_device,
        }
        return {"instance_name": spi_instance, "enabled": params["enabled"],
                "params": params, "calculated": {},
                "mcu_family": self.current_mcu_family, "target_device": self.current_target_device}