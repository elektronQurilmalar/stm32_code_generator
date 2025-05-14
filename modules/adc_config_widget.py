from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QCheckBox, QLabel, QScrollArea,
                             QGroupBox, QComboBox, QLineEdit, QPushButton, QHBoxLayout, QSpinBox, QFrame,
                             QSizePolicy)
from PyQt5.QtCore import pyqtSignal, Qt

from core.mcu_defines_loader import CURRENT_MCU_DEFINES


class ADCChannelConfigWidget(QWidget):
    config_changed = pyqtSignal()
    remove_clicked = pyqtSignal(object)  # object is this widget itself
    channel_selection_changed = pyqtSignal(str, str)  # old_channel_text, new_channel_text

    def __init__(self, rank_number, available_channels_list, parent=None):
        super().__init__(parent)
        self.rank = rank_number
        self.current_selected_channel = None  # Store the text of the currently selected channel

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Compact layout
        self.label_rank = QLabel(f"R{self.rank}:")
        self.combo_channel = QComboBox()
        self._populate_channels_combo(available_channels_list)  # Initial population

        self.combo_sampling_time = QComboBox()
        # Sampling times are mostly standard across F1/F2/F4, but F1 might have fewer options
        # For now, use F4 list, can be refined in update_for_target_device of parent
        self.combo_sampling_time.addItems(CURRENT_MCU_DEFINES.get("ADC_SAMPLING_TIMES_F4", ["3 cycles", "15 cycles"]))
        self.combo_sampling_time.setCurrentIndex(1)  # Default to 15 cycles

        self.btn_remove = QPushButton("X")
        self.btn_remove.setFixedWidth(25)
        self.btn_remove.clicked.connect(self._on_remove_clicked)

        layout.addWidget(self.label_rank)
        layout.addWidget(self.combo_channel)
        layout.addWidget(QLabel("Smpl:"))
        layout.addWidget(self.combo_sampling_time)
        layout.addWidget(self.btn_remove)
        self.setLayout(layout)

        self.combo_channel.currentTextChanged.connect(self._on_channel_selected_internal)
        self.combo_sampling_time.currentTextChanged.connect(self._on_config_changed_emit)

    def _populate_channels_combo(self, channels_list):
        self.combo_channel.blockSignals(True)
        current_selection = self.combo_channel.currentText()  # Preserve if possible
        self.combo_channel.clear()
        # Ensure channels_list contains strings, handle None or unexpected types
        safe_channels_list = [str(ch) for ch in channels_list if ch is not None] if channels_list else [
            "Error_IN0_EmptyList"]
        if not all(isinstance(item, str) for item in safe_channels_list):
            safe_channels_list = ["Error_IN0_InvalidData"]  # Fallback

        self.combo_channel.addItems(safe_channels_list)

        if current_selection in safe_channels_list:
            self.combo_channel.setCurrentText(current_selection)
        elif safe_channels_list:  # If current selection is no longer valid, select first available
            self.combo_channel.setCurrentIndex(0)

        self.current_selected_channel = self.combo_channel.currentText() if safe_channels_list else None
        self.combo_channel.blockSignals(False)

    def _on_channel_selected_internal(self, new_channel_text):
        # This is an internal handler for currentTextChanged
        old_channel = self.current_selected_channel
        if old_channel != new_channel_text:  # Only emit if actually changed
            self.current_selected_channel = new_channel_text
            self.channel_selection_changed.emit(old_channel, new_channel_text)  # Signal to parent (ADCConfigWidget)
            self._on_config_changed_emit()  # Also emit general config changed

    def _on_remove_clicked(self):
        self.remove_clicked.emit(self)

    def _on_config_changed_emit(self, _=None):  # Catch potential argument from signal
        self.config_changed.emit()

    def get_config(self):
        return {
            "rank": self.rank,
            "channel": self.combo_channel.currentText(),
            "sampling_time": self.combo_sampling_time.currentText()
        }

    def update_channels_list(self, new_channels_list):
        self._populate_channels_combo(new_channels_list)

    def update_sampling_times_list(self, new_sampling_times_list):
        self.combo_sampling_time.blockSignals(True)
        current_selection = self.combo_sampling_time.currentText()
        self.combo_sampling_time.clear()
        safe_sampling_list = [str(st) for st in new_sampling_times_list if
                              st is not None] if new_sampling_times_list else ["Error_Sample_Time"]
        self.combo_sampling_time.addItems(safe_sampling_list)
        if current_selection in safe_sampling_list:
            self.combo_sampling_time.setCurrentText(current_selection)
        elif safe_sampling_list:
            self.combo_sampling_time.setCurrentIndex(0)
        self.combo_sampling_time.blockSignals(False)


class ADCConfigWidget(QWidget):
    config_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_initializing = True
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        self.current_target_device = "STM32F407VG"  # Will be updated by ConfigurationPane
        self.current_mcu_family = "STM32F4"  # Will be updated
        self.all_available_channels_for_mcu = []  # Populated in update_for_target_device

        scroll_content_widget = QWidget()
        self.form_layout = QFormLayout(scroll_content_widget)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(scroll_content_widget)
        self.main_layout.addWidget(self.scroll_area)

        self.adc_instance_combo = QComboBox()
        self.form_layout.addRow(QLabel("ADC Instance:"), self.adc_instance_combo)
        self.enable_adc_checkbox = QCheckBox("Enable Selected ADC")
        self.form_layout.addRow(self.enable_adc_checkbox)

        self.common_settings_groupbox = QGroupBox("Common Settings")
        common_layout = QFormLayout(self.common_settings_groupbox)
        self.adc_prescaler_combo = QComboBox()
        common_layout.addRow(QLabel("Clock Prescaler:"), self.adc_prescaler_combo)
        self.vbatsens_checkbox = QCheckBox("Enable VBAT Channel Measurement")
        self.tsens_checkbox = QCheckBox("Enable Temperature Sensor Measurement")
        common_layout.addRow(self.vbatsens_checkbox)
        common_layout.addRow(self.tsens_checkbox)
        self.form_layout.addRow(self.common_settings_groupbox)

        adc_params_group = QGroupBox("ADC Parameters (ADCx_CR1, ADCx_CR2)")
        adc_params_layout = QFormLayout(adc_params_group)
        self.resolution_combo = QComboBox()
        adc_params_layout.addRow(QLabel("Resolution:"), self.resolution_combo)
        self.data_alignment_combo = QComboBox()
        self.data_alignment_combo.addItems(["Right", "Left"])
        adc_params_layout.addRow(QLabel("Data Alignment:"), self.data_alignment_combo)
        self.scan_mode_checkbox = QCheckBox("Scan Conversion Mode")
        adc_params_layout.addRow(self.scan_mode_checkbox)
        self.continuous_mode_checkbox = QCheckBox("Continuous Conversion Mode")
        adc_params_layout.addRow(self.continuous_mode_checkbox)
        self.form_layout.addRow(adc_params_group)

        regular_group = QGroupBox("Regular Conversion Mode")
        regular_main_layout = QVBoxLayout(regular_group)
        reg_form_layout = QFormLayout()
        self.reg_ext_trigger_enable_combo = QComboBox()
        reg_form_layout.addRow(QLabel("External Trigger:"), self.reg_ext_trigger_enable_combo)
        self.reg_ext_trigger_source_combo = QComboBox()
        reg_form_layout.addRow(QLabel("Trigger Source:"), self.reg_ext_trigger_source_combo)
        self.reg_num_conversions_spin = QSpinBox()
        self.reg_num_conversions_spin.setRange(1, 16)
        self.reg_num_conversions_spin.setValue(1)
        reg_form_layout.addRow(QLabel("Number of Conversions:"), self.reg_num_conversions_spin)
        regular_main_layout.addLayout(reg_form_layout)
        self.reg_channels_header_label = QLabel("<b>Configured Regular Channels:</b>")
        regular_main_layout.addWidget(self.reg_channels_header_label)
        self.reg_channels_layout = QVBoxLayout()
        self.reg_channels_layout.setSpacing(2)
        regular_main_layout.addLayout(self.reg_channels_layout)
        self.btn_add_reg_channel = QPushButton("Add Regular Channel (manual rank)")
        self.btn_add_reg_channel.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        regular_main_layout.addWidget(self.btn_add_reg_channel)
        self.form_layout.addRow(regular_group)

        interrupt_group = QGroupBox("Interrupts")
        interrupt_layout = QFormLayout(interrupt_group)
        self.eoc_ie_checkbox = QCheckBox("End of Regular Conversion (EOCIE)")
        self.ovr_ie_checkbox = QCheckBox("Overrun (OVRIE)")
        interrupt_layout.addRow(self.eoc_ie_checkbox)
        interrupt_layout.addRow(self.ovr_ie_checkbox)
        self.form_layout.addRow(interrupt_group)

        self.regular_channel_widgets = []
        self._connect_signals()
        self._is_initializing = False
        # Initial update called by ConfigurationPane via update_for_target_device

    def _connect_signals(self):
        self.adc_instance_combo.currentTextChanged.connect(self.emit_config_update_slot)
        self.enable_adc_checkbox.stateChanged.connect(self.emit_config_update_slot_and_update_visibility)
        # Common settings
        self.adc_prescaler_combo.currentTextChanged.connect(self.emit_config_update_slot)
        self.vbatsens_checkbox.stateChanged.connect(self.emit_config_update_slot)
        self.tsens_checkbox.stateChanged.connect(self.emit_config_update_slot)
        # ADC Parameters
        self.resolution_combo.currentTextChanged.connect(self.emit_config_update_slot)
        self.data_alignment_combo.currentTextChanged.connect(self.emit_config_update_slot)
        self.scan_mode_checkbox.stateChanged.connect(self.emit_config_update_slot)
        self.continuous_mode_checkbox.stateChanged.connect(self.emit_config_update_slot)
        # Regular Conversion
        self.reg_ext_trigger_enable_combo.currentTextChanged.connect(self.emit_config_update_slot)
        self.reg_ext_trigger_source_combo.currentTextChanged.connect(self.emit_config_update_slot)
        self.reg_num_conversions_spin.valueChanged.connect(self.on_num_conversions_changed)
        self.btn_add_reg_channel.clicked.connect(self.add_regular_channel_manually)
        # Interrupts
        self.eoc_ie_checkbox.stateChanged.connect(self.emit_config_update_slot)
        self.ovr_ie_checkbox.stateChanged.connect(self.emit_config_update_slot)

    def update_for_target_device(self, target_device_name, target_family_name, is_initial_call=False):
        if self._is_initializing and not is_initial_call: return
        self._is_initializing = True

        device_or_family_changed = (self.current_target_device != target_device_name or \
                                    self.current_mcu_family != target_family_name)

        self.current_target_device = target_device_name
        self.current_mcu_family = target_family_name

        # --- ADC Instances ---
        current_adc_instance_text = self.adc_instance_combo.currentText()
        self.adc_instance_combo.blockSignals(True)
        self.adc_instance_combo.clear()
        adc_instances_dev = CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {}).get(target_device_name, {}).get(
            'adc_instances', ["ADC1"])
        self.adc_instance_combo.addItems(adc_instances_dev)
        if current_adc_instance_text in adc_instances_dev:
            self.adc_instance_combo.setCurrentText(current_adc_instance_text)
        elif adc_instances_dev:
            self.adc_instance_combo.setCurrentIndex(0)
        self.adc_instance_combo.setEnabled(len(adc_instances_dev) > 1)
        self.adc_instance_combo.blockSignals(False)

        # --- Common Settings ---
        self.common_settings_groupbox.setTitle(
            f"Common Settings ({'ADC_CCR' if target_family_name != 'STM32F1' else 'RCC_CFGR for Prescaler'})")
        self.vbatsens_checkbox.setVisible(target_family_name != "STM32F1")  # VBATE in ADC_CCR for F2/F4
        self.tsens_checkbox.setVisible(target_family_name != "STM32F1")  # TSVREFE in ADC_CCR for F2/F4

        prescaler_list_key = f"ADC_PRESCALERS_{target_family_name}"  # e.g. ADC_PRESCALERS_STM32F1
        prescaler_list = CURRENT_MCU_DEFINES.get(prescaler_list_key, ["PCLK2 / 2", "PCLK2 / 4"])  # Fallback
        self.adc_prescaler_combo.blockSignals(True)
        current_prescaler = self.adc_prescaler_combo.currentText()
        self.adc_prescaler_combo.clear()
        self.adc_prescaler_combo.addItems(prescaler_list)
        if current_prescaler in prescaler_list:
            self.adc_prescaler_combo.setCurrentText(current_prescaler)
        elif prescaler_list:
            self.adc_prescaler_combo.setCurrentIndex(1)  # Default PCLK2/4
        self.adc_prescaler_combo.blockSignals(False)

        # --- ADC Parameters ---
        resolutions_key = f"ADC_RESOLUTIONS_{target_family_name}"
        resolutions_list = CURRENT_MCU_DEFINES.get(resolutions_key, ["12-bit"])
        self.resolution_combo.blockSignals(True)
        current_res = self.resolution_combo.currentText()
        self.resolution_combo.clear()
        self.resolution_combo.addItems(resolutions_list)
        if current_res in resolutions_list:
            self.resolution_combo.setCurrentText(current_res)
        else:
            self.resolution_combo.setCurrentText("12-bit")
        self.resolution_combo.setEnabled(len(resolutions_list) > 1)  # Disable if only one option (e.g., F1)
        self.resolution_combo.blockSignals(False)

        trigger_enable_list_key = f"ADC_EXT_TRIG_EDGE_{target_family_name}"
        trigger_enable_list = CURRENT_MCU_DEFINES.get(trigger_enable_list_key, ["Disabled", "Rising Edge"])
        self.reg_ext_trigger_enable_combo.blockSignals(True)
        curr_trig_en = self.reg_ext_trigger_enable_combo.currentText()
        self.reg_ext_trigger_enable_combo.clear()
        self.reg_ext_trigger_enable_combo.addItems(trigger_enable_list)
        if curr_trig_en in trigger_enable_list:
            self.reg_ext_trigger_enable_combo.setCurrentText(curr_trig_en)
        else:
            self.reg_ext_trigger_enable_combo.setCurrentIndex(0)
        self.reg_ext_trigger_enable_combo.blockSignals(False)

        trigger_sources_key = f"ADC_EXT_TRIG_REGULAR_{target_family_name}"
        trigger_sources_list = CURRENT_MCU_DEFINES.get(trigger_sources_key, ["Software"])
        self.reg_ext_trigger_source_combo.blockSignals(True)
        curr_trig_src = self.reg_ext_trigger_source_combo.currentText()
        self.reg_ext_trigger_source_combo.clear()
        self.reg_ext_trigger_source_combo.addItems(trigger_sources_list)
        if curr_trig_src in trigger_sources_list:
            self.reg_ext_trigger_source_combo.setCurrentText(curr_trig_src)
        else:
            self.reg_ext_trigger_source_combo.setCurrentText("Software")
        self.reg_ext_trigger_source_combo.blockSignals(False)

        # --- Available Channels ---
        adc_ch_map_key = f'ADC_CHANNELS_MAP_{self.current_mcu_family}'
        # Fallback to generic ADC_CHANNELS_MAP if family specific one isn't found, then to device specific inside that
        adc_channels_data_family = CURRENT_MCU_DEFINES.get(adc_ch_map_key,
                                                           CURRENT_MCU_DEFINES.get('ADC_CHANNELS_MAP', {}))
        self.all_available_channels_for_mcu = list(
            adc_channels_data_family.get(self.current_target_device, ["IN0_DefaultFromCode"]))
        if not self.all_available_channels_for_mcu: self.all_available_channels_for_mcu = ["IN0_NoMapForDevice"]

        # --- Interrupts ---
        self.ovr_ie_checkbox.setVisible(
            target_family_name != "STM32F1")  # OVR is status on F1, interrupt enable in F2/F4 CR1

        # --- Sampling Times (for channel widgets) ---
        sampling_times_key = f"ADC_SAMPLING_TIMES_{target_family_name}"
        sampling_times_list = CURRENT_MCU_DEFINES.get(sampling_times_key, ["3 cycles", "15 cycles"])  # Fallback

        # Recreate/update channel widgets if device or family changed significantly
        if device_or_family_changed or is_initial_call:
            current_num_conv = self.reg_num_conversions_spin.value()  # Preserve NofC
            self._clear_channel_widgets()
            # Restore NofC to trigger recreation of channel widgets with new settings
            self.reg_num_conversions_spin.setValue(0)  # Force change if current_num_conv is 1
            self.reg_num_conversions_spin.setValue(max(1, current_num_conv))  # This calls on_num_conversions_changed
        else:  # Just refresh lists within existing channel widgets
            self._refresh_channel_widgets_channel_lists()

        for cw in self.regular_channel_widgets:  # Update sampling times for existing/newly created widgets
            cw.update_sampling_times_list(sampling_times_list)

        self._is_initializing = False
        self.update_ui_visibility()  # Update visibility of all sections based on enable checkbox and family
        if not is_initial_call:
            self.emit_config_update_slot()

    def _clear_channel_widgets(self):
        while self.regular_channel_widgets:
            widget = self.regular_channel_widgets.pop(0)
            widget.deleteLater()
        # Ensure layout is also cleared (though QObject parentage should handle it)
        while self.reg_channels_layout.count():
            item = self.reg_channels_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

    def update_ui_visibility(self):
        enabled = self.enable_adc_checkbox.isChecked()
        # Iterate over QFormLayout rows and enable/disable widgets
        # This requires finding the start index of ADC parameters after the enable_adc_checkbox
        start_row_index = -1
        for i in range(self.form_layout.rowCount()):
            widget_item = self.form_layout.itemAt(i, QFormLayout.FieldRole)
            label_item = self.form_layout.itemAt(i, QFormLayout.LabelRole)
            spanning_item = self.form_layout.itemAt(i, QFormLayout.SpanningRole)  # For GroupBoxes

            # Find the enable_adc_checkbox itself
            if widget_item and widget_item.widget() is self.enable_adc_checkbox:
                start_row_index = i + 1
                break
            if spanning_item and spanning_item.widget() is self.enable_adc_checkbox:  # Should not happen with current layout
                start_row_index = i + 1
                break

        if start_row_index == -1:  # Should always find it
            print("Error: Could not find enable_adc_checkbox in layout for visibility toggle.")
            return

        for i in range(start_row_index, self.form_layout.rowCount()):
            label_widget = self.form_layout.itemAt(i, QFormLayout.LabelRole).widget() if self.form_layout.itemAt(i,
                                                                                                                 QFormLayout.LabelRole) else None
            field_widget = self.form_layout.itemAt(i, QFormLayout.FieldRole).widget() if self.form_layout.itemAt(i,
                                                                                                                 QFormLayout.FieldRole) else None
            spanning_widget = self.form_layout.itemAt(i, QFormLayout.SpanningRole).widget() if self.form_layout.itemAt(
                i, QFormLayout.SpanningRole) else None

            if label_widget: label_widget.setVisible(enabled)
            if field_widget: field_widget.setVisible(enabled)
            if spanning_widget: spanning_widget.setVisible(enabled)  # This will toggle GroupBoxes

        # Further fine-tune visibility based on family for specific items within enabled groups
        if enabled:
            is_f1 = (self.current_mcu_family == "STM32F1")
            self.vbatsens_checkbox.setVisible(not is_f1)
            self.tsens_checkbox.setVisible(not is_f1)
            self.ovr_ie_checkbox.setVisible(not is_f1)
            self.resolution_combo.setEnabled(not is_f1)  # F1 resolution is fixed
            self.common_settings_groupbox.setTitle(
                f"Common Settings ({'ADC_CCR' if not is_f1 else 'RCC_CFGR for Prescaler'})")

    def emit_config_update_slot_and_update_visibility(self, _=None):
        self.update_ui_visibility()
        self.emit_config_update_slot()

    def _get_currently_selected_channels_in_widgets(self):
        # Get channels selected in *other* widgets to determine availability for a new one
        return {cw.combo_channel.currentText() for cw in self.regular_channel_widgets if cw.combo_channel.currentText()}

    def _get_available_channels_for_new_widget(self):
        selected_in_others = self._get_currently_selected_channels_in_widgets()
        return [ch for ch in self.all_available_channels_for_mcu if ch not in selected_in_others]

    def _refresh_channel_widgets_channel_lists(self):
        # When a channel is selected in one widget, it should become unavailable in others
        all_selected_channels = self._get_currently_selected_channels_in_widgets()
        for cw in self.regular_channel_widgets:
            current_channel_of_this_widget = cw.combo_channel.currentText()
            # Channels available to *this* widget: all MCU channels minus those selected by *other* widgets
            available_for_this_widget = list(self.all_available_channels_for_mcu)
            for other_selected_channel in all_selected_channels:
                if other_selected_channel != current_channel_of_this_widget and other_selected_channel in available_for_this_widget:
                    available_for_this_widget.remove(other_selected_channel)

            # Ensure the widget's own current selection is part of its list if it's valid
            if current_channel_of_this_widget and current_channel_of_this_widget not in available_for_this_widget and current_channel_of_this_widget in self.all_available_channels_for_mcu:
                available_for_this_widget.append(current_channel_of_this_widget)
                available_for_this_widget.sort()  # Or maintain specific order

            cw.update_channels_list(available_for_this_widget)

    def on_num_conversions_changed(self, value, called_internally=False):
        if self._is_initializing and not called_internally: return
        # Avoid issues if called during a blockSignals period externally
        if not self._is_initializing and self.reg_num_conversions_spin.signalsBlocked(): return

        target_channels = value
        # Remove excess widgets
        while len(self.regular_channel_widgets) > target_channels:
            if self.regular_channel_widgets:  # Should always be true if len > 0
                widget_to_remove = self.regular_channel_widgets.pop()  # Remove from end
                widget_to_remove.deleteLater()

        # Add new widgets if needed
        current_ranks = {cw.rank for cw in self.regular_channel_widgets}
        for rank_to_add in range(1, target_channels + 1):
            if rank_to_add not in current_ranks:
                # Find the first available channel not used by other potential new widgets
                available_for_new = self._get_available_channels_for_new_widget()  # This considers existing widgets
                self._add_new_regular_channel_widget(rank_to_add, available_for_new, emit_update=False)  # Delay emit

        self._refresh_channel_widgets_channel_lists()  # Refresh all lists after adds/removes
        if not called_internally and not self._is_initializing:
            self.emit_config_update_slot()

    def add_regular_channel_manually(self):
        if self._is_initializing: return

        current_ranks = {cw.rank for cw in self.regular_channel_widgets}
        if len(current_ranks) >= 16: return  # Max 16 conversions

        next_rank = 1
        while next_rank in current_ranks: next_rank += 1
        if next_rank > 16: return  # Should be caught by len check too

        available_for_new = self._get_available_channels_for_new_widget()
        if not available_for_new:  # No more unique channels to assign
            # QMessageBox.information(self, "No Channels", "All available ADC channels are already assigned.")
            return

        self.reg_num_conversions_spin.blockSignals(True)
        if next_rank > self.reg_num_conversions_spin.value():
            self.reg_num_conversions_spin.setValue(next_rank)  # This will trigger on_num_conversions_changed
        self.reg_num_conversions_spin.blockSignals(False)

        # on_num_conversions_changed will handle adding the widget if NofC increased.
        # If NofC didn't change (because next_rank was <= current NofC), we might need to add it explicitly.
        # However, on_num_conversions_changed should have created placeholders up to NofC.
        # This manual add is more about finding a gap or forcing a specific rank.
        # Simpler: just increase NofC and let on_num_conversions_changed handle it.
        if self.reg_num_conversions_spin.value() < next_rank:  # If spin was not increased enough
            self.reg_num_conversions_spin.setValue(next_rank)
        else:  # if spin value already covers this rank, ensure widget exists
            if not any(cw.rank == next_rank for cw in self.regular_channel_widgets):
                self._add_new_regular_channel_widget(next_rank, available_for_new, emit_update=True)
            else:  # Widget for this rank already exists, just refresh lists
                self._refresh_channel_widgets_channel_lists()
                self.emit_config_update_slot()

    def _add_new_regular_channel_widget(self, rank, channels_list, emit_update=True):
        # Only add if a widget for this rank doesn't already exist
        if any(cw.rank == rank for cw in self.regular_channel_widgets): return

        channel_w = ADCChannelConfigWidget(rank, channels_list if channels_list else ["NoChannels"])
        # Update sampling times based on current family
        sampling_times_key = f"ADC_SAMPLING_TIMES_{self.current_mcu_family}"
        sampling_times_list = CURRENT_MCU_DEFINES.get(sampling_times_key, ["3 cycles", "15 cycles"])
        channel_w.update_sampling_times_list(sampling_times_list)

        channel_w.config_changed.connect(self.emit_config_update_slot)
        channel_w.remove_clicked.connect(self.remove_regular_channel_widget)
        channel_w.channel_selection_changed.connect(self._on_channel_widget_selection_changed)

        # Insert in sorted order of rank
        inserted_idx = -1
        for i, existing_widget in enumerate(self.regular_channel_widgets):
            if rank < existing_widget.rank:
                self.reg_channels_layout.insertWidget(i, channel_w)
                self.regular_channel_widgets.insert(i, channel_w)
                inserted_idx = i
                break
        if inserted_idx == -1:  # Append if rank is highest or list was empty
            self.reg_channels_layout.addWidget(channel_w)
            self.regular_channel_widgets.append(channel_w)

        # self._refresh_channel_widgets_channel_lists() # Called by caller typically
        if emit_update and not self._is_initializing:
            self.emit_config_update_slot()

    def _on_channel_widget_selection_changed(self, old_channel_text, new_channel_text):
        # This is called when a channel in an ADCChannelConfigWidget changes
        if self._is_initializing: return
        self._refresh_channel_widgets_channel_lists()  # Update available channels in other widgets
        # self.emit_config_update_slot() # Already emitted by ADCChannelConfigWidget's config_changed

    def remove_regular_channel_widget(self, widget_to_remove):
        if self._is_initializing: return
        if widget_to_remove in self.regular_channel_widgets:
            self.regular_channel_widgets.remove(widget_to_remove)
            widget_to_remove.deleteLater()

            # Adjust Number of Conversions spinbox
            self.reg_num_conversions_spin.blockSignals(True)
            current_nof_widgets = len(self.regular_channel_widgets)
            new_spin_value = max(1, current_nof_widgets)  # Min 1 conversion

            # If ranks are now sparse (e.g. R1, R3 exist, R2 removed), spin should reflect highest rank or count
            # For simplicity, set to current_nof_widgets. User can adjust if they want gaps.
            # More robust: find max rank among remaining widgets.
            max_remaining_rank = 0
            if self.regular_channel_widgets:
                max_remaining_rank = max(cw.rank for cw in self.regular_channel_widgets)
            new_spin_value = max(1, max_remaining_rank)  # Set to highest rank or 1

            if self.reg_num_conversions_spin.value() > new_spin_value:  # Only decrease if it was higher
                self.reg_num_conversions_spin.setValue(new_spin_value)
            self.reg_num_conversions_spin.blockSignals(False)

            self._refresh_channel_widgets_channel_lists()
            self.emit_config_update_slot()

    def get_config(self):
        # Ensure channels are sorted by rank for the generator
        regular_channels_config = sorted(
            [cw.get_config() for cw in self.regular_channel_widgets],
            key=lambda c: c['rank']
        )

        params = {
            "adc_instance": self.adc_instance_combo.currentText(),
            "enabled": self.enable_adc_checkbox.isChecked(),
            # Common
            "common_prescaler": self.adc_prescaler_combo.currentText(),
            "common_vbat_enabled": self.vbatsens_checkbox.isChecked() and self.vbatsens_checkbox.isVisible(),
            "common_tsens_enabled": self.tsens_checkbox.isChecked() and self.tsens_checkbox.isVisible(),
            # ADC Params
            "resolution": self.resolution_combo.currentText(),
            "data_alignment": self.data_alignment_combo.currentText(),
            "scan_mode": self.scan_mode_checkbox.isChecked(),
            "continuous_mode": self.continuous_mode_checkbox.isChecked(),
            # Regular Conversion
            "regular_trigger_edge": self.reg_ext_trigger_enable_combo.currentText(),
            "regular_trigger_source": self.reg_ext_trigger_source_combo.currentText(),
            "regular_num_conversions": self.reg_num_conversions_spin.value(),
            # This should match len(regular_channels) if scan mode is on
            "regular_channels": regular_channels_config,
            # Interrupts
            "interrupt_eoc": self.eoc_ie_checkbox.isChecked(),
            "interrupt_overrun": self.ovr_ie_checkbox.isChecked() and self.ovr_ie_checkbox.isVisible(),
            # MCU Context for generator
            "mcu_family": self.current_mcu_family,
            "target_device": self.current_target_device,
        }
        return {"params": params, "calculated": {}}  # Generator will handle 'calculated' if needed

    def emit_config_update_slot(self, _=None):
        if self._is_initializing: return
        self.config_updated.emit(self.get_config())