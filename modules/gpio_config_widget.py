# --- MODIFIED FILE modules/gpio_config_widget.py ---
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QComboBox,
                             QLineEdit, QPushButton, QLabel, QScrollArea, QGroupBox, QHBoxLayout, QFrame)
from PyQt5.QtCore import pyqtSignal, Qt

from core.mcu_defines_loader import CURRENT_MCU_DEFINES


class GPIOPinConfigWidget(QWidget):
    config_changed = pyqtSignal()
    remove_clicked = pyqtSignal(object)

    def __init__(self, pin_name="PA0", mcu_family="STM32F4"):
        super().__init__()
        self.pin_name = pin_name
        self.mcu_family = mcu_family  # Initial family
        self._is_internal_update = False

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)

        header_layout = QHBoxLayout()
        self.label_pin_name = QLabel(f"<b>{pin_name}</b>")
        header_layout.addWidget(self.label_pin_name)
        header_layout.addStretch()
        self.btn_remove = QPushButton("X")
        self.btn_remove.setFixedWidth(30)
        self.btn_remove.clicked.connect(lambda: self.remove_clicked.emit(self))
        header_layout.addWidget(self.btn_remove)
        main_layout.addLayout(header_layout)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 5, 0, 0)

        self.combo_mode = QComboBox()
        form_layout.addRow(QLabel("Mode:"), self.combo_mode)

        self.combo_pull = QComboBox()
        form_layout.addRow(QLabel("Pull:"), self.combo_pull)

        self.combo_speed = QComboBox()
        self.label_speed = QLabel("Speed (Output):")  # Label will be updated for F1
        form_layout.addRow(self.label_speed, self.combo_speed)

        self.line_af = QLineEdit()
        self.label_af = QLabel("AF/Remap:")
        form_layout.addRow(self.label_af, self.line_af)

        main_layout.addLayout(form_layout)
        self.setLayout(main_layout)

        # Connect signals after initial population by update_ui_for_family
        self.combo_mode.currentIndexChanged.connect(self.on_ui_element_changed)
        self.combo_pull.currentIndexChanged.connect(self.on_ui_element_changed)
        self.combo_speed.currentIndexChanged.connect(self.on_ui_element_changed)
        self.line_af.textChanged.connect(self.on_ui_element_changed)

        self.set_mcu_family(self.mcu_family, is_initial_setup=True)  # Call to set initial UI state

    def on_ui_element_changed(self):  # Renamed to avoid confusion
        if self._is_internal_update:
            return
        self._update_field_enabled_states()  # Update enabled states based on new selections
        self.config_changed.emit()

    def set_mcu_family(self, family_name, is_initial_setup=False):
        # print(f"GPIOPinConfigWidget ({self.pin_name}): Setting family to {family_name}")
        if self.mcu_family == family_name and not is_initial_setup:  # Avoid redundant updates
            # print(f"  Family already {family_name}, no UI change needed.")
            return

        self._is_internal_update = True
        self.mcu_family = family_name

        # --- Mode Combo ---
        current_mode_text = self.combo_mode.currentText()
        self.combo_mode.clear()
        f1_modes = [
            "Input Analog", "Input Floating", "Input Pull-up", "Input Pull-down",
            "Output Push-pull", "Output Open-drain",
            "Alternate Function Push-pull", "Alternate Function Open-drain"
        ]
        f2_f4_modes = [
            "Input", "Output PP", "Output OD",
            "Analog", "Alternate Function PP", "Alternate Function OD",
        ]
        modes_to_add = f1_modes if self.mcu_family == "STM32F1" else f2_f4_modes
        self.combo_mode.addItems(modes_to_add)

        if current_mode_text and self.combo_mode.findText(current_mode_text) != -1:
            self.combo_mode.setCurrentText(current_mode_text)
        elif modes_to_add:  # If old selection invalid, pick first from new list
            self.combo_mode.setCurrentIndex(0)

        # --- Pull Combo ---
        current_pull_text = self.combo_pull.currentText()
        self.combo_pull.clear()
        # For F1, "No Pull (default)" is a valid state, "Pull-up", "Pull-down" apply to specific input mode
        # For F2/F4, "No Pull-up/Pull-down" is the general no-pull state.
        pull_options = ["No Pull-up/Pull-down", "Pull-up", "Pull-down"]
        if self.mcu_family == "STM32F1":
            pull_options = ["No Pull (default)", "Pull-up", "Pull-down"]  # Slightly different wording for F1 UI clarity

        self.combo_pull.addItems(pull_options)
        if current_pull_text and self.combo_pull.findText(current_pull_text) != -1:
            self.combo_pull.setCurrentText(current_pull_text)
        elif pull_options:
            self.combo_pull.setCurrentIndex(0)

        # --- Speed Combo ---
        current_speed_text = self.combo_speed.currentText()
        self.combo_speed.clear()
        if self.mcu_family == "STM32F1":
            self.label_speed.setText("Speed (Output):")  # F1 speed directly sets MODE for output
            self.combo_speed.addItems(list(CURRENT_MCU_DEFINES.get("GPIO_F1_SPEED_TO_MODE_BITS_MAP", {}).keys()))
        else:
            self.label_speed.setText("Speed:")
            self.combo_speed.addItems(["Low", "Medium", "Fast", "High"])

        if current_speed_text and self.combo_speed.findText(current_speed_text) != -1:
            self.combo_speed.setCurrentText(current_speed_text)
        elif self.combo_speed.count() > 0:
            self.combo_speed.setCurrentIndex(0)

        # --- AF LineEdit and Label ---
        if self.mcu_family == "STM32F1":
            self.label_af.setText("Remap (AFIO):")
            self.line_af.setPlaceholderText("e.g., USART1_REMAP")
        else:
            self.label_af.setText("Alternate Func:")
            self.line_af.setPlaceholderText("AF0-AF15")

        self._is_internal_update = False
        self._update_field_enabled_states()  # Set initial enabled/disabled states after repopulating

    def _update_field_enabled_states(self):
        """Updates the enabled/disabled state of fields based on current selections."""
        if self._is_internal_update: return  # Don't do this if we are programmatically changing things

        mode_text = self.combo_mode.currentText()

        if self.mcu_family == "STM32F1":
            is_output_type = "Output" in mode_text or "Alternate Function" in mode_text
            is_af_type = "Alternate Function" in mode_text
            is_input_pupd_type_ui = mode_text in ["Input Pull-up", "Input Pull-down"]
            is_input_analog_or_float = mode_text in ["Input Analog", "Input Floating"]

            self.combo_speed.setEnabled(is_output_type)
            # For F1, pull selection is only meaningful if the mode is specifically "Input Pull-up" or "Input Pull-down" from UI
            self.combo_pull.setEnabled(is_input_pupd_type_ui)
            if not is_input_pupd_type_ui and self.combo_pull.currentText() not in ["No Pull (default)"]:
                # If mode changes from pupd, reset pull to "No Pull" if it's not already that
                # This prevents having "Pull-up" selected when mode is, e.g., "Input Analog"
                self._is_internal_update = True  # Prevent signal loop
                self.combo_pull.setCurrentText("No Pull (default)")
                self._is_internal_update = False

            self.line_af.setEnabled(is_af_type)
            self.label_af.setVisible(True)  # Remap might always be relevant to show for F1, enable/disable field itself

        else:  # F2/F4
            is_output_or_af = "Output" in mode_text or "Alternate Function" in mode_text
            is_af = "Alternate Function" in mode_text
            is_analog = mode_text == "Analog"  # F2/F4 has a distinct "Analog" mode

            self.combo_speed.setEnabled(is_output_or_af and not is_analog)
            self.line_af.setEnabled(is_af)
            self.label_af.setVisible(is_af)  # Only show AF field if AF mode selected
            self.combo_pull.setEnabled(not is_analog)
            if is_analog and self.combo_pull.currentText() != "No Pull-up/Pull-down":
                self._is_internal_update = True
                self.combo_pull.setCurrentText("No Pull-up/Pull-down")
                self._is_internal_update = False

    def get_config(self):
        return {
            "pin_name": self.pin_name,
            "mode": self.combo_mode.currentText(),
            "pull": self.combo_pull.currentText(),
            "speed": self.combo_speed.currentText() if self.combo_speed.isEnabled() else None,
            "af": self.line_af.text().strip() if self.line_af.isEnabled() and self.line_af.isVisible() else None,
        }


class GPIOConfigWidget(QWidget):
    config_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._is_initializing = True
        self.current_mcu_family = "STM32F4"  # Default, will be updated

        self.main_layout = QVBoxLayout(self)
        add_pin_group = QGroupBox("Add GPIO Pin")
        add_pin_layout = QHBoxLayout()

        self.combo_port_select = QComboBox()
        # Populated by update_for_target_device

        self.combo_pin_select = QComboBox()
        self.combo_pin_select.addItems([str(i) for i in range(16)])

        self.btn_add_pin = QPushButton("Add Pin")
        self.btn_add_pin.clicked.connect(self.add_pin_config_widget)

        add_pin_layout.addWidget(QLabel("Port:"))
        add_pin_layout.addWidget(self.combo_port_select)
        add_pin_layout.addWidget(QLabel("Pin:"))
        add_pin_layout.addWidget(self.combo_pin_select)
        add_pin_layout.addWidget(self.btn_add_pin)
        add_pin_group.setLayout(add_pin_layout)
        self.main_layout.addWidget(add_pin_group)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.configured_pins_widget = QWidget()
        self.pins_layout = QVBoxLayout(self.configured_pins_widget)
        self.pins_layout.setAlignment(Qt.AlignTop)
        self.pins_layout.setSpacing(10)
        self.configured_pins_widget.setLayout(self.pins_layout)  # This line was missing
        self.scroll_area.setWidget(self.configured_pins_widget)
        self.main_layout.addWidget(self.scroll_area)
        self.pin_widgets = []
        self._is_initializing = False

    def _populate_port_combo(self):  # Renamed for clarity
        # print(f"GPIOConfigWidget: _populate_port_combo for family {self.current_mcu_family}")
        self.combo_port_select.blockSignals(True)
        current_port_text = self.combo_port_select.currentText()
        self.combo_port_select.clear()

        # Use family-specific max port char from defines
        max_port_char_key = f"GPIO_MAX_PORT_CHAR_{self.current_mcu_family}"
        default_max_char_for_family = 'G'  # Generic default
        if self.current_mcu_family == "STM32F4":
            default_max_char_for_family = 'K'
        elif self.current_mcu_family == "STM32F2":
            default_max_char_for_family = 'I'
        elif self.current_mcu_family == "STM32F1":
            default_max_char_for_family = CURRENT_MCU_DEFINES.get("GPIO_MAX_PORT_CHAR_F1", 'G')

        max_port_char = CURRENT_MCU_DEFINES.get(max_port_char_key, default_max_char_for_family)
        max_port_char_ord = ord(max_port_char)

        ports = [f"GPIO{chr(ord('A') + i)}" for i in range(max_port_char_ord - ord('A') + 1)]
        self.combo_port_select.addItems(ports)

        if current_port_text in ports:
            self.combo_port_select.setCurrentText(current_port_text)
        elif ports:
            self.combo_port_select.setCurrentIndex(0)
        # print(f"  Port combo populated. Selected: {self.combo_port_select.currentText()}")
        self.combo_port_select.blockSignals(False)

    def update_for_target_device(self, target_device_name, target_family_name, is_initial_call=False):
        # print(f"GPIOConfigWidget: update_for_target_device: Device='{target_device_name}', Family='{target_family_name}', Initial={is_initial_call}")
        self._is_initializing = True

        family_changed = self.current_mcu_family != target_family_name
        self.current_mcu_family = target_family_name  # Update internal family state

        self._populate_port_combo()  # Update port list based on new family

        if family_changed:
            # print(f"  Family changed from {self.current_mcu_family} (old) to {target_family_name}. Updating pin widgets.")
            for pw_widget in self.pin_widgets:
                pw_widget.set_mcu_family(self.current_mcu_family)  # Pass the new family

        self._is_initializing = False
        if not is_initial_call and family_changed:
            # print("  Family changed, emitting config update.")
            self.emit_config_update_slot()

    def add_pin_config_widget(self):
        if self._is_initializing: return
        port_text = self.combo_port_select.currentText()
        if not port_text:
            # print("Error: No GPIO port selected for adding pin.")
            return

        port_char = port_text[-1]
        pin_num_str = self.combo_pin_select.currentText()
        pin_id = f"{port_char}{pin_num_str}"

        if any(pw.pin_name == pin_id for pw in self.pin_widgets):
            # print(f"Pin {pin_id} already configured.")
            return

        # Create new pin widget with the CURRENT family of the parent GPIOConfigWidget
        pin_config_w = GPIOPinConfigWidget(pin_id, self.current_mcu_family)
        pin_config_w.config_changed.connect(self.emit_config_update_slot)
        pin_config_w.remove_clicked.connect(self.remove_pin_config_widget)

        self.pins_layout.addWidget(pin_config_w)
        self.pin_widgets.append(pin_config_w)
        self.emit_config_update_slot()

    def remove_pin_config_widget(self, widget_to_remove):
        if self._is_initializing: return
        if widget_to_remove in self.pin_widgets:
            self.pin_widgets.remove(widget_to_remove)
            widget_to_remove.deleteLater()
            self.emit_config_update_slot()

    def get_config(self):
        pins_config = {}
        for pin_widget in self.pin_widgets:
            cfg = pin_widget.get_config()
            pins_config[cfg["pin_name"]] = cfg
        return {"pins": pins_config, "mcu_family": self.current_mcu_family}

    def emit_config_update_slot(self, _=None):  # _ to accept potential signal args
        if self._is_initializing: return
        # print(f"GPIOConfigWidget: Emitting config_updated. Current family: {self.current_mcu_family}")
        self.config_updated.emit(self.get_config())