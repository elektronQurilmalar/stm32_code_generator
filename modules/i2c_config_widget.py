from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QComboBox, QLineEdit,
                             QGroupBox, QCheckBox, QLabel, QHBoxLayout)
from PyQt5.QtCore import pyqtSignal

from core.mcu_defines_loader import CURRENT_MCU_DEFINES


class I2CConfigWidget(QWidget):
    config_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_initializing = True
        self.current_target_device = "STM32F407VG"  # Updated by update_for_target_device
        self.current_mcu_family = "STM32F4"  # Updated by update_for_target_device

        self.main_layout = QVBoxLayout(self)
        instance_selection_layout = QHBoxLayout()
        instance_selection_layout.addWidget(QLabel("Configure I2C Instance:"))
        self.i2c_instance_combo = QComboBox()
        instance_selection_layout.addWidget(self.i2c_instance_combo)
        instance_selection_layout.addStretch()
        self.main_layout.addLayout(instance_selection_layout)

        self.enable_i2c_checkbox = QCheckBox("Enable I2C Instance")
        self.main_layout.addWidget(self.enable_i2c_checkbox)

        self.params_groupbox = QGroupBox("I2C Parameters")
        self.form_layout = QFormLayout(self.params_groupbox)

        self.clock_speed_combo = QComboBox()  # Populated in update_for_target_device
        self.form_layout.addRow(QLabel("Clock Speed:"), self.clock_speed_combo)

        self.duty_cycle_combo = QComboBox()
        self.label_duty_cycle = QLabel("Fast Mode Duty Cycle:")
        self.form_layout.addRow(self.label_duty_cycle, self.duty_cycle_combo)

        self.clock_stretching_enable_checkbox = QCheckBox("Enable Clock Stretching (SCL)")
        self.clock_stretching_enable_checkbox.setChecked(True)
        self.form_layout.addRow(self.clock_stretching_enable_checkbox)

        self.addressing_mode_combo = QComboBox()
        self.addressing_mode_combo.addItems(CURRENT_MCU_DEFINES.get("I2C_ADDRESSING_MODES", {"7-bit": 0}).keys())
        self.form_layout.addRow(QLabel("Addressing Mode (Master):"), self.addressing_mode_combo)

        self.own_address1_lineedit = QLineEdit("0x00")
        self.form_layout.addRow(QLabel("Own Address 1 (Slave Mode):"), self.own_address1_lineedit)

        self.dual_address_enable_checkbox = QCheckBox("Enable Dual Addressing Mode (OA2 - Slave)")
        self.form_layout.addRow(self.dual_address_enable_checkbox)
        self.own_address2_lineedit = QLineEdit("0x00")
        self.label_own_address2 = QLabel("Own Address 2 (Slave Mode):")
        self.form_layout.addRow(self.label_own_address2, self.own_address2_lineedit)

        self.general_call_enable_checkbox = QCheckBox("Enable General Call Address (Slave)")
        self.form_layout.addRow(self.general_call_enable_checkbox)

        interrupt_group = QGroupBox("Interrupts")
        interrupt_layout = QFormLayout(interrupt_group)
        self.ev_ie_checkbox = QCheckBox("Event Interrupt Enable (ITEVTEN)")
        self.buf_ie_checkbox = QCheckBox("Buffer Interrupt Enable (ITBUFEN)")
        self.er_ie_checkbox = QCheckBox("Error Interrupt Enable (ITERREN)")
        interrupt_layout.addRow(self.ev_ie_checkbox);
        interrupt_layout.addRow(self.buf_ie_checkbox);
        interrupt_layout.addRow(self.er_ie_checkbox)
        self.form_layout.addRow(interrupt_group)

        default_funcs_group = QGroupBox("Default Helper Functions (Blocking Master)")
        default_funcs_layout = QFormLayout(default_funcs_group)
        self.func_master_tx_checkbox = QCheckBox("Generate Master Transmit Function")
        self.func_master_rx_checkbox = QCheckBox("Generate Master Receive Function")
        default_funcs_layout.addRow(self.func_master_tx_checkbox);
        default_funcs_layout.addRow(self.func_master_rx_checkbox)
        self.form_layout.addRow(default_funcs_group)

        self.pin_info_label = QLabel("Pinout: N/A")
        self.pin_info_label.setWordWrap(True)
        self.form_layout.addRow(QLabel("Suggested Pins:"), self.pin_info_label)
        self.main_layout.addWidget(self.params_groupbox)

        self._connect_signals()
        self._is_initializing = False
        # Initial update by ConfigurationPane

    def _connect_signals(self):
        self.i2c_instance_combo.currentTextChanged.connect(self.on_current_instance_changed)
        self.enable_i2c_checkbox.stateChanged.connect(self.emit_config_and_update_visibility)
        # Param changes
        self.clock_speed_combo.currentTextChanged.connect(self.on_clock_speed_changed)
        self.duty_cycle_combo.currentTextChanged.connect(self.emit_config_update_slot)
        self.clock_stretching_enable_checkbox.stateChanged.connect(self.emit_config_update_slot)
        self.addressing_mode_combo.currentTextChanged.connect(self.emit_config_update_slot)
        self.own_address1_lineedit.editingFinished.connect(self.emit_config_update_slot)
        self.dual_address_enable_checkbox.stateChanged.connect(self.on_dual_address_toggled)
        self.own_address2_lineedit.editingFinished.connect(self.emit_config_update_slot)
        self.general_call_enable_checkbox.stateChanged.connect(self.emit_config_update_slot)
        self.ev_ie_checkbox.stateChanged.connect(self.emit_config_update_slot)
        self.buf_ie_checkbox.stateChanged.connect(self.emit_config_update_slot)
        self.er_ie_checkbox.stateChanged.connect(self.emit_config_update_slot)
        self.func_master_tx_checkbox.stateChanged.connect(self.emit_config_update_slot)
        self.func_master_rx_checkbox.stateChanged.connect(self.emit_config_update_slot)

    def update_for_target_device(self, target_device_name, target_family_name, is_initial_call=False):
        self._is_initializing = True
        self.current_target_device = target_device_name
        self.current_mcu_family = target_family_name

        # Update I2C Instances
        current_instance = self.i2c_instance_combo.currentText()
        self.i2c_instance_combo.blockSignals(True)
        self.i2c_instance_combo.clear()
        available_instances = CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {}).get(target_device_name, {}).get(
            "i2c_instances", [])
        # Fallback if device-specific list is empty, use generic from family defines
        if not available_instances:
            i2c_info_map_key = f"I2C_PERIPHERALS_INFO_{target_family_name}"
            i2c_info_map = CURRENT_MCU_DEFINES.get(i2c_info_map_key,
                                                   CURRENT_MCU_DEFINES.get("I2C_PERIPHERALS_INFO", {}))
            available_instances = list(i2c_info_map.keys())
        self.i2c_instance_combo.addItems(available_instances)
        if current_instance in available_instances:
            self.i2c_instance_combo.setCurrentText(current_instance)
        elif available_instances:
            self.i2c_instance_combo.setCurrentIndex(0)
        self.i2c_instance_combo.blockSignals(False)

        # Update Clock Speeds (FMPI2C might only be on F446/F479 etc.)
        clock_speeds_key = f"I2C_CLOCK_SPEEDS_HZ_{target_family_name}"
        clock_speeds_map = CURRENT_MCU_DEFINES.get(clock_speeds_key, CURRENT_MCU_DEFINES.get("I2C_CLOCK_SPEEDS_HZ", {}))
        current_clk_speed = self.clock_speed_combo.currentText()
        self.clock_speed_combo.blockSignals(True)
        self.clock_speed_combo.clear()
        self.clock_speed_combo.addItems(clock_speeds_map.keys())
        if current_clk_speed in clock_speeds_map:
            self.clock_speed_combo.setCurrentText(current_clk_speed)
        elif clock_speeds_map:
            self.clock_speed_combo.setCurrentIndex(0)  # Default to first available
        self.clock_speed_combo.blockSignals(False)

        # Update Duty Cycle options (can be family specific)
        duty_cycles_key = f"I2C_DUTY_CYCLE_MODES_{target_family_name}"
        duty_cycles_map = CURRENT_MCU_DEFINES.get(duty_cycles_key, CURRENT_MCU_DEFINES.get("I2C_DUTY_CYCLE_MODES", {}))
        current_duty = self.duty_cycle_combo.currentText()
        self.duty_cycle_combo.blockSignals(True)
        self.duty_cycle_combo.clear()
        self.duty_cycle_combo.addItems(duty_cycles_map.keys())
        if current_duty in duty_cycles_map:
            self.duty_cycle_combo.setCurrentText(current_duty)
        elif duty_cycles_map:
            self.duty_cycle_combo.setCurrentIndex(0)
        self.duty_cycle_combo.blockSignals(False)

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
        instance_name = self.i2c_instance_combo.currentText()
        if not instance_name: self.pin_info_label.setText("Pinout: N/A"); return

        pin_sugg_map_key = f"I2C_PIN_CONFIG_SUGGESTIONS_{self.current_mcu_family}"
        pin_sugg_map = CURRENT_MCU_DEFINES.get(pin_sugg_map_key,
                                               CURRENT_MCU_DEFINES.get("I2C_PIN_CONFIG_SUGGESTIONS", {}))
        suggestions = pin_sugg_map.get(self.current_target_device, {}).get(instance_name, {})

        pin_text = []
        if suggestions:
            if "SCL" in suggestions: pin_text.append(f"SCL: {suggestions['SCL']}")
            if "SDA" in suggestions: pin_text.append(f"SDA: {suggestions['SDA']}")
            if "SMBA" in suggestions: pin_text.append(f"SMBA: {suggestions['SMBA']}")  # If SMBus supported
            self.pin_info_label.setText("; ".join(pin_text) if pin_text else "No specific pin suggestions.")
        else:
            self.pin_info_label.setText(f"Pinout: No suggestions for {instance_name} on {self.current_target_device}")

    def on_clock_speed_changed(self, speed_text):
        self.update_duty_cycle_visibility()
        self.emit_config_update_slot()

    def update_duty_cycle_visibility(self):
        if not self.enable_i2c_checkbox.isChecked():
            self.label_duty_cycle.setVisible(False);
            self.duty_cycle_combo.setVisible(False)
            return

        clock_speeds_map = CURRENT_MCU_DEFINES.get(f"I2C_CLOCK_SPEEDS_HZ_{self.current_mcu_family}",
                                                   CURRENT_MCU_DEFINES.get("I2C_CLOCK_SPEEDS_HZ", {}))
        speed_hz = clock_speeds_map.get(self.clock_speed_combo.currentText(), 0)

        # Fast Mode (>100kHz) is where duty cycle applies for F2/F4. F1 does not have DUTY bit.
        is_fast_mode_relevant = speed_hz > 100000 and self.current_mcu_family in ["STM32F2", "STM32F4"]
        self.label_duty_cycle.setVisible(is_fast_mode_relevant)
        self.duty_cycle_combo.setVisible(is_fast_mode_relevant)

    def on_dual_address_toggled(self, state):
        self.update_oa2_visibility()
        self.emit_config_update_slot()

    def update_oa2_visibility(self):
        if not self.enable_i2c_checkbox.isChecked():
            self.label_own_address2.setVisible(False);
            self.own_address2_lineedit.setVisible(False)
            return
        is_dual_enabled = self.dual_address_enable_checkbox.isChecked()
        self.label_own_address2.setVisible(is_dual_enabled)
        self.own_address2_lineedit.setVisible(is_dual_enabled)

    def update_ui_visibility(self):
        enabled = self.enable_i2c_checkbox.isChecked()
        self.params_groupbox.setEnabled(enabled)
        if enabled:  # Only update sub-visibilities if main group is enabled
            self.update_duty_cycle_visibility()
            self.update_oa2_visibility()
        else:  # If main group disabled, hide conditional sub-elements too
            self.label_duty_cycle.setVisible(False);
            self.duty_cycle_combo.setVisible(False)
            self.label_own_address2.setVisible(False);
            self.own_address2_lineedit.setVisible(False)

    def emit_config_and_update_visibility(self, _=None):
        self.update_ui_visibility()
        self.emit_config_update_slot()

    def emit_config_update_slot(self, _=None):
        if self._is_initializing: return
        self.config_updated.emit(self.get_config())

    def get_config(self):
        i2c_instance = self.i2c_instance_combo.currentText()
        if not i2c_instance:
            return {"instance_name": "", "enabled": False, "params": {}, "calculated": {},
                    "mcu_family": self.current_mcu_family, "target_device": self.current_target_device}
        try:
            own_addr1_val = int(self.own_address1_lineedit.text(), 0)
        except ValueError:
            own_addr1_val = 0
        try:
            own_addr2_val = int(self.own_address2_lineedit.text(), 0)
        except ValueError:
            own_addr2_val = 0

        params = {
            "instance_name": i2c_instance,
            "enabled": self.enable_i2c_checkbox.isChecked(),
            "clock_speed_str": self.clock_speed_combo.currentText(),
            "duty_cycle_str": self.duty_cycle_combo.currentText() if self.duty_cycle_combo.isVisible() else None,
            "clock_stretching_enabled": self.clock_stretching_enable_checkbox.isChecked(),
            "addressing_mode_str": self.addressing_mode_combo.currentText(),
            "own_address1": own_addr1_val,
            "dual_address_mode_enabled": self.dual_address_enable_checkbox.isChecked(),
            "own_address2": own_addr2_val if self.dual_address_enable_checkbox.isChecked() and self.own_address2_lineedit.isVisible() else 0,
            "general_call_address_enabled": self.general_call_enable_checkbox.isChecked(),
            "interrupt_event_enabled": self.ev_ie_checkbox.isChecked(),
            "interrupt_buffer_enabled": self.buf_ie_checkbox.isChecked(),
            "interrupt_error_enabled": self.er_ie_checkbox.isChecked(),
            "generate_master_tx_func": self.func_master_tx_checkbox.isChecked(),
            "generate_master_rx_func": self.func_master_rx_checkbox.isChecked(),
            "mcu_family": self.current_mcu_family,
            "target_device": self.current_target_device,
        }
        return {"instance_name": i2c_instance, "enabled": params["enabled"],
                "params": params, "calculated": {},
                "mcu_family": self.current_mcu_family, "target_device": self.current_target_device}