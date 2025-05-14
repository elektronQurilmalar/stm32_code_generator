# --- MODIFIED FILE main_window.py ---

import traceback

from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter
from PyQt5.QtCore import Qt

from widgets.selection_pane import SelectionPane
from widgets.configuration_pane import ConfigurationPane
from widgets.code_pane import CodePane

from core.mcu_defines_loader import set_current_mcu_defines, CURRENT_MCU_DEFINES

from generators.rcc_generator import generate_rcc_code_cmsis
from generators.gpio_generator import generate_gpio_code
from generators.adc_generator import generate_adc_code_cmsis
from generators.dac_generator import generate_dac_code_cmsis
from generators.uart_generator import generate_uart_code_cmsis
from generators.timer_generator import generate_timer_code_cmsis
from generators.i2c_generator import generate_i2c_code_cmsis
from generators.spi_generator import generate_spi_code_cmsis
from generators.dma_generator import generate_dma_code_cmsis
from generators.delay_generator import generate_delay_code_cmsis


class MainWindow(QMainWindow):
    LOGICAL_MODULE_ORDER = [
        "MCU", "RCC", "GPIO", "DMA", "ADC", "DAC", "TIMERS",
        "I2C", "SPI", "USART", "Delay"
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("STM32 CMSIS Code Generator")
        self.setGeometry(100, 100, 1400, 850)
        self._is_regenerating_code = False
        self.current_target_mcu = "STM32F407VG"
        self.current_mcu_family = "STM32F4"

        if not set_current_mcu_defines(self.current_mcu_family):
            print(
                f"FATAL: Could not load defines for initial MCU family {self.current_mcu_family}. Application may not work correctly.")
        self.setWindowTitle(f"STM32 CMSIS Code Generator ({self.current_mcu_family} - {self.current_target_mcu})")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        self.selection_pane = SelectionPane()
        self.configuration_pane = ConfigurationPane(self.current_target_mcu, self.current_mcu_family)
        self.code_pane = CodePane()

        config_code_splitter = QSplitter(Qt.Horizontal)
        config_code_splitter.addWidget(self.configuration_pane)
        config_code_splitter.addWidget(self.code_pane)
        config_code_splitter.setStretchFactor(0, 2)
        config_code_splitter.setStretchFactor(1, 3)

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(self.selection_pane)
        main_splitter.addWidget(config_code_splitter)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 4)
        main_splitter.setSizes([250, 1150])
        self.layout.addWidget(main_splitter)

        self.selection_pane.module_selected.connect(self.on_module_selected)
        self.configuration_pane.config_changed.connect(self.on_config_changed)
        self.configuration_pane.mcu_target_device_globally_changed.connect(self.on_global_mcu_target_changed)

        self.current_config_data = self.configuration_pane.get_all_configurations()  # Get initial full config

        if self.selection_pane.module_list.count() > 0:
            self.selection_pane.module_list.setCurrentRow(0)  # Triggers on_module_selected
            # on_module_selected will handle getting initial config for "MCU" if not already present
            # and trigger initial code generation.

    def get_fixed_processing_order(self):
        available_modules_in_gui = [self.selection_pane.module_list.item(i).text() for i in
                                    range(self.selection_pane.module_list.count())]
        ordered_for_processing = [m for m in self.LOGICAL_MODULE_ORDER if m in available_modules_in_gui]
        for m in available_modules_in_gui:
            if m not in ordered_for_processing:
                ordered_for_processing.append(m)
        return ordered_for_processing

    def on_module_selected(self, module_name):
        # print(f"MainWindow: Module selected: {module_name}")
        self.configuration_pane.display_module_config(module_name)
        # Ensure config data for newly selected module is loaded if not already.
        # display_module_config might update widget, so get_module_config_data afterwards.
        if module_name not in self.current_config_data or not self.current_config_data[module_name]:
            # print(f"MainWindow: Config for {module_name} not found or empty, fetching from widget.")
            config_data = self.configuration_pane.get_module_config_data(module_name)
            if config_data is not None:
                self.current_config_data[module_name] = config_data  # Store it
                # Don't regenerate here, let on_config_changed handle it if it was a real change
            else:
                self.current_config_data[module_name] = {}  # Store empty if widget returned None

        # Selecting a module doesn't inherently change config, so only regen if data was newly fetched and non-empty
        # Or, if the config pane itself emits a change upon displaying (e.g. if its update_for_target_device changes defaults)
        # For now, let on_config_changed manage regeneration.
        # If just switching view, don't regenerate unless a config change signal is emitted by the widget after display.

    def on_global_mcu_target_changed(self, new_mcu_device, new_mcu_family):
        # print(f"MainWindow: Global MCU target changed to Device: {new_mcu_device}, Family: {new_mcu_family}")
        if self.current_target_mcu == new_mcu_device and self.current_mcu_family == new_mcu_family:
            # print("MainWindow: Global MCU target changed, but no actual change in device/family. Skipping.")
            return  # No actual change

        self._is_regenerating_code = True  # Prevent re-entry during this complex update

        self.current_target_mcu = new_mcu_device
        self.current_mcu_family = new_mcu_family
        self.setWindowTitle(f"STM32 CMSIS Code Generator ({new_mcu_family} - {new_mcu_device})")

        # Defines are already set by ConfigurationPane's on_mcu_widget_config_updated
        # before it emits mcu_target_device_globally_changed.

        # ConfigurationPane needs to update all its children for the new MCU.
        # This must happen *before* we try to get all configurations.
        # print("MainWindow: Calling configuration_pane.update_all_sub_widgets_for_mcu")
        self.configuration_pane.update_all_sub_widgets_for_mcu(new_mcu_device, new_mcu_family)

        # After sub-widgets are updated, fetch their (potentially new default) configurations.
        # print("MainWindow: Fetching all configurations after global MCU change.")
        self.current_config_data = self.configuration_pane.get_all_configurations()

        self._is_regenerating_code = False
        # print("MainWindow: Triggering regenerate_all_code after global MCU change processing.")
        self.regenerate_all_code()

    def on_config_changed(self, module_name, config_data):
        # print(f"MainWindow: Config changed for module: {module_name}")
        if self._is_regenerating_code:
            # print("MainWindow: Bailing on_config_changed: _is_regenerating_code is True")
            return

        # Update the stored config for the specific module
        self.current_config_data[module_name] = config_data

        # If MCU config changed, it's handled by on_global_mcu_target_changed for broader updates.
        # This slot handles other module changes.
        # print(f"MainWindow: Triggering regenerate_all_code from on_config_changed for {module_name}")
        self.regenerate_all_code()

    def regenerate_all_code(self):
        # print("MainWindow: regenerate_all_code called.")
        if self._is_regenerating_code:
            # print("MainWindow: Bailing regenerate_all_code: already regenerating.")
            return
        self._is_regenerating_code = True
        # print(f"MainWindow: Starting code regeneration for {self.current_mcu_family} - {self.current_target_mcu}")

        if not set_current_mcu_defines(self.current_mcu_family):
            self.code_pane.set_code(
                f"/* ERROR: Could not load defines for MCU family {self.current_mcu_family}. Code generation aborted. */")
            self._is_regenerating_code = False
            # print("MainWindow: Code regeneration aborted due to define loading failure.")
            return

        try:
            all_includes, all_function_defs, all_init_calls, all_default_helper_functions, \
                all_error_messages, generated_code_parts, all_peripheral_rcc_clocks, \
                all_gpio_af_configs, all_gpio_analog_configs = set(), [], [], [], [], {}, [], [], []
            system_core_clock_update_needed = False
            current_processing_order = self.get_fixed_processing_order()
            rcc_calculated_data = {}

            # Ensure all configs explicitly have the current MCU and family for generators
            # This fetches the most up-to-date config, including current MCU context
            master_config_snapshot = self.configuration_pane.get_all_configurations()
            self.current_config_data = master_config_snapshot  # Update main store with this snapshot

            # print(f"MainWindow: Configs used for generation: {list(self.current_config_data.keys())}")

            if "RCC" in self.current_config_data and self.current_config_data["RCC"] and self.current_config_data[
                "RCC"].get("params"):
                rcc_config = self.current_config_data["RCC"]
                # The 'calculated' part of RCC config should be up-to-date from RCC widget's get_config
                rcc_calculated_data = rcc_config.get("calculated", {})
                if not rcc_calculated_data:  # If somehow missing, try to get it from widget directly (should not be needed)
                    rcc_widget_cfg = self.configuration_pane.get_module_config_data("RCC")
                    if rcc_widget_cfg and rcc_widget_cfg.get("calculated"):
                        rcc_calculated_data = rcc_widget_cfg.get("calculated")

                if rcc_calculated_data.get("errors"):
                    for err in rcc_calculated_data["errors"]:
                        if err not in all_error_messages: all_error_messages.append(f"RCC Calc: {err}")

                cmsis_header_from_rcc = rcc_config.get("params", {}).get(
                    "cmsis_device_header")  # This might not be how header is passed
                if not cmsis_header_from_rcc:  # Fallback
                    target_devices_map = CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {})
                    cmsis_header_from_rcc = target_devices_map.get(self.current_target_mcu, {}).get("cmsis_header",
                                                                                                    f"stm32{self.current_mcu_family.lower()}xx.h")
                if cmsis_header_from_rcc:
                    all_includes.add(f"#include \"{cmsis_header_from_rcc}\"")

            else:  # Fallback if RCC is not configured
                all_error_messages.append(
                    "WARNING: RCC module not configured or config is empty. Using default clock assumptions.")
                hsi_val = CURRENT_MCU_DEFINES.get('HSI_VALUE_HZ', 8000000)
                rcc_calculated_data = {
                    "pclk1_freq_hz": hsi_val, "pclk2_freq_hz": hsi_val,
                    "sysclk_freq_hz": hsi_val, "hclk_freq_hz": hsi_val,
                    "apb1_div": 1, "apb2_div": 1, "ahb_div": 1,
                    "target_device": self.current_target_mcu, "mcu_family": self.current_mcu_family,
                    "flash_latency_val": 0,  # Sensible default
                }
                target_devices_map = CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {})
                default_header = target_devices_map.get(self.current_target_mcu, {}).get("cmsis_header",
                                                                                         f"stm32{self.current_mcu_family.lower()}xx.h")
                all_includes.add(f"#include \"{default_header}\"")

            for module_name in current_processing_order:
                if module_name in ["MCU", "RCC"]: continue  # RCC handled separately for peripheral clocks
                if module_name in self.current_config_data and self.current_config_data[module_name]:
                    module_config = self.current_config_data[module_name]
                    if not module_config.get("params", {}).get("enabled",
                                                               False) and module_name != "GPIO":  # GPIO always "enabled" conceptually for pins
                        # print(f"MainWindow: Skipping module {module_name} as it's not enabled.")
                        continue

                    # print(f"MainWindow: Generating code for {module_name}")
                    parts = {}
                    if module_name == "GPIO":
                        parts = generate_gpio_code(module_config)
                    elif module_name == "ADC":
                        parts = generate_adc_code_cmsis(module_config)
                    elif module_name == "DAC":
                        parts = generate_dac_code_cmsis(module_config)
                    elif module_name == "TIMERS":
                        parts = generate_timer_code_cmsis(module_config, rcc_calculated_data)
                    elif module_name == "I2C":
                        parts = generate_i2c_code_cmsis(module_config, rcc_calculated_data)
                    elif module_name == "SPI":
                        parts = generate_spi_code_cmsis(module_config, rcc_calculated_data)
                    elif module_name == "USART":
                        parts = generate_uart_code_cmsis(module_config, rcc_calculated_data)
                    elif module_name == "DMA":
                        parts = generate_dma_code_cmsis(module_config)
                    elif module_name == "Delay":
                        parts = generate_delay_code_cmsis(module_config, rcc_calculated_data)

                    if parts:
                        generated_code_parts[module_name] = parts
                        if parts.get("rcc_clocks_to_enable"):
                            all_peripheral_rcc_clocks.extend(parts["rcc_clocks_to_enable"])
                        if parts.get("gpio_pins_to_configure_af"):
                            all_gpio_af_configs.extend(parts["gpio_pins_to_configure_af"])
                        if parts.get("gpio_pins_to_configure_analog"):
                            all_gpio_analog_configs.extend(parts["gpio_pins_to_configure_analog"])
                        if parts.get("default_helper_functions"):
                            helper = parts["default_helper_functions"]
                            if helper and helper.strip() and helper not in all_default_helper_functions:
                                all_default_helper_functions.append(helper)
                        if parts.get("error_messages"):
                            for err in parts["error_messages"]:
                                if err not in all_error_messages: all_error_messages.append(f"{module_name}: {err}")

            # --- Final RCC generation with collected peripheral clocks ---
            if "RCC" in self.current_config_data and self.current_config_data["RCC"] and self.current_config_data[
                "RCC"].get("params"):
                rcc_config_final = self.current_config_data["RCC"]
                unique_clocks = sorted(list(set(all_peripheral_rcc_clocks)))
                # print(f"MainWindow: Final RCC generation with clocks: {unique_clocks}")
                final_rcc_parts = generate_rcc_code_cmsis(rcc_config_final, unique_clocks)
                generated_code_parts["RCC"] = final_rcc_parts
                # Ensure CMSIS header from RCC is prioritized or added if not present
                cmsis_header_rcc = final_rcc_parts.get("cmsis_device_header")
                if cmsis_header_rcc: all_includes.add(f"#include \"{cmsis_header_rcc}\"")

                if final_rcc_parts.get("error_messages"):
                    for err in final_rcc_parts["error_messages"]:
                        if err not in all_error_messages: all_error_messages.append(f"RCC Final: {err}")
                if final_rcc_parts.get("system_core_clock_update_needed"):
                    system_core_clock_update_needed = True

            # --- Assemble the final code string ---
            temp_function_defs, temp_init_calls = [], []
            for module_name_ordered in current_processing_order:
                if module_name_ordered == "MCU": continue
                if module_name_ordered in generated_code_parts and generated_code_parts[module_name_ordered]:
                    parts_to_assemble = generated_code_parts[module_name_ordered]
                    if parts_to_assemble.get("source_function"):
                        func_code = parts_to_assemble["source_function"].strip()
                        if func_code and not func_code.startswith(
                                ("// No", f"// {module_name_ordered} not enabled")):  # Avoid empty/disabled stubs
                            if func_code not in temp_function_defs: temp_function_defs.append(func_code)
                    if parts_to_assemble.get("init_call"):
                        init_c = parts_to_assemble["init_call"].strip()
                        if init_c and init_c not in temp_init_calls: temp_init_calls.append(init_c)

            final_code_str = ""
            unique_errors_list = sorted(list(set(all_error_messages)))
            if unique_errors_list:
                final_code_str += "/*\n * !!! ERRORS/WARNINGS GENERATED !!!\n"
                for msg in unique_errors_list: final_code_str += f" * - {msg}\n"
                final_code_str += " */\n\n"

            define_mcu_name = "".join(c if c.isalnum() else '_' for c in self.current_target_mcu.upper())
            final_code_str += f"#define {define_mcu_name} 1\n"
            define_family_name = self.current_mcu_family.upper()
            final_code_str += f"#define {define_family_name.replace('STM32', 'STM32_')}_SERIES 1 // e.g. STM32_F4_SERIES\n\n"

            for inc in sorted(list(all_includes)): final_code_str += f"{inc}\n"
            if all_includes: final_code_str += "\n"

            if temp_function_defs:
                final_code_str += "// Peripheral Initialization Functions\n"
                for func_def in temp_function_defs: final_code_str += func_def + "\n\n"
            if all_default_helper_functions:
                final_code_str += "// Default Helper Functions\n"
                for helper in all_default_helper_functions: final_code_str += helper + "\n\n"

            if all_gpio_af_configs:
                unique_af = sorted(list(set(all_gpio_af_configs)),
                                   key=lambda x: (x[0], int(x[1]) if x[1].isdigit() else -1, x[2]))
                final_code_str += "/* NOTE: Configure GPIO pins for Alternate Function (AF) in GPIO_User_Init():\n"
                for p_char, pin_n, af_val, fn_name in unique_af:
                    # F1 remap might not use AF number directly
                    af_str = f"AF{af_val}" if af_val != -1 else "Remap"
                    final_code_str += f" *       - P{p_char}{pin_n}: {af_str} ({fn_name})\n"
                final_code_str += " */\n\n"

            if all_gpio_analog_configs:
                unique_ana = {}
                for item in all_gpio_analog_configs:
                    key = (item['port_char'], item['pin_num'])
                    if key not in unique_ana:
                        unique_ana[key] = item['module']
                    elif item['module'] not in unique_ana[key]:
                        unique_ana[key] += f", {item['module']}"

                final_code_str += "/* NOTE: Configure GPIO pins for Analog mode in GPIO_User_Init():\n"
                for (p_c, p_n), m_names in sorted(unique_ana.items(), key=lambda x_sort: (x_sort[0][0], x_sort[0][1])):
                    final_code_str += f" *       - P{p_c}{p_n} (for {m_names})\n"
                final_code_str += " */\n\n"

            final_code_str += "int main(void) {\n    // SystemInit() may be called here by startup code or before main.\n\n"
            ordered_init_calls_final = []
            if "RCC_User_Init()" in temp_init_calls: ordered_init_calls_final.append("RCC_User_Init()")
            if "GPIO_User_Init()" in temp_init_calls: ordered_init_calls_final.append("GPIO_User_Init()")
            other_c = [call for call in temp_init_calls if call not in ordered_init_calls_final]
            ordered_init_calls_final.extend(other_c)

            for call_main in ordered_init_calls_final:
                if call_main: final_code_str += f"    {call_main};\n"

            if system_core_clock_update_needed:
                final_code_str += "\n    SystemCoreClockUpdate();\n"

            final_code_str += "\n    // SysTick_Config(SystemCoreClock / 1000); // For 1ms tick\n"
            final_code_str += "\n    while(1) {\n        // Application loop\n    }\n    return 0;\n}\n\n"

            # Use calculated HCLK for default SystemCoreClock if RCC wasn't configured
            scc_val = rcc_calculated_data.get("hclk_freq_hz", CURRENT_MCU_DEFINES.get('HSI_VALUE_HZ', 8000000))
            final_code_str += f"#ifndef SystemCoreClock\nvolatile uint32_t SystemCoreClock = {int(scc_val)}UL;\n#endif\n\n"
            final_code_str += "#ifndef SystemCoreClockUpdate\nvoid SystemCoreClockUpdate(void) { /* Implement if needed, e.g. read SystemCoreClock after RCC setup */ }\n#endif\n"

            self.code_pane.set_code(final_code_str)
            # print("MainWindow: Code regeneration finished.")
        except Exception as e:
            self.code_pane.set_code(f"/* CODE GENERATION ERROR:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()} */")
            print(f"MainWindow: Code generation EXCEPTION: {e}")
            traceback.print_exc()
        finally:
            self._is_regenerating_code = False