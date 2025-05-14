from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QComboBox,
                             QGroupBox, QCheckBox, QLabel)
from PyQt5.QtCore import pyqtSignal

from core.mcu_defines_loader import CURRENT_MCU_DEFINES


class DACChannelConfigWidget(QWidget):
    config_changed = pyqtSignal()

    def __init__(self, channel_id, dac_instance_name, mcu_family="STM32F4", parent=None):
        super().__init__(parent)
        self.channel_id = channel_id
        self.dac_instance_name = dac_instance_name
        self.mcu_family = mcu_family  # To adjust UI elements if needed
        self._is_internal_change = False  # For blocking signals during internal updates

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.group_box = QGroupBox(f"Channel {self.channel_id} (Output: N/A)")
        self.group_box.setCheckable(True)
        self.group_box.setChecked(False)
        form_layout = QFormLayout(self.group_box)

        self.output_buffer_combo = QComboBox()
        # Output buffer options are generally standard
        self.output_buffer_combo.addItems(
            CURRENT_MCU_DEFINES.get("DAC_OUTPUT_BUFFER_OPTIONS", {"Enabled": 0, "Disabled": 1}).keys())
        form_layout.addRow("Output Buffer:", self.output_buffer_combo)

        self.trigger_enable_checkbox = QCheckBox("Enable Trigger")
        form_layout.addRow(self.trigger_enable_checkbox)

        self.trigger_source_combo = QComboBox()
        # Trigger sources can vary by family (e.g. F1 has fewer timer triggers)
        trigger_sources_key = f"DAC_TRIGGER_SOURCES_{self.mcu_family}"
        dac_trigger_sources = CURRENT_MCU_DEFINES.get(trigger_sources_key,
                                                      CURRENT_MCU_DEFINES.get("DAC_TRIGGER_SOURCES", {"Software": 0}))
        self.trigger_source_combo.addItems(dac_trigger_sources.keys())
        self.trigger_source_combo.setCurrentText("Software")
        form_layout.addRow("Trigger Source:", self.trigger_source_combo)

        self.wave_gen_combo = QComboBox()
        # Wave generation options generally standard
        self.wave_gen_combo.addItems(CURRENT_MCU_DEFINES.get("DAC_WAVE_GENERATION", {"Disabled": 0}).keys())
        form_layout.addRow("Wave Generation:", self.wave_gen_combo)

        self.dma_enable_checkbox = QCheckBox("Enable DMA Request")
        form_layout.addRow(self.dma_enable_checkbox)

        layout.addWidget(self.group_box)
        self._connect_signals()
        self.update_visibility()  # Initial visibility update

    def _connect_signals(self):
        self.group_box.toggled.connect(self.on_config_changed_and_update_visibility)
        self.output_buffer_combo.currentTextChanged.connect(self.config_changed.emit)
        self.trigger_enable_checkbox.stateChanged.connect(self.on_config_changed_and_update_visibility)
        self.trigger_source_combo.currentTextChanged.connect(self.config_changed.emit)
        self.wave_gen_combo.currentTextChanged.connect(self.config_changed.emit)
        self.dma_enable_checkbox.stateChanged.connect(self.config_changed.emit)

    def on_config_changed_and_update_visibility(self):
        self.update_visibility()
        if not self._is_internal_change: self.config_changed.emit()

    def update_visibility(self):
        is_enabled = self.group_box.isChecked()
        # GroupBox handles disabling children. Specific logic:
        self.trigger_source_combo.setEnabled(is_enabled and self.trigger_enable_checkbox.isChecked())
        # Wave generation might depend on trigger for some MCUs (check RM)
        # self.wave_gen_combo.setEnabled(is_enabled and self.trigger_enable_checkbox.isChecked())

    def update_for_family_and_device(self, mcu_family, target_device):
        self._is_internal_change = True
        self.mcu_family = mcu_family

        # Update Trigger Sources based on the new family
        trigger_sources_key = f"DAC_TRIGGER_SOURCES_{self.mcu_family}"
        dac_trigger_sources_map = CURRENT_MCU_DEFINES.get(trigger_sources_key,
                                                          CURRENT_MCU_DEFINES.get("DAC_TRIGGER_SOURCES",
                                                                                  {"Software": 0}))

        current_trigger_source = self.trigger_source_combo.currentText()
        self.trigger_source_combo.clear()
        self.trigger_source_combo.addItems(dac_trigger_sources_map.keys())
        if current_trigger_source in dac_trigger_sources_map:
            self.trigger_source_combo.setCurrentText(current_trigger_source)
        elif dac_trigger_sources_map:
            self.trigger_source_combo.setCurrentText("Software")  # Default

        # Update Pin Label
        dac_pins_map_key = f"DAC_OUTPUT_PINS_{self.mcu_family}"
        dac_pins_map = CURRENT_MCU_DEFINES.get(dac_pins_map_key, CURRENT_MCU_DEFINES.get("DAC_OUTPUT_PINS", {}))
        pin_name = dac_pins_map.get(target_device, {}).get(f"DAC_OUT{self.channel_id}", "N/A")
        self.group_box.setTitle(f"Channel {self.channel_id} (Pin: {pin_name})")

        self._is_internal_change = False
        self.update_visibility()  # Refresh visibility based on new state

    def get_config(self):
        if not self.group_box.isChecked():
            return {"enabled": False, "channel_id": self.channel_id}
        return {
            "enabled": True,
            "channel_id": self.channel_id,
            "output_buffer_str": self.output_buffer_combo.currentText(),
            "trigger_enabled": self.trigger_enable_checkbox.isChecked(),
            "trigger_source_str": self.trigger_source_combo.currentText() if self.trigger_enable_checkbox.isChecked() else "Software",
            "wave_generation_str": self.wave_gen_combo.currentText(),
            "dma_enabled": self.dma_enable_checkbox.isChecked(),
        }


class DACConfigWidget(QWidget):
    config_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_initializing = True
        self.current_target_device = "STM32F407VG"  # Updated by update_for_target_device
        self.current_mcu_family = "STM32F4"  # Updated by update_for_target_device
        self.dac_instance_name = "DAC"  # Generic name for the peripheral block

        self.main_layout = QVBoxLayout(self)
        self.info_label = QLabel(f"DAC peripheral configuration.")
        self.info_label.setWordWrap(True)
        self.main_layout.addWidget(self.info_label)

        # Assuming max 2 channels for DAC peripheral block. Widgets created once.
        self.channel1_widget = DACChannelConfigWidget(1, self.dac_instance_name, self.current_mcu_family)
        self.main_layout.addWidget(self.channel1_widget)
        self.channel2_widget = DACChannelConfigWidget(2, self.dac_instance_name, self.current_mcu_family)
        self.main_layout.addWidget(self.channel2_widget)
        self.main_layout.addStretch()

        self._connect_signals()
        self._is_initializing = False
        # Initial update called by ConfigurationPane

    def _connect_signals(self):
        self.channel1_widget.config_changed.connect(self.emit_config_update_slot)
        self.channel2_widget.config_changed.connect(self.emit_config_update_slot)

    def update_for_target_device(self, target_device_name, target_family_name, is_initial_call=False):
        self._is_initializing = True
        self.current_target_device = target_device_name
        self.current_mcu_family = target_family_name

        # Check DAC availability and number of channels from CURRENT_MCU_DEFINES
        target_mcu_info = CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {}).get(target_device_name, {})
        dac_instances_on_mcu = target_mcu_info.get("dac_instances", [])  # e.g., ["DAC1"] or ["DAC1_CH1", "DAC1_CH2"]

        has_dac_peripheral = bool(dac_instances_on_mcu)  # True if any DAC instance mentioned

        # Determine if device has one or two DAC channels associated with the "DAC" block
        # This logic might need refinement based on how dac_instances is structured
        # For F100, DAC1 has CH1 and CH2. For F407, DAC block has CH1 and CH2.
        # Assume dac_instances like ["DAC1"] implies the DAC peripheral block is present.
        # Number of channels often fixed at 2 if DAC block exists, but some MCUs might have only DAC_CH1.

        dac_peripheral_info_key = f"DAC_PERIPHERALS_INFO_{target_family_name}"
        dac_peripheral_info_map = CURRENT_MCU_DEFINES.get(dac_peripheral_info_key,
                                                          CURRENT_MCU_DEFINES.get("DAC_PERIPHERALS_INFO", {}))

        # Find info for the first DAC instance (e.g., "DAC1")
        num_channels_for_dac_block = 0
        if dac_instances_on_mcu:
            # Assuming the dac_instances list contains the name of the DAC block (e.g. "DAC1")
            # And that DAC_PERIPHERALS_INFO has a "channels" key for it.
            # This is a simplification.
            first_dac_block_name = dac_instances_on_mcu[0]
            num_channels_for_dac_block = dac_peripheral_info_map.get(first_dac_block_name, {}).get("channels", 0)

        self.channel1_widget.setVisible(has_dac_peripheral and num_channels_for_dac_block >= 1)
        if self.channel1_widget.isVisible():
            self.channel1_widget.update_for_family_and_device(target_family_name, target_device_name)

        self.channel2_widget.setVisible(has_dac_peripheral and num_channels_for_dac_block >= 2)
        if self.channel2_widget.isVisible():
            self.channel2_widget.update_for_family_and_device(target_family_name, target_device_name)

        if has_dac_peripheral:
            self.info_label.setText(f"DAC peripheral configuration for {target_device_name} ({target_family_name}).")
        else:
            self.info_label.setText(f"DAC peripheral not available on {target_device_name}.")

        self._is_initializing = False
        if not is_initial_call:
            self.emit_config_update_slot()

    def get_config(self):
        target_mcu_info = CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {}).get(self.current_target_device, {})
        if not target_mcu_info.get("dac_instances", []):  # No DAC peripheral on this MCU
            return {"enabled": False, "dac_instance": self.dac_instance_name, "channels": [],
                    "mcu_family": self.current_mcu_family, "target_device": self.current_target_device}

        channels_config_list = []
        if self.channel1_widget.isVisible() and self.channel1_widget.group_box.isChecked():
            channels_config_list.append(self.channel1_widget.get_config())
        if self.channel2_widget.isVisible() and self.channel2_widget.group_box.isChecked():
            channels_config_list.append(self.channel2_widget.get_config())

        overall_enabled = bool(channels_config_list)  # Enabled if any channel is active

        return {
            "dac_instance": self.dac_instance_name,  # Generic name of the DAC block
            "enabled": overall_enabled,
            "channels": channels_config_list,
            "mcu_family": self.current_mcu_family,
            "target_device": self.current_target_device
        }

    def emit_config_update_slot(self, _=None):
        if self._is_initializing: return
        self.config_updated.emit(self.get_config())
