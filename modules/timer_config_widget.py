# --- MODIFIED FILE modules/timer_config_widget.py ---
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QComboBox,
                             QGroupBox, QCheckBox, QLabel, QHBoxLayout, QSpinBox, QScrollArea)
from PyQt5.QtCore import pyqtSignal

from core.mcu_defines_loader import CURRENT_MCU_DEFINES

QSPINBOX_MAX_RANGE = 2147483647  # Max value for a typical 32-bit signed int


class TimerChannelConfigWidget(QWidget):
    config_changed = pyqtSignal()

    def __init__(self, channel_number, timer_type="GP16", mcu_family="STM32F4"):
        super().__init__()
        self.channel_number = channel_number
        self.timer_type = timer_type
        self.mcu_family = mcu_family
        self._is_internal_change = False

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.group_box = QGroupBox(f"Channel {channel_number}")
        self.group_box.setCheckable(True)
        self.group_box.setChecked(False)
        self.channel_layout = QFormLayout(self.group_box)

        self.mode_combo = QComboBox()  # Disabled, OC, IC
        self.channel_layout.addRow("Mode:", self.mode_combo)

        self.oc_settings_group = QGroupBox("Output Compare")
        self.oc_layout = QFormLayout(self.oc_settings_group)
        self.oc_mode_combo = QComboBox()
        self.oc_layout.addRow("OC Mode:", self.oc_mode_combo)
        self.oc_pulse_spin = QSpinBox()
        self.oc_pulse_spin.setRange(0, 65535)  # Will be updated in update_for_timer_and_family
        self.oc_layout.addRow("Pulse (CCR):", self.oc_pulse_spin)
        self.oc_polarity_combo = QComboBox()
        self.oc_layout.addRow("Polarity:", self.oc_polarity_combo)
        self.oc_preload_checkbox = QCheckBox("Enable Preload (OCxPE)")
        self.oc_preload_checkbox.setChecked(True)
        self.oc_layout.addRow(self.oc_preload_checkbox)
        self.channel_layout.addRow(self.oc_settings_group)

        self.ic_settings_group = QGroupBox("Input Capture")
        self.ic_layout = QFormLayout(self.ic_settings_group)
        self.ic_polarity_combo = QComboBox()
        self.ic_layout.addRow("Polarity:", self.ic_polarity_combo)
        self.ic_selection_combo = QComboBox()
        self.ic_layout.addRow("Selection:", self.ic_selection_combo)
        self.ic_prescaler_combo = QComboBox()
        self.ic_layout.addRow("Prescaler:", self.ic_prescaler_combo)
        self.ic_filter_spin = QSpinBox()
        self.ic_filter_spin.setRange(0, 15)
        self.ic_layout.addRow("Filter (0-15):", self.ic_filter_spin)
        self.channel_layout.addRow(self.ic_settings_group)
        self.main_layout.addWidget(self.group_box)

        self._connect_signals()
        self._populate_channel_combos()  # Populate based on initial family
        self.update_visibility()

    def _connect_signals(self):
        self.group_box.toggled.connect(self.on_config_changed_and_update_visibility)
        self.mode_combo.currentTextChanged.connect(self.on_config_changed_and_update_visibility)
        # OC
        self.oc_mode_combo.currentTextChanged.connect(self.config_changed.emit)
        self.oc_pulse_spin.valueChanged.connect(self.config_changed.emit)
        self.oc_polarity_combo.currentTextChanged.connect(self.config_changed.emit)
        self.oc_preload_checkbox.stateChanged.connect(self.config_changed.emit)
        # IC
        self.ic_polarity_combo.currentTextChanged.connect(self.config_changed.emit)
        self.ic_selection_combo.currentTextChanged.connect(self.config_changed.emit)
        self.ic_prescaler_combo.currentTextChanged.connect(self.config_changed.emit)
        self.ic_filter_spin.valueChanged.connect(self.config_changed.emit)

    def _populate_channel_combos(self):
        self._is_internal_change = True
        # Modes
        self.mode_combo.clear()
        self.mode_combo.addItems(["Disabled", "Output Compare", "Input Capture"])

        # OC
        oc_modes_key = f"TIM_OC_MODES_{self.mcu_family}"
        oc_modes = CURRENT_MCU_DEFINES.get(oc_modes_key, CURRENT_MCU_DEFINES.get("TIM_OC_MODES", {}))
        self.oc_mode_combo.clear()
        self.oc_mode_combo.addItems(oc_modes.keys())
        default_oc_mode = "PWM Mode 1" if "PWM Mode 1" in oc_modes else (
            next(iter(oc_modes.keys()), "") if oc_modes else "")
        self.oc_mode_combo.setCurrentText(default_oc_mode)

        oc_polarity_key = f"TIM_OC_POLARITY_{self.mcu_family}"
        oc_polarities = CURRENT_MCU_DEFINES.get(oc_polarity_key, CURRENT_MCU_DEFINES.get("TIM_OC_POLARITY", {}))
        self.oc_polarity_combo.clear()
        self.oc_polarity_combo.addItems(oc_polarities.keys())

        # IC
        ic_polarity_key = f"TIM_IC_POLARITY_{self.mcu_family}"
        ic_polarities = CURRENT_MCU_DEFINES.get(ic_polarity_key, CURRENT_MCU_DEFINES.get("TIM_IC_POLARITY", {}))
        self.ic_polarity_combo.clear()
        self.ic_polarity_combo.addItems(ic_polarities.keys())

        ic_selection_key = f"TIM_IC_SELECTION_{self.mcu_family}"
        ic_selections = CURRENT_MCU_DEFINES.get(ic_selection_key, CURRENT_MCU_DEFINES.get("TIM_IC_SELECTION", {}))
        self.ic_selection_combo.clear()
        self.ic_selection_combo.addItems(ic_selections.keys())

        ic_prescaler_key = f"TIM_IC_PRESCALER_{self.mcu_family}"
        ic_prescalers = CURRENT_MCU_DEFINES.get(ic_prescaler_key, CURRENT_MCU_DEFINES.get("TIM_IC_PRESCALER", {}))
        self.ic_prescaler_combo.clear()
        self.ic_prescaler_combo.addItems(ic_prescalers.keys())
        self._is_internal_change = False

    def on_config_changed_and_update_visibility(self):
        self.update_visibility()
        if not self._is_internal_change: self.config_changed.emit()

    def update_visibility(self):
        is_channel_enabled = self.group_box.isChecked()
        mode = self.mode_combo.currentText()
        self.oc_settings_group.setVisible(is_channel_enabled and mode == "Output Compare")
        self.ic_settings_group.setVisible(is_channel_enabled and mode == "Input Capture")
        self.mode_combo.setEnabled(is_channel_enabled)

    def update_for_timer_and_family(self, timer_type, mcu_family, max_arr_val=65535):
        self._is_internal_change = True
        family_changed = self.mcu_family != mcu_family
        self.timer_type = timer_type
        self.mcu_family = mcu_family

        if family_changed:
            self._populate_channel_combos()  # Repopulate if family is different

        # Cap the OC pulse spinbox range to what QSpinBox can handle
        self.oc_pulse_spin.setRange(0, min(max_arr_val, QSPINBOX_MAX_RANGE))
        self.update_visibility()
        self._is_internal_change = False

    def get_config(self):
        is_enabled = self.group_box.isChecked()
        mode = self.mode_combo.currentText() if is_enabled else "Disabled"
        oc_config = None
        if is_enabled and mode == "Output Compare":
            oc_config = {"oc_mode": self.oc_mode_combo.currentText(), "pulse": self.oc_pulse_spin.value(),
                         "polarity": self.oc_polarity_combo.currentText(),
                         "preload_enable": self.oc_preload_checkbox.isChecked()}
        ic_config = None
        if is_enabled and mode == "Input Capture":
            ic_config = {"polarity": self.ic_polarity_combo.currentText(),
                         "selection": self.ic_selection_combo.currentText(),
                         "prescaler": self.ic_prescaler_combo.currentText(), "filter": self.ic_filter_spin.value()}
        return {"channel_number": self.channel_number, "enabled": is_enabled, "mode": mode,
                "output_compare": oc_config, "input_capture": ic_config}


class TimerConfigWidget(QWidget):
    config_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_initializing = True
        self.current_target_device = "STM32F407VG"  # Updated by ConfigurationPane
        self.current_mcu_family = "STM32F4"  # Updated by ConfigurationPane
        self.current_timer_info = {}  # Info for the currently selected timer instance
        self.channel_widgets = []

        self.main_layout = QVBoxLayout(self)
        instance_layout = QHBoxLayout()
        instance_layout.addWidget(QLabel("Configure Timer Instance:"))
        self.timer_instance_combo = QComboBox()
        instance_layout.addWidget(self.timer_instance_combo)
        instance_layout.addStretch()
        self.main_layout.addLayout(instance_layout)

        self.enable_timer_checkbox = QCheckBox("Enable Timer Instance")
        self.main_layout.addWidget(self.enable_timer_checkbox)

        self.scroll_area = QScrollArea();
        self.scroll_area.setWidgetResizable(True)
        scroll_content_widget = QWidget();
        self.params_layout = QVBoxLayout(scroll_content_widget)
        self.scroll_area.setWidget(scroll_content_widget);
        self.main_layout.addWidget(self.scroll_area)

        time_base_group = QGroupBox("Time Base Settings");
        time_base_form = QFormLayout(time_base_group)
        self.prescaler_spin = QSpinBox();
        self.prescaler_spin.setRange(0, 65535);
        time_base_form.addRow("Prescaler (PSC - 16-bit):", self.prescaler_spin)
        self.counter_mode_combo = QComboBox();
        time_base_form.addRow("Counter Mode:", self.counter_mode_combo)
        self.period_spin = QSpinBox();
        self.period_spin.setRange(0, 65535);  # Will be updated
        self.period_spin.setValue(65535);
        time_base_form.addRow("Period (Auto-Reload ARR):", self.period_spin)
        self.clock_division_combo = QComboBox();
        time_base_form.addRow("Clock Division (CKD):", self.clock_division_combo)
        self.auto_reload_preload_checkbox = QCheckBox("Auto-Reload Preload (ARPE)");
        self.auto_reload_preload_checkbox.setChecked(True);
        time_base_form.addRow(self.auto_reload_preload_checkbox)
        self.params_layout.addWidget(time_base_group)

        clock_source_group = QGroupBox("Clock Source");
        clock_source_form = QFormLayout(clock_source_group)
        self.clock_source_combo = QComboBox();
        clock_source_form.addRow("Source:", self.clock_source_combo)
        self.params_layout.addWidget(clock_source_group)

        self.channels_group = QGroupBox("Channels (Output Compare / Input Capture)");
        self.channels_layout = QVBoxLayout(self.channels_group)
        self.params_layout.addWidget(self.channels_group)

        interrupt_group = QGroupBox("Interrupts (DIER)");
        interrupt_form = QFormLayout(interrupt_group)
        self.update_interrupt_checkbox = QCheckBox("Update Interrupt (UIE)");
        interrupt_form.addRow(self.update_interrupt_checkbox)
        self.params_layout.addWidget(interrupt_group)

        self.adv_specific_group = QGroupBox("Advanced Timer Specific (TIM1/TIM8-like)")  # Dynamic title
        adv_specific_form = QFormLayout(self.adv_specific_group)
        self.main_output_enable_checkbox = QCheckBox("Main Output Enable (MOE)")
        adv_specific_form.addRow(self.main_output_enable_checkbox)
        self.params_layout.addWidget(self.adv_specific_group)

        self._connect_signals()
        self._is_initializing = False
        # Initial update done by ConfigurationPane

    def _connect_signals(self):
        self.timer_instance_combo.currentTextChanged.connect(self.on_timer_instance_changed)
        self.enable_timer_checkbox.stateChanged.connect(self.emit_config_and_update_overall_visibility)
        # Time Base
        self.prescaler_spin.valueChanged.connect(self.emit_config_update_slot)
        self.counter_mode_combo.currentTextChanged.connect(self.emit_config_update_slot)
        self.period_spin.valueChanged.connect(self.emit_config_update_slot)
        self.clock_division_combo.currentTextChanged.connect(self.emit_config_update_slot)
        self.auto_reload_preload_checkbox.stateChanged.connect(self.emit_config_update_slot)
        # Clock Source
        self.clock_source_combo.currentTextChanged.connect(self.emit_config_update_slot)
        # Interrupts
        self.update_interrupt_checkbox.stateChanged.connect(self.emit_config_update_slot)
        # Advanced
        self.main_output_enable_checkbox.stateChanged.connect(self.emit_config_update_slot)

    def update_for_target_device(self, target_device_name, target_family_name, is_initial_call=False):
        if self._is_initializing and not is_initial_call: return
        self._is_initializing = True

        family_or_device_changed = (self.current_mcu_family != target_family_name or \
                                    self.current_target_device != target_device_name)

        self.current_target_device = target_device_name
        self.current_mcu_family = target_family_name

        # Update Timer Instances
        current_timer_sel = self.timer_instance_combo.currentText()
        self.timer_instance_combo.blockSignals(True)
        self.timer_instance_combo.clear()
        available_instances = CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {}).get(target_device_name, {}).get(
            "timer_instances", [])
        if not available_instances:  # Fallback to generic list for family
            timer_info_map_key = f"TIMER_PERIPHERALS_INFO_{target_family_name}"
            timer_info_map = CURRENT_MCU_DEFINES.get(timer_info_map_key,
                                                     CURRENT_MCU_DEFINES.get("TIMER_PERIPHERALS_INFO", {}))
            available_instances = list(timer_info_map.keys())
        self.timer_instance_combo.addItems(available_instances)
        if current_timer_sel in available_instances:
            self.timer_instance_combo.setCurrentText(current_timer_sel)
        elif available_instances:
            self.timer_instance_combo.setCurrentIndex(0)
        self.timer_instance_combo.blockSignals(False)

        # This will trigger on_timer_instance_changed if selection actually changed or if it's the first population
        # which in turn calls update_ui_for_timer_instance
        if self.timer_instance_combo.count() > 0:  # If instances are available
            self.on_timer_instance_changed(self.timer_instance_combo.currentText(), is_update_for_target_call=True)
        else:  # No timers for this device/family, clear UI
            self._clear_all_timer_ui_fields()

        self._is_initializing = False
        if not is_initial_call:  # and family_or_device_changed: # Emit if truly changed
            self.emit_config_update_slot()

    def _clear_all_timer_ui_fields(self):
        # Clear dynamic combos and channel widgets
        self.counter_mode_combo.clear()
        self.clock_division_combo.clear()
        self.clock_source_combo.clear()
        while self.channel_widgets:
            cw = self.channel_widgets.pop()
            self.channels_layout.removeWidget(cw)
            cw.deleteLater()
        self.current_timer_info = {}
        self.update_overall_visibility()  # Hide groups

    def on_timer_instance_changed(self, instance_name, is_update_for_target_call=False):
        # is_update_for_target_call helps avoid double emit if called from update_for_target_device
        if self._is_initializing and not is_update_for_target_call: return

        timer_info_map_key = f"TIMER_PERIPHERALS_INFO_{self.current_mcu_family}"
        timer_info_map = CURRENT_MCU_DEFINES.get(timer_info_map_key,
                                                 CURRENT_MCU_DEFINES.get("TIMER_PERIPHERALS_INFO", {}))
        self.current_timer_info = timer_info_map.get(instance_name, {})

        self.update_ui_for_timer_instance()
        if not is_update_for_target_call:  # Avoid emitting if this was called from update_for_target_device
            self.emit_config_update_slot()

    def update_ui_for_timer_instance(self):
        # This method now assumes self.current_timer_info and self.current_mcu_family are correctly set.
        timer_type = self.current_timer_info.get("type", "GP16")
        max_channels = self.current_timer_info.get("max_channels", 0)
        has_bdtr = self.current_timer_info.get("has_bdtr", False)
        is_overall_enabled = self.enable_timer_checkbox.isChecked()

        self.adv_specific_group.setVisible(is_overall_enabled and has_bdtr)
        self.adv_specific_group.setTitle(
            f"Advanced Timer Specific ({self.timer_instance_combo.currentText() if has_bdtr else 'N/A'})")

        is_f1_family = (self.current_mcu_family == "STM32F1")

        if timer_type == "GP32":  # Specifically for 32-bit GP timers like F4's TIM2/5 or F2's TIM2/5
            max_arr_val = 0xFFFFFFFF
        elif timer_type == "ADV":  # ADV timers have 16-bit ARR across F1, F2, F4
            max_arr_val = 0xFFFF
        elif timer_type == "GP16_OR_GP32" and is_f1_family:  # F1's TIM2/TIM5
            # For F1, direct access to TIMx->ARR is 16-bit. UI doesn't support special 32-bit config.
            max_arr_val = 0xFFFF
        else:  # GP16, BASIC, or other unhandled types default to 16-bit
            max_arr_val = 0xFFFF

        self.period_spin.blockSignals(True)
        current_period = self.period_spin.value()
        self.period_spin.setRange(0, min(max_arr_val, QSPINBOX_MAX_RANGE))  # Apply cap for QSpinBox
        self.period_spin.setValue(min(current_period, min(max_arr_val, QSPINBOX_MAX_RANGE)))
        self.period_spin.blockSignals(False)

        # Populate combos based on family and timer type
        self._populate_main_timer_combos(timer_type)

        self.channels_group.setVisible(is_overall_enabled and max_channels > 0)
        # Pass the original hardware max_arr_val to channel widgets
        self._recreate_channel_widgets(max_channels, timer_type, max_arr_val)

        is_basic = (timer_type == "BASIC")
        self.counter_mode_combo.setEnabled(not is_basic)
        self.clock_division_combo.setEnabled(not is_basic)
        self.channels_group.setEnabled(not is_basic)
        # Basic timers usually only have internal clock and UIE.
        self.clock_source_combo.setEnabled(not is_basic)
        self.adv_specific_group.setEnabled(not is_basic and has_bdtr)  # Enable only if also not basic

    def _populate_main_timer_combos(self, timer_type):
        # Counter Mode
        counter_modes_key = f"TIM_COUNTER_MODES_{self.current_mcu_family}"
        counter_modes = CURRENT_MCU_DEFINES.get(counter_modes_key, CURRENT_MCU_DEFINES.get("TIM_COUNTER_MODES", {}))
        current_cm = self.counter_mode_combo.currentText()
        self.counter_mode_combo.blockSignals(True);
        self.counter_mode_combo.clear()
        self.counter_mode_combo.addItems(counter_modes.keys())
        if current_cm in counter_modes:
            self.counter_mode_combo.setCurrentText(current_cm)
        elif counter_modes:
            self.counter_mode_combo.setCurrentIndex(0)
        self.counter_mode_combo.blockSignals(False)

        # Clock Division
        clk_div_key = f"TIM_CLOCK_DIVISION_{self.current_mcu_family}"
        clk_divs = CURRENT_MCU_DEFINES.get(clk_div_key, CURRENT_MCU_DEFINES.get("TIM_CLOCK_DIVISION", {}))
        current_cd = self.clock_division_combo.currentText()
        self.clock_division_combo.blockSignals(True);
        self.clock_division_combo.clear()
        self.clock_division_combo.addItems(clk_divs.keys())
        if current_cd in clk_divs:
            self.clock_division_combo.setCurrentText(current_cd)
        elif clk_divs:
            self.clock_division_combo.setCurrentIndex(0)
        self.clock_division_combo.blockSignals(False)

        # Clock Source
        clk_src_list = [CURRENT_MCU_DEFINES.get("TIM_INTERNAL_CLOCK_SOURCE", "Internal Clock")]
        if timer_type != "BASIC":
            etr_modes_key = f"TIM_ETR_MODES_{self.current_mcu_family}"
            etr_modes = CURRENT_MCU_DEFINES.get(etr_modes_key, CURRENT_MCU_DEFINES.get("TIM_ETR_MODES", {}))
            clk_src_list.extend(etr_modes.keys())
        current_cs = self.clock_source_combo.currentText()
        self.clock_source_combo.blockSignals(True);
        self.clock_source_combo.clear()
        self.clock_source_combo.addItems(clk_src_list)
        if current_cs in clk_src_list:
            self.clock_source_combo.setCurrentText(current_cs)
        elif clk_src_list:
            self.clock_source_combo.setCurrentIndex(0)
        self.clock_source_combo.blockSignals(False)

    def _recreate_channel_widgets(self, max_channels, timer_type, max_arr_val):
        while self.channel_widgets:
            cw = self.channel_widgets.pop()
            self.channels_layout.removeWidget(cw)
            cw.deleteLater()

        if max_channels > 0 and self.channels_group.isVisible():  # Only create if group is visible
            for i in range(1, max_channels + 1):
                cw = TimerChannelConfigWidget(i, timer_type, self.current_mcu_family)
                cw.update_for_timer_and_family(timer_type, self.current_mcu_family, max_arr_val)
                cw.config_changed.connect(self.emit_config_update_slot)
                self.channels_layout.addWidget(cw)
                self.channel_widgets.append(cw)

    def emit_config_and_update_overall_visibility(self):
        self.update_overall_visibility()  # First update visibility of groups
        self.update_ui_for_timer_instance()  # Then update specifics within groups
        self.emit_config_update_slot()

    def update_overall_visibility(self):
        enabled = self.enable_timer_checkbox.isChecked()
        for i in range(self.params_layout.count()):
            widget = self.params_layout.itemAt(i).widget()
            if widget: widget.setEnabled(enabled)
        # After enabling/disabling groups, refresh specific visibilities inside them
        if enabled: self.update_ui_for_timer_instance()

    def emit_config_update_slot(self, _=None):
        if self._is_initializing: return
        self.config_updated.emit(self.get_config())

    def get_config(self):
        timer_instance = self.timer_instance_combo.currentText()
        if not timer_instance:
            return {"instance_name": "", "enabled": False, "params": {}, "calculated": {},
                    "mcu_family": self.current_mcu_family, "target_device": self.current_target_device}

        channels_config = [cw.get_config() for cw in self.channel_widgets]
        params = {
            "instance_name": timer_instance,
            "enabled": self.enable_timer_checkbox.isChecked(),
            "prescaler": self.prescaler_spin.value(),
            "counter_mode": self.counter_mode_combo.currentText(),
            "period": self.period_spin.value(),
            "clock_division": self.clock_division_combo.currentText(),
            "auto_reload_preload": self.auto_reload_preload_checkbox.isChecked(),
            "clock_source": self.clock_source_combo.currentText(),
            "update_interrupt_enable": self.update_interrupt_checkbox.isChecked(),
            "channels": channels_config,
            "main_output_enable": self.main_output_enable_checkbox.isChecked() if self.adv_specific_group.isVisible() and self.adv_specific_group.isEnabled() else False,
            "timer_type": self.current_timer_info.get("type", "GP16"),  # Add timer type for generator
            "has_bdtr": self.current_timer_info.get("has_bdtr", False),  # Add BDTR info
            "mcu_family": self.current_mcu_family,
            "target_device": self.current_target_device,
        }
        return {"instance_name": timer_instance, "enabled": params["enabled"],
                "params": params, "calculated": {},  # Calculated is handled by MainWindow now
                "mcu_family": self.current_mcu_family, "target_device": self.current_target_device}