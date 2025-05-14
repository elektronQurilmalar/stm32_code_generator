# --- MODIFIED FILE modules/rcc_config_widget.py ---

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QCheckBox, QLabel,
                             QGroupBox, QComboBox, QLineEdit)
from PyQt5.QtCore import pyqtSignal

from core.mcu_defines_loader import CURRENT_MCU_DEFINES


class RCCConfigWidget(QWidget):
    config_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_initializing = True
        self._is_auto_calculating_pll = False
        self.current_target_device = ""
        self.current_mcu_family = ""

        self.layout = QVBoxLayout(self)
        self.main_form_layout = QFormLayout()
        self.rcc_group_box = QGroupBox("RCC Configuration")

        self.hsi_checkbox = QCheckBox("Enable HSI")
        self.hsi_checkbox.setChecked(True)
        self.main_form_layout.addRow(self.hsi_checkbox)

        self.hse_checkbox = QCheckBox("Enable HSE")
        self.main_form_layout.addRow(self.hse_checkbox)
        self.label_hse_value = QLabel("HSE Value (Hz):")
        self.hse_value_lineedit = QLineEdit()
        self.main_form_layout.addRow(self.label_hse_value, self.hse_value_lineedit)
        self.hse_bypass_checkbox = QCheckBox("HSE Bypass")
        self.main_form_layout.addRow(QLabel("HSE Bypass Mode:"), self.hse_bypass_checkbox)

        self.pll_enable_for_sysclk_checkbox = QCheckBox("Use PLL as SYSCLK source")
        self.main_form_layout.addRow(self.pll_enable_for_sysclk_checkbox)

        self.label_target_sysclk = QLabel("Target SYSCLK (Hz) with PLL:")  # For F2/F4 target
        self.target_sysclk_lineedit = QLineEdit()  # User input for F2/F4 target
        self.main_form_layout.addRow(self.label_target_sysclk, self.target_sysclk_lineedit)

        self.auto_calc_status_label = QLabel("PLL params status.")  # Shows calculated/error
        self.main_form_layout.addRow(self.auto_calc_status_label)

        self.label_pll_source = QLabel("PLL Source:")
        self.pll_source_combo = QComboBox()
        self.main_form_layout.addRow(self.label_pll_source, self.pll_source_combo)

        self.label_pllm_or_xtpre = QLabel("PLLM / PLLXTPRE:")  # Dynamic label
        self.pllm_or_xtpre_lineedit = QLineEdit()  # User input for F1 XTPRE, calc for F2/F4 M
        self.main_form_layout.addRow(self.label_pllm_or_xtpre, self.pllm_or_xtpre_lineedit)

        self.label_plln_or_mul = QLabel("PLLN / PLLMUL:")  # Dynamic label
        self.plln_or_mul_lineedit = QLineEdit()  # User input for F1 MUL, calc for F2/F4 N
        self.main_form_layout.addRow(self.label_plln_or_mul, self.plln_or_mul_lineedit)

        self.label_pllp = QLabel("PLLP (calculated):")  # Only for F2/F4
        self.pllp_lineedit = QLineEdit()
        self.main_form_layout.addRow(self.label_pllp, self.pllp_lineedit)

        self.label_pllq = QLabel("PLLQ (USB/SDIO - if applicable):")  # Only for F2/F4
        self.pllq_lineedit = QLineEdit("7")
        self.main_form_layout.addRow(self.label_pllq, self.pllq_lineedit)

        self.sysclk_source_combo = QComboBox()
        self.sysclk_source_combo.addItems(["HSI", "HSE", "PLL"])
        self.main_form_layout.addRow(QLabel("System Clock (SYSCLK) Source:"), self.sysclk_source_combo)

        self.ahb_div_combo = QComboBox()
        self.main_form_layout.addRow(QLabel("AHB Prescaler (HCLK):"), self.ahb_div_combo)
        self.apb1_div_combo = QComboBox()
        self.main_form_layout.addRow(QLabel("APB1 Prescaler (PCLK1):"), self.apb1_div_combo)
        self.apb2_div_combo = QComboBox()
        self.main_form_layout.addRow(QLabel("APB2 Prescaler (PCLK2):"), self.apb2_div_combo)

        self.rcc_group_box.setLayout(self.main_form_layout)
        self.layout.addWidget(self.rcc_group_box)

        self._connect_signals()
        self._is_initializing = False

    def _connect_signals(self):
        # Critical for PLL calculation/verification
        critical_widgets = [
            self.hse_checkbox, self.hse_value_lineedit,
            self.target_sysclk_lineedit,  # For F2/F4 target input
            self.pll_source_combo,
            self.pllm_or_xtpre_lineedit,  # For F1 manual input
            self.plln_or_mul_lineedit  # For F1 manual input
        ]
        for widget in critical_widgets:
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self.on_critical_param_changed)
            elif isinstance(widget, QCheckBox):
                widget.stateChanged.connect(self.on_critical_param_changed)
            elif isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(self.on_critical_param_changed)

        # Other params that trigger a general config update
        other_widgets = [
            self.hsi_checkbox, self.hse_bypass_checkbox,
            self.pllq_lineedit,  # For F2/F4
            self.ahb_div_combo, self.apb1_div_combo, self.apb2_div_combo
        ]
        for widget in other_widgets:
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self.emit_config_update_slot)
            elif isinstance(widget, QCheckBox):
                widget.stateChanged.connect(self.emit_config_update_slot)
            elif isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(self.emit_config_update_slot)

        self.pll_enable_for_sysclk_checkbox.stateChanged.connect(self.on_pll_enable_changed)
        self.sysclk_source_combo.currentTextChanged.connect(self.on_sysclk_source_changed)

    def update_for_target_device(self, target_device_name, target_family_name, is_initial_call=False):
        self._is_initializing = True

        family_changed = self.current_mcu_family != target_family_name
        self.current_target_device = target_device_name
        self.current_mcu_family = target_family_name

        target_devices_map = CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {})  # Should be generic key now
        device_info = target_devices_map.get(self.current_target_device, {})

        # --- Set HSE Default ---
        self.hse_value_lineedit.blockSignals(True)
        self.hse_value_lineedit.setText(str(CURRENT_MCU_DEFINES.get('HSE_DEFAULT_HZ', 8000000)))
        self.hse_value_lineedit.blockSignals(False)

        # --- Set Target SYSCLK default (for F2/F4 auto-calc guidance) ---
        # For F1, this field is less critical as user sets PLL factors, but can be a reference
        max_sysclk_val = device_info.get("max_sysclk_hz", 72000000)  # Generic default
        if self.current_mcu_family == "STM32F4":
            max_sysclk_map_dev = CURRENT_MCU_DEFINES.get('SYSCLK_MAX_HZ_MAP', {}).get(target_device_name, {})
            if "VOS1_od" in max_sysclk_map_dev:
                max_sysclk_val = max_sysclk_map_dev["VOS1_od"]
            elif "VOS1_old" in max_sysclk_map_dev:
                max_sysclk_val = max_sysclk_map_dev["VOS1_old"]
            elif "VOS1" in max_sysclk_map_dev:
                max_sysclk_val = max_sysclk_map_dev["VOS1"]
        self.target_sysclk_lineedit.blockSignals(True)
        self.target_sysclk_lineedit.setText(str(int(max_sysclk_val)))
        self.target_sysclk_lineedit.blockSignals(False)

        # --- PLL Source Combo ---
        self.pll_source_combo.blockSignals(True)
        current_pll_src = self.pll_source_combo.currentText()
        self.pll_source_combo.clear()
        self.pll_source_combo.addItem("HSI")
        self.pll_source_combo.addItem("HSE")
        if self.current_mcu_family == "STM32F1":
            self.pll_source_combo.addItem("HSI/2")

        possible_pll_sources = [self.pll_source_combo.itemText(i) for i in range(self.pll_source_combo.count())]
        if current_pll_src in possible_pll_sources and not (is_initial_call or family_changed):
            self.pll_source_combo.setCurrentText(current_pll_src)
        else:  # Default on initial or family change
            self.pll_source_combo.setCurrentText("HSE")
        self.pll_source_combo.blockSignals(False)

        # --- Adapt PLL parameter labels and interactivity based on family ---
        is_f1 = (self.current_mcu_family == "STM32F1")

        self.label_target_sysclk.setText(
            "Target SYSCLK (Hz) with PLL:" if not is_f1 else "Target SYSCLK (Hz) with PLL (for reference):")
        self.target_sysclk_lineedit.setReadOnly(is_f1)  # For F1, it's a reference, user sets factors

        self.label_pllm_or_xtpre.setText("PLLXTPRE (1 or 2):" if is_f1 else "PLLM (calculated for target):")
        self.pllm_or_xtpre_lineedit.setReadOnly(not is_f1)  # User inputs for F1
        if is_f1 and (is_initial_call or family_changed): self.pllm_or_xtpre_lineedit.setText("1")

        self.label_plln_or_mul.setText("PLLMUL (2-16):" if is_f1 else "PLLN (calculated for target):")
        self.plln_or_mul_lineedit.setReadOnly(not is_f1)  # User inputs for F1
        if is_f1 and (is_initial_call or family_changed): self.plln_or_mul_lineedit.setText("9")

        self.label_pllp.setVisible(not is_f1);
        self.pllp_lineedit.setVisible(not is_f1)
        self.pllp_lineedit.setReadOnly(True)  # Always calculated for F2/F4

        self.label_pllq.setVisible(not is_f1);
        self.pllq_lineedit.setVisible(not is_f1)
        # self.pllq_lineedit.setReadOnly(is_f1) # Q is user-set for F2/F4, non-existent for F1
        if not is_f1 and (is_initial_call or family_changed):
            self.pllq_lineedit.setText("7")
        elif is_f1:
            self.pllq_lineedit.setText("")

        # --- Prescaler Combos ---
        ahb_map_key = f'AHB_PRESCALER_MAP_{self.current_mcu_family}'
        apb_map_key = f'APB_PRESCALER_MAP_{self.current_mcu_family}'
        ahb_map = CURRENT_MCU_DEFINES.get(ahb_map_key, CURRENT_MCU_DEFINES.get('AHB_PRESCALER_MAP', {}))
        apb_map = CURRENT_MCU_DEFINES.get(apb_map_key, CURRENT_MCU_DEFINES.get('APB_PRESCALER_MAP', {}))

        for combo, item_map in [(self.ahb_div_combo, ahb_map), (self.apb1_div_combo, apb_map),
                                (self.apb2_div_combo, apb_map)]:
            combo.blockSignals(True)
            current_text = combo.currentText()
            combo.clear()
            str_keys = [str(k) for k in item_map.keys()]
            combo.addItems(str_keys)
            if current_text in str_keys and not (is_initial_call or family_changed):
                combo.setCurrentText(current_text)
            elif combo.count() > 0:  # Default on initial/family change or if old value invalid
                combo.setCurrentIndex(0)
            combo.blockSignals(False)

        # --- Set default prescalers and SYSCLK source on initial/family change ---
        if is_initial_call or family_changed:
            self.ahb_div_combo.setCurrentText("1")
            self.apb1_div_combo.setCurrentText("2")  # Common default
            self.apb2_div_combo.setCurrentText("1")  # Common default

            self.sysclk_source_combo.blockSignals(True)
            self.sysclk_source_combo.setCurrentText("PLL")
            self.sysclk_source_combo.blockSignals(False)

            self.pll_enable_for_sysclk_checkbox.blockSignals(True)
            self.pll_enable_for_sysclk_checkbox.setChecked(True)
            self.pll_enable_for_sysclk_checkbox.blockSignals(False)

        self._update_ui_element_visibility()
        self._try_auto_calculate_pll()

        self._is_initializing = False
        if not is_initial_call:
            self.emit_config_update_slot()

    def _sync_sysclk_source_and_pll_checkbox(self):
        # ... (same as before)
        if self._is_initializing or self._is_auto_calculating_pll: return

        pll_checked = self.pll_enable_for_sysclk_checkbox.isChecked()
        sysclk_is_pll = (self.sysclk_source_combo.currentText() == "PLL")

        if pll_checked and not sysclk_is_pll:
            self.sysclk_source_combo.blockSignals(True)
            self.sysclk_source_combo.setCurrentText("PLL")
            self.sysclk_source_combo.blockSignals(False)
        elif not pll_checked and sysclk_is_pll:
            self.sysclk_source_combo.blockSignals(True)
            if self.hse_checkbox.isChecked():
                self.sysclk_source_combo.setCurrentText("HSE")
            else:
                self.sysclk_source_combo.setCurrentText("HSI")
            self.sysclk_source_combo.blockSignals(False)

    def on_critical_param_changed(self, _=None):
        # ... (same as before, calls _try_auto_calculate_pll and emit)
        if self._is_initializing or self._is_auto_calculating_pll: return
        self._update_ui_element_visibility()
        self._try_auto_calculate_pll()
        self.emit_config_update_slot()

    def on_pll_enable_changed(self, _=None):
        # ... (same as before)
        if self._is_initializing or self._is_auto_calculating_pll: return
        self._sync_sysclk_source_and_pll_checkbox()
        self._update_ui_element_visibility()
        self._try_auto_calculate_pll()
        self.emit_config_update_slot()

    def on_sysclk_source_changed(self, source_text):
        # ... (same as before)
        if self._is_initializing or self._is_auto_calculating_pll: return

        is_pll_source = (source_text == "PLL")
        if self.pll_enable_for_sysclk_checkbox.isChecked() != is_pll_source:
            self.pll_enable_for_sysclk_checkbox.blockSignals(True)
            self.pll_enable_for_sysclk_checkbox.setChecked(is_pll_source)
            self.pll_enable_for_sysclk_checkbox.blockSignals(False)

        self._update_ui_element_visibility()
        if is_pll_source:
            self._try_auto_calculate_pll()
        self.emit_config_update_slot()

    def _update_ui_element_visibility(self):
        # ... (same as before, but consider F1 target_sysclk_lineedit readOnly state)
        if self._is_initializing: return
        hse_on = self.hse_checkbox.isChecked()
        self.label_hse_value.setVisible(hse_on)
        self.hse_value_lineedit.setVisible(hse_on)
        self.hse_bypass_checkbox.setVisible(hse_on)

        use_pll_for_sysclk_ui = self.pll_enable_for_sysclk_checkbox.isChecked()
        is_f1 = (self.current_mcu_family == "STM32F1")

        self.label_target_sysclk.setVisible(use_pll_for_sysclk_ui)
        self.target_sysclk_lineedit.setVisible(use_pll_for_sysclk_ui)
        self.target_sysclk_lineedit.setReadOnly(is_f1)  # F1 target is for reference

        self.auto_calc_status_label.setVisible(use_pll_for_sysclk_ui)
        self.label_pll_source.setVisible(use_pll_for_sysclk_ui)
        self.pll_source_combo.setVisible(use_pll_for_sysclk_ui)

        self.label_pllm_or_xtpre.setVisible(use_pll_for_sysclk_ui)
        self.pllm_or_xtpre_lineedit.setVisible(use_pll_for_sysclk_ui)
        self.pllm_or_xtpre_lineedit.setReadOnly(not is_f1)

        self.label_plln_or_mul.setVisible(use_pll_for_sysclk_ui)
        self.plln_or_mul_lineedit.setVisible(use_pll_for_sysclk_ui)
        self.plln_or_mul_lineedit.setReadOnly(not is_f1)

        self.label_pllp.setVisible(use_pll_for_sysclk_ui and not is_f1)
        self.pllp_lineedit.setVisible(use_pll_for_sysclk_ui and not is_f1)
        self.label_pllq.setVisible(use_pll_for_sysclk_ui and not is_f1)
        self.pllq_lineedit.setVisible(use_pll_for_sysclk_ui and not is_f1)
        self.pllq_lineedit.setReadOnly(is_f1)  # User input for F2/F4

    def _try_auto_calculate_pll(self):
        # ... (same as before, but _calculate_f1_pll will use user inputs from lineedits)
        if self._is_initializing or self._is_auto_calculating_pll: return
        self._is_auto_calculating_pll = True

        try:
            if not self.pll_enable_for_sysclk_checkbox.isChecked():
                self.pllp_lineedit.setText("")  # Clear F2/F4 calculated P
                # For F1, M and N are user inputs, don't clear them if PLL is disabled,
                # but status should reflect PLL is off.
                self.auto_calc_status_label.setText("PLL for SYSCLK is disabled.")
                self.auto_calc_status_label.setStyleSheet("color: black;")
                self._is_auto_calculating_pll = False
                return

            # Target SYSCLK is primarily for F2/F4 auto-calculation
            # For F1, it's more of a reference, as user provides factors
            target_sysclk_for_calc = 0
            try:
                target_sysclk_for_calc = int(self.target_sysclk_lineedit.text())
            except ValueError:
                if self.current_mcu_family != "STM32F1":  # Only critical for F2/F4 auto-calc
                    self.auto_calc_status_label.setText("Invalid Target SYSCLK value for PLL calculation.");
                    self.auto_calc_status_label.setStyleSheet("color: red;")
                    self._is_auto_calculating_pll = False
                    return
                # For F1, proceed even if target_sysclk_lineedit is invalid, as factors are manual

            pll_input_freq = 0
            pll_source_type = self.pll_source_combo.currentText()
            hsi_val = CURRENT_MCU_DEFINES.get('HSI_VALUE_HZ', 8000000)
            hse_val_str = self.hse_value_lineedit.text()
            hse_val = int(hse_val_str) if hse_val_str.isdigit() else CURRENT_MCU_DEFINES.get('HSE_DEFAULT_HZ', 8000000)

            if pll_source_type == "HSI":
                if not self.hsi_checkbox.isChecked(): self.auto_calc_status_label.setText(
                    "HSI (PLL src) disabled."); self._is_auto_calculating_pll = False; return
                pll_input_freq = hsi_val
            elif pll_source_type == "HSI/2" and self.current_mcu_family == "STM32F1":
                if not self.hsi_checkbox.isChecked(): self.auto_calc_status_label.setText(
                    "HSI (PLL src) disabled."); self._is_auto_calculating_pll = False; return
                pll_input_freq = hsi_val / 2.0
            elif pll_source_type == "HSE":
                if not self.hse_checkbox.isChecked(): self.auto_calc_status_label.setText(
                    "HSE (PLL src) disabled."); self._is_auto_calculating_pll = False; return
                pll_input_freq = float(hse_val)
            else:
                self.auto_calc_status_label.setText(f"Unknown PLL source: {pll_source_type}");
                self._is_auto_calculating_pll = False;
                return

            if pll_input_freq <= 0: self.auto_calc_status_label.setText(
                "PLL input freq invalid or zero."); self._is_auto_calculating_pll = False; return

            if self.current_mcu_family == "STM32F1":
                self._calculate_f1_pll(pll_input_freq, target_sysclk_for_calc)  # target is for reference/check
            elif self.current_mcu_family in ["STM32F2", "STM32F4"]:
                if target_sysclk_for_calc <= 0:  # Must have valid target for F2/F4
                    self.auto_calc_status_label.setText("Target SYSCLK for PLL calc must be > 0.");
                    self.auto_calc_status_label.setStyleSheet("color: red;");
                else:
                    self._calculate_f2_f4_pll(pll_input_freq, target_sysclk_for_calc)
            else:
                self.auto_calc_status_label.setText(f"PLL Calc not impl for {self.current_mcu_family}")
        finally:
            self._is_auto_calculating_pll = False

    def _calculate_f1_pll(self, pll_input_freq, target_sysclk_reference):
        # For F1, user provides PLLXTPRE and PLLMUL. This function verifies them.
        try:
            xtpre_str = self.pllm_or_xtpre_lineedit.text()
            mul_str = self.plln_or_mul_lineedit.text()

            if not xtpre_str.isdigit() or not mul_str.isdigit():
                self.auto_calc_status_label.setText("PLLXTPRE/PLLMUL must be numbers.");
                self.auto_calc_status_label.setStyleSheet("color: red;")
                return

            xtpre_val = int(xtpre_str)
            mul_val = int(mul_str)

            valid_xtpre_options = CURRENT_MCU_DEFINES.get('PLLXTPRE_VALUES', [1, 2])
            min_mul = CURRENT_MCU_DEFINES.get('PLLMUL_MIN', 2)
            max_mul = CURRENT_MCU_DEFINES.get('PLLMUL_MAX', 16)

            if xtpre_val not in valid_xtpre_options:
                self.auto_calc_status_label.setText(f"Invalid PLLXTPRE ({xtpre_val}). Use {valid_xtpre_options}.");
                self.auto_calc_status_label.setStyleSheet("color: red;")
                return
            if not (min_mul <= mul_val <= max_mul):
                self.auto_calc_status_label.setText(f"Invalid PLLMUL ({mul_val}). Use {min_mul}-{max_mul}.");
                self.auto_calc_status_label.setStyleSheet("color: red;")
                return

            effective_pll_in = pll_input_freq
            if self.pll_source_combo.currentText() == "HSE":  # PLLXTPRE applies only to HSE source for PLL
                if xtpre_val == 0:  # Should not happen due to check above
                    self.auto_calc_status_label.setText(f"PLLXTPRE cannot be 0 for HSE source.");
                    return
                effective_pll_in = pll_input_freq / xtpre_val

            actual_sysclk = effective_pll_in * mul_val

            device_info = CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {}).get(self.current_target_device, {})
            # max_sysclk_for_device is the true limit for the selected F1 device
            max_sysclk_for_device = device_info.get("max_sysclk_hz",
                                                    CURRENT_MCU_DEFINES.get('SYSCLK_MAX_HZ_F103', 72000000))

            if actual_sysclk > max_sysclk_for_device:
                self.auto_calc_status_label.setText(
                    f"F1 SYSCLK ({actual_sysclk / 1e6:.1f}MHz) > Max ({max_sysclk_for_device / 1e6:.1f}MHz for {self.current_target_device}).")
                self.auto_calc_status_label.setStyleSheet("color: red;")
            # For F1, target_sysclk_reference is just for user's info, not strict matching
            elif target_sysclk_reference > 0 and abs(
                    actual_sysclk - target_sysclk_reference) > 1000000:  # 1MHz tolerance for reference
                self.auto_calc_status_label.setText(
                    f"F1 SYSCLK: {actual_sysclk / 1e6:.1f}MHz. (Ref Target: {target_sysclk_reference / 1e6:.1f}MHz).")
                self.auto_calc_status_label.setStyleSheet("color: orange;")  # Warning if far from reference target
            else:
                self.auto_calc_status_label.setText(f"F1 Calculated SYSCLK: {actual_sysclk / 1e6:.1f} MHz.")
                self.auto_calc_status_label.setStyleSheet("color: green;")
        except Exception as e:  # Catch any other conversion errors
            self.auto_calc_status_label.setText(f"Error in F1 PLL params: {e}")
            self.auto_calc_status_label.setStyleSheet("color: red;")

    def _calculate_f2_f4_pll(self, pll_input_freq, target_sysclk):
        # ... (This part should be mostly okay, as it attempts to find M,N,P)
        # Ensure it uses the correct VCO_OUT ranges for F2 vs F4 from defines
        best_solution = None;
        smallest_diff = float('inf')

        pllm_min = CURRENT_MCU_DEFINES.get('PLLM_MIN', 2)
        pllm_max = CURRENT_MCU_DEFINES.get('PLLM_MAX', 63)
        pllp_values = CURRENT_MCU_DEFINES.get('PLLP_VALUES', [2, 4, 6, 8])
        vco_in_min = CURRENT_MCU_DEFINES.get('VCO_INPUT_MIN_HZ', 1e6)
        vco_in_max = CURRENT_MCU_DEFINES.get('VCO_INPUT_MAX_HZ', 2e6)

        vco_out_min_key = f'VCO_OUTPUT_MIN_HZ_{self.current_mcu_family}'  # e.g. VCO_OUTPUT_MIN_HZ_F2
        vco_out_max_key = f'VCO_OUTPUT_MAX_HZ_{self.current_mcu_family}'  # e.g. VCO_OUTPUT_MAX_HZ_F2

        vco_out_min = CURRENT_MCU_DEFINES.get(vco_out_min_key, CURRENT_MCU_DEFINES.get('VCO_OUTPUT_MIN_HZ', 192e6))
        vco_out_max = CURRENT_MCU_DEFINES.get(vco_out_max_key, CURRENT_MCU_DEFINES.get('VCO_OUTPUT_MAX_HZ', 432e6))

        get_plln_range_func = CURRENT_MCU_DEFINES.get('get_plln_range')

        plln_min_default_key = f'PLLN_MIN_{self.current_mcu_family}'  # e.g. PLLN_MIN_F2
        plln_max_default_key = f'PLLN_MAX_{self.current_mcu_family}'  # e.g. PLLN_MAX_F2

        plln_min_default = CURRENT_MCU_DEFINES.get(plln_min_default_key,
                                                   CURRENT_MCU_DEFINES.get('PLLN_MIN_GENERAL', 192))
        plln_max_default = CURRENT_MCU_DEFINES.get(plln_max_default_key,
                                                   CURRENT_MCU_DEFINES.get('PLLN_MAX_GENERAL', 432))

        min_plln, max_plln = (plln_min_default, plln_max_default)
        if get_plln_range_func and self.current_mcu_family == "STM32F4":
            min_plln, max_plln = get_plln_range_func(self.current_target_device)

        for pllm_candidate in range(pllm_min, pllm_max + 1):
            if pllm_candidate == 0: continue
            vco_in_candidate = pll_input_freq / pllm_candidate
            if not (vco_in_min <= vco_in_candidate <= vco_in_max): continue

            for pllp_candidate in pllp_values:
                plln_float = (target_sysclk * pllp_candidate) / vco_in_candidate
                for plln_offset in range(-2, 3):
                    plln_candidate_rounded = round(plln_float) + plln_offset
                    if not (min_plln <= plln_candidate_rounded <= max_plln): continue

                    vco_out_candidate = vco_in_candidate * plln_candidate_rounded
                    if not (vco_out_min <= vco_out_candidate <= vco_out_max): continue

                    actual_sysclk = vco_out_candidate / pllp_candidate
                    diff = abs(actual_sysclk - target_sysclk)

                    current_max_sysclk_for_device = CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {}).get(
                        self.current_target_device, {}).get('max_sysclk_hz',
                                                            SYSCLK_MAX_HZ_F2 if self.current_mcu_family == "STM32F2" else CURRENT_MCU_DEFINES.get(
                                                                'SYSCLK_MAX_HZ_MAP', {}).get(self.current_target_device,
                                                                                             {}).get("VOS1_od",
                                                                                                     168000000))  # complex fallback
                    if actual_sysclk > current_max_sysclk_for_device + 1000:  # Allow small overshoot due to rounding
                        continue

                    if diff < smallest_diff:
                        smallest_diff = diff
                        best_solution = (pllm_candidate, int(plln_candidate_rounded), pllp_candidate, actual_sysclk)
                    if diff == 0 and actual_sysclk <= current_max_sysclk_for_device: break
                if best_solution and smallest_diff == 0 and best_solution[3] <= current_max_sysclk_for_device: break
            if best_solution and smallest_diff == 0 and best_solution[3] <= current_max_sysclk_for_device: break

        if best_solution:
            m, n, p, actual_f = best_solution
            self.pllm_or_xtpre_lineedit.setText(str(m))
            self.plln_or_mul_lineedit.setText(str(n))
            self.pllp_lineedit.setText(str(p))
            self.auto_calc_status_label.setText(
                f"Calc: ~{actual_f / 1e6:.2f}MHz (Target: {target_sysclk / 1e6:.1f}MHz)")
            self.auto_calc_status_label.setStyleSheet("color: green;")
        else:
            self.pllm_or_xtpre_lineedit.setText("N/A");
            self.plln_or_mul_lineedit.setText("N/A");
            self.pllp_lineedit.setText("N/A")
            self.auto_calc_status_label.setText(f"Could not find PLL params for {target_sysclk / 1e6:.1f} MHz.")
            self.auto_calc_status_label.setStyleSheet("color: red;")

    def _calculate_clocks_and_settings(self, params_in):
        # ... (this function needs to use the user-provided F1 factors if family is F1)
        # ... or the calculated F2/F4 factors ...
        params = params_in.copy()
        calculated = {"errors": [], "warnings": []}
        mcu_family = params.get("mcu_family", self.current_mcu_family)

        target_devices_map = CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {})
        device_info = target_devices_map.get(params.get("target_device", self.current_target_device), {})
        max_sysclk_for_device = device_info.get("max_sysclk_hz", 0)

        hsi_val = CURRENT_MCU_DEFINES.get('HSI_VALUE_HZ', 16000000)
        if mcu_family == "STM32F1":
            hsi_val = CURRENT_MCU_DEFINES.get('HSI_VALUE_HZ', 8000000)  # F1 uses 8MHz HSI usually

        sysclk_freq_hz = float(hsi_val)  # Default to HSI

        sysclk_source = params.get("sysclk_source", "HSI")

        if sysclk_source == "PLL":
            if not params.get("pll_enabled_for_sysclk"):
                calculated["warnings"].append("PLL SYSCLK selected, but 'Use PLL' is off. Using HSI.")
                sysclk_source = "HSI";
                params["sysclk_source"] = "HSI"  # Fallback
            else:
                pll_source_type = params.get("pll_source", "HSI")
                pll_input_freq = 0.0
                hse_val_param = float(params.get("hse_value_hz", CURRENT_MCU_DEFINES.get('HSE_DEFAULT_HZ', 8000000)))

                if pll_source_type == "HSI":
                    if not params.get("hsi_enabled"): calculated["errors"].append("HSI (PLL src) disabled.")
                    pll_input_freq = float(hsi_val)
                elif pll_source_type == "HSI/2" and mcu_family == "STM32F1":
                    if not params.get("hsi_enabled"): calculated["errors"].append("HSI (PLL src) disabled.")
                    pll_input_freq = float(hsi_val) / 2.0
                elif pll_source_type == "HSE":
                    if not params.get("hse_enabled"): calculated["errors"].append("HSE (PLL src) disabled.")
                    pll_input_freq = hse_val_param

                if pll_input_freq <= 0 and not calculated["errors"]:
                    calculated["errors"].append("PLL Input Freq is zero or negative.")

                if not calculated["errors"]:  # Proceed only if input freq is valid
                    if mcu_family == "STM32F1":
                        pllxtpre = params.get("pllm_or_xtpre", 1)  # User input
                        pllmul = params.get("plln_or_mul", 9)  # User input
                        if pllxtpre == 0: calculated["errors"].append("PLLXTPRE cannot be 0 for F1.")

                        effective_pll_in_f1 = pll_input_freq
                        if pll_source_type == "HSE" and pllxtpre > 0:
                            effective_pll_in_f1 = pll_input_freq / pllxtpre

                        sysclk_freq_hz = effective_pll_in_f1 * pllmul
                        if sysclk_freq_hz > max_sysclk_for_device:
                            calculated["errors"].append(
                                f"F1 SYSCLK ({sysclk_freq_hz / 1e6:.1f}MHz) exceeds max ({max_sysclk_for_device / 1e6:.1f}MHz).")

                        params["pll_p_output_freq_hz"] = sysclk_freq_hz
                        params["vco_output_freq_hz"] = sysclk_freq_hz
                        params["vco_input_freq_hz"] = effective_pll_in_f1

                    elif mcu_family in ["STM32F2", "STM32F4"]:
                        # For F2/F4, M, N, P are taken from the calculated/displayed values
                        # which _try_auto_calculate_pll should have set in the lineedits
                        # So, we read them back from params (which should reflect the lineedits)
                        pllm = params.get("pllm_or_xtpre", 0)
                        plln = params.get("plln_or_mul", 0)
                        pllp = params.get("pllp", 0)

                        if not all(isinstance(val, int) and val > 0 for val in [pllm, plln, pllp]):
                            calculated["errors"].append(
                                f"{mcu_family} PLLM,N,P invalid (likely not calculated). Using HSI.")
                            sysclk_source = "HSI";
                            params["sysclk_source"] = "HSI"
                        else:
                            vco_in = pll_input_freq / pllm
                            vco_out = vco_in * plln
                            sysclk_freq_hz = vco_out / pllp
                            if sysclk_freq_hz > max_sysclk_for_device:
                                calculated["errors"].append(
                                    f"{mcu_family} SYSCLK ({sysclk_freq_hz / 1e6:.1f}MHz) exceeds max ({max_sysclk_for_device / 1e6:.1f}MHz).")

                            params["vco_input_freq_hz"] = vco_in
                            params["vco_output_freq_hz"] = vco_out
                            params["pll_p_output_freq_hz"] = sysclk_freq_hz
                            pllq_val = params.get("pllq", 0)
                            if pllq_val > 0:
                                params["pll_q_output_freq_hz"] = vco_out / pllq_val

        # If errors occurred during PLL, fall back to HSI
        if calculated["errors"] and sysclk_source == "PLL":
            sysclk_source = "HSI";
            params["sysclk_source"] = "HSI"
            sysclk_freq_hz = float(hsi_val)
            calculated["warnings"].append("Reverted to HSI due to PLL configuration errors.")

        if sysclk_source == "HSE":
            if not params.get("hse_enabled"):
                calculated["errors"].append("HSE SYSCLK selected, but disabled. Using HSI.")
                sysclk_freq_hz = float(hsi_val);
                params["sysclk_source"] = "HSI"
            else:
                sysclk_freq_hz = float(params.get("hse_value_hz", CURRENT_MCU_DEFINES.get('HSE_DEFAULT_HZ', 8000000)))

        if sysclk_source == "HSI":  # Explicit HSI or fallback
            if not params.get("hsi_enabled"): calculated["warnings"].append(
                "HSI SYSCLK selected, but HSI not enabled by user.")
            sysclk_freq_hz = float(hsi_val)

        # Ensure sysclk_freq_hz does not exceed absolute max for device if something went wrong
        if sysclk_freq_hz > max_sysclk_for_device and max_sysclk_for_device > 0:
            if not any("SYSCLK" in err for err in calculated["errors"]):  # Add error if not already present
                calculated["errors"].append(
                    f"Final SYSCLK ({sysclk_freq_hz / 1e6:.1f}MHz) capped to max ({max_sysclk_for_device / 1e6:.1f}MHz).")
            sysclk_freq_hz = float(max_sysclk_for_device)

        ahb_div = params.get("ahb_div", 1);
        hclk_freq_hz = sysclk_freq_hz / ahb_div
        apb1_div = params.get("apb1_div", 1);
        pclk1_freq_hz = hclk_freq_hz / apb1_div
        apb2_div = params.get("apb2_div", 1);
        pclk2_freq_hz = hclk_freq_hz / apb2_div

        # Max clock checks (using device_info for specific limits)
        max_hclk_dev = device_info.get("max_hclk_hz", max_sysclk_for_device)  # HCLK often same as SYSCLK max
        max_pclk1_dev = device_info.get("max_pclk1_hz", 36000000)
        max_pclk2_dev = device_info.get("max_pclk2_hz", 72000000)

        vos_scale_id = "N/A";
        vos_pwr_cr_val = None;
        overdrive_active = False  # F4 specific

        if mcu_family == "STM32F4":
            get_required_vos_func = CURRENT_MCU_DEFINES.get('get_required_vos')
            if get_required_vos_func:
                vos_max_hclk_dev = device_info.get("vos_max_hclk", {})
                non_od_max_vos1 = vos_max_hclk_dev.get("VOS_SCALE_1", 0)
                od_intended = device_info.get("has_overdrive") and hclk_freq_hz > non_od_max_vos1

                vos_scale_id, vos_pwr_cr_val = get_required_vos_func(hclk_freq_hz, params.get("target_device"),
                                                                     od_intended)
                overdrive_active = (vos_scale_id == "VOS_SCALE_1_OD")

                # Update max peripheral clocks based on VOS for F4
                vos_lookup_key = vos_scale_id.replace("_OD", "")  # Use base VOS scale for map lookup
                max_hclk_dev = vos_max_hclk_dev.get(vos_lookup_key, max_hclk_dev)
                if overdrive_active: max_hclk_dev = device_info.get("max_sysclk_vos1_od", max_hclk_dev)

                max_pclk1_dev = CURRENT_MCU_DEFINES.get('PCLK1_MAX_HZ_MAP', {}).get(params.get("target_device"),
                                                                                    {}).get(vos_lookup_key,
                                                                                            max_pclk1_dev)
                max_pclk2_dev = CURRENT_MCU_DEFINES.get('PCLK2_MAX_HZ_MAP', {}).get(params.get("target_device"),
                                                                                    {}).get(vos_lookup_key,
                                                                                            max_pclk2_dev)

        if hclk_freq_hz > max_hclk_dev: calculated["errors"].append(
            f"HCLK ({hclk_freq_hz / 1e6:.1f}MHz) > max ({max_hclk_dev / 1e6:.1f}MHz).")
        if pclk1_freq_hz > max_pclk1_dev: calculated["errors"].append(
            f"PCLK1 ({pclk1_freq_hz / 1e6:.1f}MHz) > max ({max_pclk1_dev / 1e6:.1f}MHz).")
        if pclk2_freq_hz > max_pclk2_dev: calculated["errors"].append(
            f"PCLK2 ({pclk2_freq_hz / 1e6:.1f}MHz) > max ({max_pclk2_dev / 1e6:.1f}MHz).")

        flash_latency_val = 0
        get_flash_latency_func_name = f"get_{mcu_family.lower()}_flash_latency"
        get_flash_latency_func = CURRENT_MCU_DEFINES.get(get_flash_latency_func_name)
        if get_flash_latency_func:
            if mcu_family == "STM32F4":
                flash_latency_val = get_flash_latency_func(hclk_freq_hz, params.get("target_device"), vos_scale_id)
            else:
                flash_latency_val = get_flash_latency_func(hclk_freq_hz, params.get("target_device"))
        else:
            # Generic fallback if specific function is missing (less ideal)
            flash_latency_val = CURRENT_MCU_DEFINES.get('get_flash_latency', lambda f, d, v=None: 0)(hclk_freq_hz,
                                                                                                     params.get(
                                                                                                         "target_device"),
                                                                                                     vos_scale_id if mcu_family == "STM32F4" else None)

        calculated.update({
            "sysclk_freq_hz": int(sysclk_freq_hz), "hclk_freq_hz": int(hclk_freq_hz),
            "pclk1_freq_hz": int(pclk1_freq_hz), "pclk2_freq_hz": int(pclk2_freq_hz),
            "vco_input_freq_hz": int(params.get("vco_input_freq_hz", 0)),
            "vco_output_freq_hz": int(params.get("vco_output_freq_hz", 0)),
            "pll_p_output_freq_hz": int(params.get("pll_p_output_freq_hz", 0)),
            "pll_q_output_freq_hz": int(params.get("pll_q_output_freq_hz", 0)),
            "flash_latency_val": flash_latency_val,
            "vos_scale_id": vos_scale_id, "vos_scale_pwr_cr_val": vos_pwr_cr_val,
            "overdrive_active": overdrive_active,
            "ahb_div": ahb_div, "apb1_div": apb1_div, "apb2_div": apb2_div
        })
        return calculated

    def get_config(self):
        # ... (same as before) ...
        mcu_fam = self.current_mcu_family
        mcu_dev = self.current_target_device

        params = {
            "target_device": mcu_dev, "mcu_family": mcu_fam,
            "hsi_enabled": self.hsi_checkbox.isChecked(),
            "hse_enabled": self.hse_checkbox.isChecked(),
            "hse_value_hz": int(
                self.hse_value_lineedit.text()) if self.hse_value_lineedit.text().isdigit() else CURRENT_MCU_DEFINES.get(
                'HSE_DEFAULT_HZ', 8000000),
            "hse_bypass": self.hse_bypass_checkbox.isChecked(),
            "pll_enabled_for_sysclk": self.pll_enable_for_sysclk_checkbox.isChecked(),
            "pll_source": self.pll_source_combo.currentText(),
            "pllm_or_xtpre": int(
                self.pllm_or_xtpre_lineedit.text()) if self.pllm_or_xtpre_lineedit.text().strip().lstrip(
                '-').isdigit() else 0,
            "plln_or_mul": int(self.plln_or_mul_lineedit.text()) if self.plln_or_mul_lineedit.text().strip().lstrip(
                '-').isdigit() else 0,
            "pllp": int(self.pllp_lineedit.text()) if self.pllp_lineedit.text().strip().lstrip('-').isdigit() else 0,
            "pllq": int(self.pllq_lineedit.text()) if self.pllq_lineedit.text().strip().lstrip('-').isdigit() else (
                7 if mcu_fam != "STM32F1" else 0),
            "sysclk_source": self.sysclk_source_combo.currentText(),
            "ahb_div": int(self.ahb_div_combo.currentText()) if self.ahb_div_combo.currentText().isdigit() else 1,
            "apb1_div": int(self.apb1_div_combo.currentText()) if self.apb1_div_combo.currentText().isdigit() else 1,
            "apb2_div": int(self.apb2_div_combo.currentText()) if self.apb2_div_combo.currentText().isdigit() else 1,
        }
        params["pll_enabled"] = params["pll_enabled_for_sysclk"]
        calculated_data = self._calculate_clocks_and_settings(params)
        return {"params": params, "calculated": calculated_data}

    def emit_config_update_slot(self, _=None):
        # ... (same as before) ...
        if self._is_initializing or self._is_auto_calculating_pll: return
        self.config_updated.emit(self.get_config())