# --- MODIFIED FILE modules/mcu_config_widget.py ---
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QComboBox, QLabel
from PyQt5.QtCore import pyqtSignal

from core.mcu_defines_loader import set_current_mcu_defines, CURRENT_MCU_DEFINES, load_defines


class MCUConfigWidget(QWidget):
    config_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_initializing = True

        self.main_layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        self.mcu_family_combo = QComboBox()
        self.available_families = ["STM32F1", "STM32F2", "STM32F4"]
        self.mcu_family_combo.addItems(self.available_families)
        self.mcu_family_combo.setCurrentText("STM32F4")  # Default
        self.form_layout.addRow(QLabel("MCU Family:"), self.mcu_family_combo)

        self.mcu_device_combo = QComboBox()
        self.form_layout.addRow(QLabel("Target Device:"), self.mcu_device_combo)

        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addStretch()

        # Connect signals AFTER initial population if possible, or use _is_initializing
        self.mcu_family_combo.currentTextChanged.connect(self.on_family_changed_by_user)
        self.mcu_device_combo.currentTextChanged.connect(self.on_device_changed_by_user)

        self._is_initializing = False
        # Initial population will be triggered by ConfigurationPane calling update_for_target_device

    def on_family_changed_by_user(self, family_name):
        """Slot for when the family is changed directly by user interaction with the combo box."""
        if self._is_initializing:
            return
        # print(f"MCUConfigWidget: User changed family to {family_name}")
        self._update_devices_for_family(family_name)
        self.emit_config_update_slot()  # Emit that MCU config (family and new default device) changed

    def on_device_changed_by_user(self, device_name):
        """Slot for when the device is changed directly by user interaction with the combo box."""
        if self._is_initializing or not device_name:  # device_name can be empty if combo is cleared
            return
        # print(f"MCUConfigWidget: User changed device to {device_name}")
        self.emit_config_update_slot()  # Only device changed, family is the same

    def _update_devices_for_family(self, family_name):
        """Loads defines for the family and populates the device combo."""
        # print(f"MCUConfigWidget: _update_devices_for_family for {family_name}")
        self.mcu_device_combo.blockSignals(True)  # Prevent on_device_changed_by_user during repopulation

        if set_current_mcu_defines(family_name):
            self._populate_device_combo_from_defines()
        else:
            self.mcu_device_combo.clear()
            print(f"Warning: MCUConfigWidget - Failed to load defines for family {family_name}")

        self.mcu_device_combo.blockSignals(False)
        # If populate made a selection, on_device_changed_by_user will NOT fire because of blockSignals.
        # The overall config update is handled by the caller of this internal method (e.g., on_family_changed_by_user)

    def _populate_device_combo_from_defines(self):
        """Populates the device combo based on CURRENT_MCU_DEFINES. Assumes defines are loaded."""
        # print("MCUConfigWidget: _populate_device_combo_from_defines")
        current_selection_attempt = self.mcu_device_combo.currentText()  # Store to try to reselect
        self.mcu_device_combo.clear()

        target_devices_map = CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {})
        if not target_devices_map:
            print(f"Warning: No target devices in defines for family {CURRENT_MCU_DEFINES.get('FAMILY_NAME')}")
            return

        devices = sorted(list(target_devices_map.keys()))
        self.mcu_device_combo.addItems(devices)

        if current_selection_attempt in devices:
            self.mcu_device_combo.setCurrentText(current_selection_attempt)
        elif devices:
            self.mcu_device_combo.setCurrentIndex(0)  # Default to the first device in the new list
        # print(f"MCUConfigWidget: Device combo populated. Selected: {self.mcu_device_combo.currentText()}")

    def get_config(self):
        selected_family = self.mcu_family_combo.currentText()
        selected_device = self.mcu_device_combo.currentText()
        return {
            "mcu_family": selected_family,
            "target_device": selected_device
        }

    def emit_config_update_slot(self, _=None):  # _=None to accept potential arguments from signals
        if self._is_initializing:
            return
        # print(f"MCUConfigWidget: Emitting config_updated. Family: {self.mcu_family_combo.currentText()}, Device: {self.mcu_device_combo.currentText()}")
        config = self.get_config()
        self.config_updated.emit(config)

    def update_for_target_device(self, target_device_name, target_family_name, is_initial_call=False):
        # print(f"MCUConfigWidget: update_for_target_device: Device='{target_device_name}', Family='{target_family_name}', Initial={is_initial_call}")
        self._is_initializing = True

        # 1. Set Family
        if self.mcu_family_combo.currentText() != target_family_name:
            # print(f"  Setting family combo to {target_family_name}")
            self.mcu_family_combo.blockSignals(True)
            if target_family_name in self.available_families:
                self.mcu_family_combo.setCurrentText(target_family_name)
            else:
                print(f"Error: MCUConfigWidget - Update to unsupported family {target_family_name}")
                # Keep current family if target_family_name is invalid
                target_family_name = self.mcu_family_combo.currentText()
            self.mcu_family_combo.blockSignals(False)
            # After family is programmatically set, update devices for this family
            self._update_devices_for_family(target_family_name)
        else:
            # Family is the same, but ensure device list is correct if it's an initial call
            # or if defines might have been reloaded elsewhere.
            if is_initial_call:
                if not CURRENT_MCU_DEFINES.get('TARGET_DEVICES') or \
                        CURRENT_MCU_DEFINES.get('FAMILY_NAME') != target_family_name:
                    # print(f"  Initial call or defines mismatch, reloading for family {target_family_name}")
                    set_current_mcu_defines(target_family_name)  # Ensure defines are loaded
                self._populate_device_combo_from_defines()

        # 2. Set Device (after device list for the correct family is populated)
        # print(f"  Attempting to set device combo to {target_device_name}")
        self.mcu_device_combo.blockSignals(True)
        devices_in_combo = [self.mcu_device_combo.itemText(i) for i in range(self.mcu_device_combo.count())]
        if target_device_name in devices_in_combo:
            # print(f"    Device {target_device_name} found in combo.")
            if self.mcu_device_combo.currentText() != target_device_name:
                self.mcu_device_combo.setCurrentText(target_device_name)
        elif devices_in_combo:  # Target device not in list, select first one
            # print(f"    Device {target_device_name} NOT found. Selecting first: {devices_in_combo[0]}")
            if self.mcu_device_combo.currentIndex() != 0:
                self.mcu_device_combo.setCurrentIndex(0)
        else:
            # print(f"    Device combo is empty for family {target_family_name}.")
            pass  # Combo is empty, nothing to select
        self.mcu_device_combo.blockSignals(False)

        self._is_initializing = False
        # If it's an initial call, MainWindow will trigger the first full generation.
        # If it's a programmatic update (not by user directly changing combo),
        # the caller (e.g., ConfigurationPane via on_global_mcu_target_changed in MainWindow)
        # should handle triggering a regeneration. We avoid emitting here to prevent loops
        # if this was called as part of a larger update sequence.
        # print(f"MCUConfigWidget: update_for_target_device finished. Current state: Family={self.mcu_family_combo.currentText()}, Device={self.mcu_device_combo.currentText()}")

    def get_current_target_device(self):
        return self.mcu_device_combo.currentText()

    def get_current_mcu_family(self):
        return self.mcu_family_combo.currentText()