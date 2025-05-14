from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QComboBox,
                             QGroupBox, QCheckBox, QLabel)
from PyQt5.QtCore import pyqtSignal

from core.mcu_defines_loader import CURRENT_MCU_DEFINES


class DelayConfigWidget(QWidget):
    config_updated = pyqtSignal(dict)

    def __init__(self, parent=None):  # Removed parent from constructor args to match others
        super().__init__(parent)
        self._is_initializing = True
        self.current_target_device = "STM32F407VG"  # Updated by update_for_target_device
        self.current_mcu_family = "STM32F4"  # Updated by update_for_target_device

        self.main_layout = QVBoxLayout(self)
        self.delay_params_group = QGroupBox("Delay Function Generation")
        delay_form_layout = QFormLayout(self.delay_params_group)

        self.gen_ms_delay_checkbox = QCheckBox("Generate Millisecond Delay Function (Delay_ms)")
        delay_form_layout.addRow(self.gen_ms_delay_checkbox)
        self.gen_us_delay_checkbox = QCheckBox("Generate Microsecond Delay Function (Delay_us)")
        delay_form_layout.addRow(self.gen_us_delay_checkbox)

        self.delay_source_combo = QComboBox()
        # DELAY_SOURCES could be family specific if DWT/TIMx availability differs widely
        self.delay_source_combo.addItems(CURRENT_MCU_DEFINES.get("DELAY_SOURCES", ["SysTick"]))
        delay_form_layout.addRow(QLabel("Delay Source:"), self.delay_source_combo)

        self.delay_timer_instance_label = QLabel("Timer Instance for Delay:")
        self.delay_timer_instance_combo = QComboBox()
        delay_form_layout.addRow(self.delay_timer_instance_label, self.delay_timer_instance_combo)

        self.main_layout.addWidget(self.delay_params_group)
        self.main_layout.addStretch()

        self._connect_signals()
        self._is_initializing = False
        # Initial update_for_target_device and update_ui_visibility called by ConfigurationPane
        # For standalone use, they'd be called here after _is_initializing = False

    def _connect_signals(self):
        self.gen_ms_delay_checkbox.stateChanged.connect(self.emit_config_update_slot)
        self.gen_us_delay_checkbox.stateChanged.connect(self.emit_config_update_slot)
        self.delay_source_combo.currentTextChanged.connect(self.on_delay_source_changed)
        self.delay_timer_instance_combo.currentTextChanged.connect(self.emit_config_update_slot)

    def on_delay_source_changed(self, source_text):
        self.update_ui_visibility()  # Update visibility based on new source
        self.emit_config_update_slot()

    def update_ui_visibility(self):
        source = self.delay_source_combo.currentText()
        show_timer_selection = (source == "TIMx (General Purpose Timer)")

        self.delay_timer_instance_label.setVisible(show_timer_selection)
        self.delay_timer_instance_combo.setVisible(show_timer_selection)

        # DWT is good for us, less common for ms. Simple loop is possible for both.
        # SysTick is good for ms, rough for us without careful setup.
        # TIMx is good for both.
        can_do_us = source in ["SysTick", "DWT Cycle Counter", "TIMx (General Purpose Timer)",
                               "Simple Loop (Blocking, Inaccurate)"]
        can_do_ms = source in ["SysTick", "TIMx (General Purpose Timer)", "Simple Loop (Blocking, Inaccurate)"]

        self.gen_us_delay_checkbox.setEnabled(can_do_us)
        if not can_do_us and self.gen_us_delay_checkbox.isChecked():
            self.gen_us_delay_checkbox.setChecked(False)

        self.gen_ms_delay_checkbox.setEnabled(can_do_ms)
        if not can_do_ms and self.gen_ms_delay_checkbox.isChecked():
            self.gen_ms_delay_checkbox.setChecked(False)

    def update_for_target_device(self, target_device_name, target_family_name, is_initial_call=False):
        self._is_initializing = True
        self.current_target_device = target_device_name
        self.current_mcu_family = target_family_name

        # Update Delay Sources if they are family specific
        delay_sources_key = f"DELAY_SOURCES_{target_family_name}"
        delay_sources_list = CURRENT_MCU_DEFINES.get(delay_sources_key,
                                                     CURRENT_MCU_DEFINES.get("DELAY_SOURCES", ["SysTick"]))
        current_delay_source = self.delay_source_combo.currentText()
        self.delay_source_combo.blockSignals(True)
        self.delay_source_combo.clear()
        self.delay_source_combo.addItems(delay_sources_list)
        if current_delay_source in delay_sources_list:
            self.delay_source_combo.setCurrentText(current_delay_source)
        elif delay_sources_list:
            self.delay_source_combo.setCurrentIndex(0)
        self.delay_source_combo.blockSignals(False)

        # Update Timer Instance Combo for TIMx delay source
        self.delay_timer_instance_combo.blockSignals(True)
        current_timer_selection = self.delay_timer_instance_combo.currentText()
        self.delay_timer_instance_combo.clear()

        mcu_timer_instances = CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {}).get(target_device_name, {}).get(
            "timer_instances", [])
        timer_peripheral_info_map = CURRENT_MCU_DEFINES.get(f"TIMER_PERIPHERALS_INFO_{target_family_name}",
                                                            CURRENT_MCU_DEFINES.get("TIMER_PERIPHERALS_INFO", {}))
        delay_timer_candidates = CURRENT_MCU_DEFINES.get("DELAY_TIMER_CANDIDATES",
                                                         [])  # Generic list of preferred timer names

        available_delay_timers = []
        for timer_name in delay_timer_candidates:  # Check preferred ones first
            if timer_name in mcu_timer_instances:
                timer_info = timer_peripheral_info_map.get(timer_name, {})
                # Typically GP16 or GP32 timers are suitable
                if timer_info.get("type") in ["GP16", "GP32", "GP16_OR_GP32"]:
                    available_delay_timers.append(timer_name)

        # Fallback: if no preferred timers found, check all GP timers on device
        if not available_delay_timers:
            for timer_name in mcu_timer_instances:
                timer_info = timer_peripheral_info_map.get(timer_name, {})
                if timer_info.get("type") in ["GP16", "GP32", "GP16_OR_GP32"]:
                    available_delay_timers.append(timer_name)

        self.delay_timer_instance_combo.addItems(available_delay_timers)
        if current_timer_selection in available_delay_timers:
            self.delay_timer_instance_combo.setCurrentText(current_timer_selection)
        elif available_delay_timers:
            self.delay_timer_instance_combo.setCurrentIndex(0)
        self.delay_timer_instance_combo.blockSignals(False)

        self.update_ui_visibility()  # Refresh UI based on new settings
        self._is_initializing = False
        if not is_initial_call:
            self.emit_config_update_slot()

    def update_timer_configs(self, timer_configs):
        # This method is called by ConfigurationPane when TIMERS config changes.
        # It could be used to disable delay timer selection if the chosen timer
        # is already heavily configured by the TIMERS module in an incompatible way.
        # For now, this is a placeholder or for future advanced conflict detection.
        pass

    def emit_config_update_slot(self, _=None):
        if self._is_initializing: return
        self.config_updated.emit(self.get_config())

    def get_config(self):
        params = {
            "generate_ms_delay": self.gen_ms_delay_checkbox.isChecked(),
            "generate_us_delay": self.gen_us_delay_checkbox.isChecked(),
            "delay_source": self.delay_source_combo.currentText(),
            "delay_timer_instance": self.delay_timer_instance_combo.currentText() if self.delay_timer_instance_combo.isVisible() and self.delay_timer_instance_combo.count() > 0 else None,
            "mcu_family": self.current_mcu_family,
            "target_device": self.current_target_device,
        }
        # Add family and device for generator context
        return {"params": params}
