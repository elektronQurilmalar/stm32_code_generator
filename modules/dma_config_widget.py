from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QComboBox,
                             QPushButton, QLabel, QScrollArea, QGroupBox, QHBoxLayout,
                             QSpinBox, QCheckBox)
from PyQt5.QtCore import pyqtSignal, Qt

from core.mcu_defines_loader import CURRENT_MCU_DEFINES


class DMAStreamChannelConfigWidget(QWidget):  # Renamed for clarity
    config_changed = pyqtSignal()
    remove_clicked = pyqtSignal(object)  # object is this widget

    def __init__(self, dma_controller_name, stream_or_channel_number, mcu_family, parent=None):
        super().__init__(parent)
        self.dma_controller_name = dma_controller_name
        self.stream_or_channel_number = stream_or_channel_number  # Stream for F2/F4, Channel for F1
        self.mcu_family = mcu_family
        self._is_internal_change = False

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)

        title_prefix = "Stream" if self.mcu_family in ["STM32F2", "STM32F4"] else "Channel"
        self.group_box = QGroupBox(f"{dma_controller_name} - {title_prefix} {stream_or_channel_number}")
        self.group_box.setCheckable(True)
        self.group_box.setChecked(False)  # Disabled by default
        self.config_layout = QFormLayout(self.group_box)  # Use a more generic name

        # --- Fields common to F1 Channel and F2/F4 Stream ---
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(CURRENT_MCU_DEFINES.get("DMA_DIRECTIONS", {}).keys())
        self.config_layout.addRow("Direction:", self.direction_combo)

        self.mode_combo = QComboBox()  # Normal, Circular. F1 doesn't have Peripheral Flow Control.
        dma_modes_key = f"DMA_MODES_{self.mcu_family}"
        dma_modes = CURRENT_MCU_DEFINES.get(dma_modes_key, CURRENT_MCU_DEFINES.get("DMA_MODES", {}))
        self.mode_combo.addItems(dma_modes.keys())
        self.config_layout.addRow("Mode:", self.mode_combo)

        self.mem_inc_combo = QComboBox()
        self.mem_inc_combo.addItems(CURRENT_MCU_DEFINES.get("DMA_INCREMENT_MODES", {}).keys())
        self.mem_inc_combo.setCurrentText("Increment")
        self.config_layout.addRow("Memory Increment:", self.mem_inc_combo)

        self.periph_inc_combo = QComboBox()
        self.periph_inc_combo.addItems(CURRENT_MCU_DEFINES.get("DMA_INCREMENT_MODES", {}).keys())
        self.periph_inc_combo.setCurrentText("Fixed")
        self.config_layout.addRow("Peripheral Increment:", self.periph_inc_combo)

        self.mem_data_size_combo = QComboBox()
        self.mem_data_size_combo.addItems(CURRENT_MCU_DEFINES.get("DMA_DATA_SIZES", {}).keys())
        self.config_layout.addRow("Memory Data Size:", self.mem_data_size_combo)

        self.periph_data_size_combo = QComboBox()
        self.periph_data_size_combo.addItems(CURRENT_MCU_DEFINES.get("DMA_DATA_SIZES", {}).keys())
        self.config_layout.addRow("Peripheral Data Size:", self.periph_data_size_combo)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(CURRENT_MCU_DEFINES.get("DMA_PRIORITIES", {}).keys())
        self.config_layout.addRow("Priority:", self.priority_combo)

        # --- F2/F4 Stream Specific Fields ---
        self.stream_channel_label = QLabel("Stream Channel (0-7):")  # For F2/F4 Stream's channel mux
        self.stream_channel_combo = QComboBox()
        self.stream_channel_combo.addItems([str(i) for i in range(8)])

        self.fifo_mode_label = QLabel("FIFO Mode:")
        self.fifo_mode_combo = QComboBox()
        self.fifo_mode_combo.addItems(CURRENT_MCU_DEFINES.get("DMA_FIFO_MODES", {}).keys())

        self.fifo_threshold_label = QLabel("FIFO Threshold:")
        self.fifo_threshold_combo = QComboBox()
        self.fifo_threshold_combo.addItems(CURRENT_MCU_DEFINES.get("DMA_FIFO_THRESHOLDS", {}).keys())

        # --- F1 Channel Specific Fields (or generic peripheral selection) ---
        self.peripheral_select_label = QLabel("Peripheral Request:")
        self.peripheral_select_combo = QComboBox()
        # Peripheral list will be populated in update_for_family_and_device

        # Add F2/F4 specific rows
        if self.mcu_family in ["STM32F2", "STM32F4"]:
            self.config_layout.addRow(self.stream_channel_label, self.stream_channel_combo)
            self.config_layout.addRow(self.peripheral_select_label,
                                      self.peripheral_select_combo)  # F2/F4 also map peripheral to stream/channel
            self.config_layout.addRow(self.fifo_mode_label, self.fifo_mode_combo)
            self.config_layout.addRow(self.fifo_threshold_label, self.fifo_threshold_combo)
        elif self.mcu_family == "STM32F1":
            # For F1, peripheral request is implicitly tied to the DMA channel number.
            # UI might show this mapping or allow selecting a peripheral which then dictates channel.
            # For now, peripheral_select_combo can list peripherals, generator maps to F1 channel.
            self.config_layout.addRow(self.peripheral_select_label, self.peripheral_select_combo)

        # Interrupts (common structure, specific bits differ)
        interrupt_group = QGroupBox("Interrupts")
        interrupt_layout = QVBoxLayout(interrupt_group)
        self.tc_int_checkbox = QCheckBox("Transfer Complete (TCIE)")
        self.ht_int_checkbox = QCheckBox("Half Transfer (HTIE)")
        self.te_int_checkbox = QCheckBox("Transfer Error (TEIE)")
        interrupt_layout.addWidget(self.tc_int_checkbox)
        interrupt_layout.addWidget(self.ht_int_checkbox)
        interrupt_layout.addWidget(self.te_int_checkbox)

        if self.mcu_family in ["STM32F2", "STM32F4"]:
            self.dme_int_checkbox = QCheckBox("Direct Mode Error (DMEIE)")  # F2/F4 specific
            self.fe_int_checkbox = QCheckBox("FIFO Error (FEIE)")  # F2/F4 specific
            interrupt_layout.addWidget(self.dme_int_checkbox)
            interrupt_layout.addWidget(self.fe_int_checkbox)
        self.config_layout.addRow(interrupt_group)

        remove_button_layout = QHBoxLayout()
        remove_button_layout.addStretch()
        self.btn_remove = QPushButton(f"Remove {title_prefix}")
        self.btn_remove.clicked.connect(lambda: self.remove_clicked.emit(self))
        remove_button_layout.addWidget(self.btn_remove)
        self.config_layout.addRow(remove_button_layout)

        main_layout.addWidget(self.group_box)
        self._connect_signals_internal()
        self.update_field_visibility()  # Initial visibility

    def _connect_signals_internal(self):
        self.group_box.toggled.connect(self.on_config_changed_and_update_visibility)
        # Connect all relevant field changes to on_config_changed_and_update_visibility or directly to config_changed.emit
        all_combos = [self.direction_combo, self.mode_combo, self.mem_inc_combo, self.periph_inc_combo,
                      self.mem_data_size_combo, self.periph_data_size_combo, self.priority_combo,
                      self.stream_channel_combo, self.peripheral_select_combo, self.fifo_mode_combo,
                      self.fifo_threshold_combo]
        for combo in all_combos:
            combo.currentTextChanged.connect(
                self.on_config_changed_and_update_visibility)  # Use this to also update visibility

        all_checkboxes = [self.tc_int_checkbox, self.ht_int_checkbox, self.te_int_checkbox]
        if self.mcu_family in ["STM32F2", "STM32F4"]:
            all_checkboxes.extend([self.dme_int_checkbox, self.fe_int_checkbox])
        for chkbox in all_checkboxes:
            chkbox.stateChanged.connect(self.config_changed.emit)

    def on_config_changed_and_update_visibility(self):
        self.update_field_visibility()
        if not self._is_internal_change: self.config_changed.emit()

    def update_for_family_and_device(self, mcu_family, target_device):
        self._is_internal_change = True
        # If family changes for an existing widget (should not happen if parent clears/recreates)
        if self.mcu_family != mcu_family:
            # This would require re-building parts of the UI (e.g. F1 vs F2/F4 specific fields)
            # For simplicity, DMAConfigWidget should recreate these widgets on family change.
            print(
                f"Warning: DMAStreamChannelConfigWidget family changed from {self.mcu_family} to {mcu_family}. UI may be inconsistent.")
            self.mcu_family = mcu_family  # Update internal state

        # Update peripheral combo based on family and device
        peripheral_map_key = f"DMA_PERIPHERAL_MAP_{target_device.upper()}"  # Try device specific first
        if not CURRENT_MCU_DEFINES.get(peripheral_map_key):  # Fallback to family generic
            peripheral_map_key = f"DMA_PERIPHERAL_MAP_{mcu_family}"

        peripheral_map = CURRENT_MCU_DEFINES.get(peripheral_map_key, {})
        available_peripherals = ["None (Memory-to-Memory)"] + list(peripheral_map.keys())

        current_peripheral = self.peripheral_select_combo.currentText()
        self.peripheral_select_combo.clear()
        self.peripheral_select_combo.addItems(available_peripherals)
        if current_peripheral in available_peripherals:
            self.peripheral_select_combo.setCurrentText(current_peripheral)
        elif available_peripherals:
            self.peripheral_select_combo.setCurrentIndex(0)

        # Auto-select channel for F2/F4 based on peripheral
        if self.mcu_family in ["STM32F2", "STM32F4"]:
            selected_peripheral_name = self.peripheral_select_combo.currentText()
            mapping_info = peripheral_map.get(selected_peripheral_name)  # (DMA_controller, stream_num, channel_num)
            if mapping_info and isinstance(mapping_info, tuple) and len(mapping_info) == 3:
                dma_ctrl, stream_idx_map, channel_num_map = mapping_info
                # Check if this peripheral is valid for the *current* stream widget
                if dma_ctrl == self.dma_controller_name and stream_idx_map == self.stream_or_channel_number:
                    if isinstance(channel_num_map, int):  # M2M might have "M2M" as channel
                        self.stream_channel_combo.setCurrentText(str(channel_num_map))

            # Auto-set direction based on peripheral name (TX/RX)
            if "_TX" in selected_peripheral_name:
                self.direction_combo.setCurrentText("Memory to Peripheral")
            elif "_RX" in selected_peripheral_name:
                self.direction_combo.setCurrentText("Peripheral to Memory")
            elif "MEM_TO_MEM" in selected_peripheral_name:
                self.direction_combo.setCurrentText("Memory to Memory")

        self._is_internal_change = False
        self.update_field_visibility()

    def update_field_visibility(self):
        is_enabled = self.group_box.isChecked()
        # All direct children of config_layout are handled by group_box.isChecked()

        is_f2_f4 = self.mcu_family in ["STM32F2", "STM32F4"]
        self.stream_channel_label.setVisible(is_enabled and is_f2_f4)
        self.stream_channel_combo.setVisible(is_enabled and is_f2_f4)
        self.fifo_mode_label.setVisible(is_enabled and is_f2_f4)
        self.fifo_mode_combo.setVisible(is_enabled and is_f2_f4)

        fifo_on = is_f2_f4 and self.fifo_mode_combo.currentText() == "FIFO Enabled"
        self.fifo_threshold_label.setVisible(is_enabled and fifo_on)
        self.fifo_threshold_combo.setVisible(is_enabled and fifo_on)
        if hasattr(self, 'fe_int_checkbox'):  # Check if F2/F4 specific interrupt exists
            self.fe_int_checkbox.setEnabled(is_enabled and fifo_on)
        if hasattr(self, 'dme_int_checkbox'):
            self.dme_int_checkbox.setEnabled(is_enabled)  # DME not strictly FIFO related

        is_m2m = self.direction_combo.currentText() == "Memory to Memory"
        # For F2/F4, stream channel is relevant even for M2M (usually CH0)
        # For F1, M2M is also usually fixed or less flexible.
        self.peripheral_select_combo.setEnabled(is_enabled and not is_m2m)
        if is_f2_f4:
            self.stream_channel_combo.setEnabled(is_enabled)  # For F2/F4, channel is always set

        # Disable peripheral selection for M2M
        if is_m2m and self.peripheral_select_combo.currentText() != "None (Memory-to-Memory)":
            self.peripheral_select_combo.setCurrentText("None (Memory-to-Memory)")

    def get_config(self):
        if not self.group_box.isChecked():
            return {"enabled": False, "dma_controller": self.dma_controller_name,
                    "id_num": self.stream_or_channel_number}  # id_num is stream or channel

        config_data = {
            "enabled": True,
            "dma_controller": self.dma_controller_name,
            "id_num": self.stream_or_channel_number,  # Stream or Channel number
            "direction_str": self.direction_combo.currentText(),
            "mode_str": self.mode_combo.currentText(),
            "mem_inc_str": self.mem_inc_combo.currentText(),
            "periph_inc_str": self.periph_inc_combo.currentText(),
            "mem_data_size_str": self.mem_data_size_combo.currentText(),
            "periph_data_size_str": self.periph_data_size_combo.currentText(),
            "priority_str": self.priority_combo.currentText(),
            "peripheral_str": self.peripheral_select_combo.currentText(),
            "tc_interrupt": self.tc_int_checkbox.isChecked(),
            "ht_interrupt": self.ht_int_checkbox.isChecked(),
            "te_interrupt": self.te_int_checkbox.isChecked(),
        }
        if self.mcu_family in ["STM32F2", "STM32F4"]:
            config_data.update({
                "stream_channel_str": self.stream_channel_combo.currentText(),
                "fifo_mode_str": self.fifo_mode_combo.currentText(),
                "fifo_threshold_str": self.fifo_threshold_combo.currentText() if self.fifo_mode_combo.currentText() == "FIFO Enabled" else None,
                "dme_interrupt": self.dme_int_checkbox.isChecked(),
                "fe_interrupt": self.fe_int_checkbox.isChecked() if self.fifo_mode_combo.currentText() == "FIFO Enabled" else False,
            })
        return config_data


class DMAConfigWidget(QWidget):
    config_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_initializing = True
        self.current_target_device = "STM32F407VG"
        self.current_mcu_family = "STM32F4"
        self.dma_item_widgets = {}  # Key: (dma_controller_name, stream_or_channel_num), Value: widget

        self.main_layout = QVBoxLayout(self)
        controller_selection_layout = QHBoxLayout()
        controller_selection_layout.addWidget(QLabel("DMA Controller:"))
        self.dma_controller_select_combo = QComboBox()
        controller_selection_layout.addWidget(self.dma_controller_select_combo)

        self.id_select_label = QLabel("Stream/Channel:")  # Dynamic label
        self.id_select_spin = QSpinBox()  # Range will be set dynamically
        controller_selection_layout.addWidget(self.id_select_label)
        controller_selection_layout.addWidget(self.id_select_spin)

        self.btn_add_item = QPushButton("Add/Configure Item")  # Dynamic button text
        self.btn_add_item.clicked.connect(self.add_or_focus_dma_item_widget)
        controller_selection_layout.addWidget(self.btn_add_item)
        controller_selection_layout.addStretch()
        self.main_layout.addLayout(controller_selection_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.configured_items_widget = QWidget()  # Renamed
        self.items_layout = QVBoxLayout(self.configured_items_widget)  # Renamed
        self.items_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.configured_items_widget)
        self.main_layout.addWidget(self.scroll_area)

        # Initial update by ConfigurationPane
        self._is_initializing = False

    def update_for_target_device(self, target_device_name, target_family_name, is_initial_call=False):
        if self._is_initializing and not is_initial_call: return
        self._is_initializing = True

        family_or_device_changed = (self.current_mcu_family != target_family_name or \
                                    self.current_target_device != target_device_name)

        self.current_target_device = target_device_name
        self.current_mcu_family = target_family_name

        dma_controllers_on_mcu = CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {}).get(target_device_name, {}).get(
            "dma_controllers", ["DMA1"])

        current_controller_sel = self.dma_controller_select_combo.currentText()
        self.dma_controller_select_combo.blockSignals(True)
        self.dma_controller_select_combo.clear()
        self.dma_controller_select_combo.addItems(dma_controllers_on_mcu)
        if current_controller_sel in dma_controllers_on_mcu:
            self.dma_controller_select_combo.setCurrentText(current_controller_sel)
        elif dma_controllers_on_mcu:
            self.dma_controller_select_combo.setCurrentIndex(0)
        self.dma_controller_select_combo.blockSignals(False)

        # Update ID select label and range based on family
        if self.current_mcu_family in ["STM32F2", "STM32F4"]:
            self.id_select_label.setText("Stream (0-7):")
            self.id_select_spin.setRange(0, 7)  # F2/F4 have 8 streams per DMA
            self.btn_add_item.setText("Add/Configure Stream")
        elif self.current_mcu_family == "STM32F1":
            # F1 DMA channels (e.g., DMA1 has 7 channels: 1-7, or 0-6 if 0-indexed in UI)
            # This needs to get max channels for selected DMA controller from defines
            selected_dma_ctrl = self.dma_controller_select_combo.currentText()
            dma_ctrl_info = CURRENT_MCU_DEFINES.get(f"DMA_PERIPHERALS_INFO_{self.current_mcu_family}",
                                                    CURRENT_MCU_DEFINES.get("DMA_PERIPHERALS_INFO", {})).get(
                selected_dma_ctrl, {})
            max_channels_f1 = dma_ctrl_info.get("channels", 7) - 1  # If 1-indexed in RM, make 0-indexed for UI

            self.id_select_label.setText(f"Channel (0-{max_channels_f1}):")
            self.id_select_spin.setRange(0, max_channels_f1)
            self.btn_add_item.setText("Add/Configure Channel")

        # Clear existing item widgets if family/device changed significantly
        if family_or_device_changed and not is_initial_call:
            for key in list(self.dma_item_widgets.keys()):
                widget = self.dma_item_widgets.pop(key)
                widget.deleteLater()
            # Clear layout too
            while self.items_layout.count():
                child = self.items_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        self._is_initializing = False
        if not is_initial_call:  # and family_or_device_changed:
            self.emit_config_update_slot()

    def add_or_focus_dma_item_widget(self):
        if self._is_initializing: return
        dma_controller = self.dma_controller_select_combo.currentText()
        id_num = self.id_select_spin.value()  # Stream or Channel number

        item_key = (dma_controller, id_num)

        if item_key not in self.dma_item_widgets:
            item_widget = DMAStreamChannelConfigWidget(dma_controller, id_num, self.current_mcu_family)
            item_widget.update_for_family_and_device(self.current_mcu_family,
                                                     self.current_target_device)  # Initial update for the widget
            item_widget.config_changed.connect(self.emit_config_update_slot)
            item_widget.remove_clicked.connect(self.remove_dma_item_widget)

            self.items_layout.addWidget(item_widget)
            self.dma_item_widgets[item_key] = item_widget
            item_widget.group_box.setChecked(True)  # Enable by default when added
        else:
            self.scroll_area.ensureWidgetVisible(self.dma_item_widgets[item_key])
            self.dma_item_widgets[item_key].group_box.setChecked(True)  # Ensure enabled

        self.emit_config_update_slot()

    def remove_dma_item_widget(self, widget_to_remove):
        if self._is_initializing: return
        key_to_remove = None
        for key, widget in self.dma_item_widgets.items():
            if widget is widget_to_remove:
                key_to_remove = key
                break
        if key_to_remove:
            self.dma_item_widgets.pop(key_to_remove)
            widget_to_remove.deleteLater()
            self.emit_config_update_slot()

    def get_config(self):
        dma_items_configs = []  # Renamed from streams_config
        for item_widget in self.dma_item_widgets.values():
            cfg = item_widget.get_config()
            if cfg.get("enabled"):
                dma_items_configs.append(cfg)

        # Sort by DMA controller then ID number for consistent output
        dma_items_configs.sort(key=lambda s: (s["dma_controller"], s["id_num"]))

        return {
            "target_device": self.current_target_device,
            "mcu_family": self.current_mcu_family,
            "dma_items": dma_items_configs  # Generic name for streams or channels
        }

    def emit_config_update_slot(self, _=None):
        if self._is_initializing: return
        self.config_updated.emit(self.get_config())