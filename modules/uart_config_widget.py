# --- MODIFIED FILE modules/uart_config_widget.py ---
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QComboBox,
                             QGroupBox, QCheckBox, QLabel, QHBoxLayout)  # Removed QLineEdit as it's not used
from PyQt5.QtCore import pyqtSignal

from core.mcu_defines_loader import CURRENT_MCU_DEFINES


class UARTConfigWidget(QWidget):
    config_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_initializing = True
        self.current_target_device = "STM32F407VG"
        self.current_mcu_family = "STM32F4"

        self.main_layout = QVBoxLayout(self)
        instance_selection_layout = QHBoxLayout()
        instance_selection_layout.addWidget(QLabel("Configure USART/UART Instance:"))
        self.uart_instance_combo = QComboBox()
        instance_selection_layout.addWidget(self.uart_instance_combo)
        instance_selection_layout.addStretch()
        self.main_layout.addLayout(instance_selection_layout)

        self.enable_uart_checkbox = QCheckBox("Enable USART/UART Instance")
        self.main_layout.addWidget(self.enable_uart_checkbox)

        self.params_groupbox = QGroupBox("USART Parameters")
        self.form_layout = QFormLayout(self.params_groupbox)

        self.baud_rate_combo = QComboBox()  # Populated in update
        self.form_layout.addRow(QLabel("Baud Rate:"), self.baud_rate_combo)
        self.word_length_combo = QComboBox()
        self.form_layout.addRow(QLabel("Word Length:"), self.word_length_combo)
        self.parity_combo = QComboBox()
        self.form_layout.addRow(QLabel("Parity:"), self.parity_combo)
        self.stop_bits_combo = QComboBox()
        self.form_layout.addRow(QLabel("Stop Bits:"), self.stop_bits_combo)
        self.hw_flow_ctrl_combo = QComboBox()
        self.form_layout.addRow(QLabel("HW Flow Control:"), self.hw_flow_ctrl_combo)
        self.mode_combo = QComboBox()
        self.form_layout.addRow(QLabel("Mode (TX/RX):"), self.mode_combo)
        self.oversampling_combo = QComboBox()
        self.form_layout.addRow(QLabel("Oversampling:"), self.oversampling_combo)

        interrupt_group = QGroupBox("Interrupts")
        interrupt_layout = QFormLayout(interrupt_group)
        self.txe_ie_checkbox = QCheckBox("TXE (Transmit Data Register Empty)")
        self.rxne_ie_checkbox = QCheckBox("RXNE (Read Data Register Not Empty)")
        self.tcie_checkbox = QCheckBox("TC (Transmission Complete)")
        self.peie_checkbox = QCheckBox("PE (Parity Error)")
        interrupt_layout.addRow(self.txe_ie_checkbox);
        interrupt_layout.addRow(self.rxne_ie_checkbox)
        interrupt_layout.addRow(self.tcie_checkbox);
        interrupt_layout.addRow(self.peie_checkbox)
        self.form_layout.addRow(interrupt_group)

        default_funcs_group = QGroupBox("Default Helper Functions")
        default_funcs_layout = QFormLayout(default_funcs_group)
        self.func_rx_byte_checkbox = QCheckBox("Generate Receive Byte Function (blocking)")
        self.func_tx_byte_checkbox = QCheckBox("Generate Transmit Byte Function (blocking)")
        self.func_tx_string_checkbox = QCheckBox("Generate Transmit String Function (blocking)")
        default_funcs_layout.addRow(self.func_rx_byte_checkbox);
        default_funcs_layout.addRow(self.func_tx_byte_checkbox);
        default_funcs_layout.addRow(self.func_tx_string_checkbox)
        self.form_layout.addRow(default_funcs_group)

        self.pin_info_label = QLabel("Pinout: N/A");
        self.pin_info_label.setWordWrap(True)
        self.form_layout.addRow(QLabel("Suggested Pins:"), self.pin_info_label)
        self.main_layout.addWidget(self.params_groupbox)

        self._connect_signals()
        self._is_initializing = False
        # Initial update by ConfigurationPane

    def _connect_signals(self):
        self.uart_instance_combo.currentTextChanged.connect(self.on_current_instance_changed)
        self.enable_uart_checkbox.stateChanged.connect(self.emit_config_and_update_visibility)
        # Connect all param widgets
        for child in self.params_groupbox.findChildren((QComboBox, QCheckBox)):
            if isinstance(child, QComboBox):
                child.currentTextChanged.connect(self.emit_config_update_slot)
            elif isinstance(child, QCheckBox):
                child.stateChanged.connect(self.emit_config_update_slot)

    def _populate_combo(self, combo_box, define_key_prefix, default_define_key):
        family_specific_key = f"{define_key_prefix}_{self.current_mcu_family}"
        options_map = CURRENT_MCU_DEFINES.get(family_specific_key, CURRENT_MCU_DEFINES.get(default_define_key, {}))

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

        # Update UART Instances
        current_instance = self.uart_instance_combo.currentText()
        self.uart_instance_combo.blockSignals(True)
        self.uart_instance_combo.clear()
        available_instances = CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {}).get(target_device_name, {}).get(
            "usart_instances", [])
        usart_info_map_key = f"USART_PERIPHERALS_INFO_{target_family_name}"
        if not available_instances:  # Fallback
            usart_info_map = CURRENT_MCU_DEFINES.get(usart_info_map_key,
                                                     CURRENT_MCU_DEFINES.get("USART_PERIPHERALS_INFO", {}))
            available_instances = list(usart_info_map.keys())
        self.uart_instance_combo.addItems(available_instances)
        if current_instance in available_instances:
            self.uart_instance_combo.setCurrentText(current_instance)
        elif available_instances:
            self.uart_instance_combo.setCurrentIndex(0)
        self.uart_instance_combo.blockSignals(False)

        # Populate Baud Rate combo (common baud rates are usually not family specific in defines)
        baud_rates_list = CURRENT_MCU_DEFINES.get("COMMON_BAUD_RATES", [9600, 115200])
        current_baud = self.baud_rate_combo.currentText()
        self.baud_rate_combo.blockSignals(True)
        self.baud_rate_combo.clear()
        self.baud_rate_combo.addItems([str(br) for br in baud_rates_list])
        if current_baud in [str(br) for br in baud_rates_list]:
            self.baud_rate_combo.setCurrentText(current_baud)
        else:
            self.baud_rate_combo.setCurrentText("115200")
        self.baud_rate_combo.blockSignals(False)

        # Populate other parameter combos
        self._populate_combo(self.word_length_combo, "USART_WORD_LENGTH_MAP", "USART_WORD_LENGTH_MAP")
        self._populate_combo(self.parity_combo, "USART_PARITY_MAP", "USART_PARITY_MAP")
        self._populate_combo(self.stop_bits_combo, "USART_STOP_BITS_MAP", "USART_STOP_BITS_MAP")
        self._populate_combo(self.hw_flow_ctrl_combo, "USART_HW_FLOW_CTRL_MAP", "USART_HW_FLOW_CTRL_MAP")
        self._populate_combo(self.mode_combo, "USART_MODE_MAP", "USART_MODE_MAP")
        self.mode_combo.setCurrentText("TX/RX")  # Default

        # Oversampling might be family specific (e.g. F2 only OVER16)
        self._populate_combo(self.oversampling_combo, "USART_OVERSAMPLING_MAP", "USART_OVERSAMPLING_MAP")
        if self.current_mcu_family == "STM32F2" and "8" in [self.oversampling_combo.itemText(i) for i in
                                                            range(self.oversampling_combo.count())]:
            self.oversampling_combo.removeItem(self.oversampling_combo.findText("8"))  # F2 does not support OVER8
            if self.oversampling_combo.currentText() == "8": self.oversampling_combo.setCurrentText("16")
        self.oversampling_combo.setEnabled(self.oversampling_combo.count() > 1)

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
        instance_name = self.uart_instance_combo.currentText()
        if not instance_name: self.pin_info_label.setText("Pinout: N/A"); return

        pin_sugg_map_key = f"USART_PIN_CONFIG_SUGGESTIONS_{self.current_mcu_family}"
        pin_sugg_map = CURRENT_MCU_DEFINES.get(pin_sugg_map_key,
                                               CURRENT_MCU_DEFINES.get("USART_PIN_CONFIG_SUGGESTIONS", {}))
        suggestions = pin_sugg_map.get(self.current_target_device, {}).get(instance_name, {})

        pin_text = []
        if suggestions:
            flow_control_active = self.hw_flow_ctrl_combo.currentText()
            if "TX" in suggestions: pin_text.append(f"TX: {suggestions['TX']}")
            if "RX" in suggestions: pin_text.append(f"RX: {suggestions['RX']}")
            if flow_control_active in ["CTS", "RTS/CTS"] and "CTS" in suggestions:
                pin_text.append(f"CTS: {suggestions['CTS']}")
            if flow_control_active in ["RTS", "RTS/CTS"] and "RTS" in suggestions:
                pin_text.append(f"RTS: {suggestions['RTS']}")
            self.pin_info_label.setText("; ".join(pin_text) if pin_text else "No specific pin suggestions.")
        else:
            self.pin_info_label.setText(f"Pinout: No suggestions for {instance_name} on {self.current_target_device}")

    def update_ui_visibility(self):
        enabled = self.enable_uart_checkbox.isChecked()
        self.params_groupbox.setEnabled(enabled)

    def emit_config_and_update_visibility(self, _=None):
        self.update_ui_visibility()
        self.emit_config_update_slot()

    def emit_config_update_slot(self, _=None):
        if self._is_initializing: return
        if self.sender() is self.hw_flow_ctrl_combo: self._update_pin_info_label()
        self.config_updated.emit(self.get_config())

    def get_config(self):
        uart_instance = self.uart_instance_combo.currentText()
        if not uart_instance:
            return {"instance_name": "", "enabled": False, "params": {}, "calculated": {},
                    "mcu_family": self.current_mcu_family, "target_device": self.current_target_device}
        params = {
            "instance_name": uart_instance,
            "enabled": self.enable_uart_checkbox.isChecked(),
            "baud_rate": int(
                self.baud_rate_combo.currentText()) if self.baud_rate_combo.currentText().isdigit() else 9600,
            "word_length": self.word_length_combo.currentText(),
            "parity": self.parity_combo.currentText(),
            "stop_bits": self.stop_bits_combo.currentText(),
            "hw_flow_control": self.hw_flow_ctrl_combo.currentText(),
            "mode": self.mode_combo.currentText(),
            "oversampling": self.oversampling_combo.currentText(),
            "interrupt_txe": self.txe_ie_checkbox.isChecked(),
            "interrupt_rxne": self.rxne_ie_checkbox.isChecked(),
            "interrupt_tcie": self.tcie_checkbox.isChecked(),
            "interrupt_peie": self.peie_checkbox.isChecked(),
            "generate_rx_byte_func": self.func_rx_byte_checkbox.isChecked(),
            "generate_tx_byte_func": self.func_tx_byte_checkbox.isChecked(),
            "generate_tx_string_func": self.func_tx_string_checkbox.isChecked(),
            "mcu_family": self.current_mcu_family,  # Add context for generator
            "target_device": self.current_target_device,
        }
        return {"instance_name": uart_instance, "enabled": params["enabled"],
                "params": params, "calculated": {},  # Calculated by generator if needed
                "mcu_family": self.current_mcu_family, "target_device": self.current_target_device}