# --- MODIFIED FILE widgets/configuration_pane.py ---

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedWidget
from PyQt5.QtCore import pyqtSignal

from modules.mcu_config_widget import MCUConfigWidget
from modules.rcc_config_widget import RCCConfigWidget
from modules.gpio_config_widget import GPIOConfigWidget
from modules.adc_config_widget import ADCConfigWidget
from modules.dac_config_widget import DACConfigWidget
from modules.uart_config_widget import UARTConfigWidget
from modules.timer_config_widget import TimerConfigWidget
from modules.i2c_config_widget import I2CConfigWidget
from modules.spi_config_widget import SPIConfigWidget
from modules.dma_config_widget import DMAConfigWidget
from modules.delay_config_widget import DelayConfigWidget

from core.mcu_defines_loader import set_current_mcu_defines, CURRENT_MCU_DEFINES


class ConfigurationPane(QWidget):
    config_changed = pyqtSignal(str, dict)
    mcu_target_device_globally_changed = pyqtSignal(str, str)  # new_mcu_device, new_mcu_family

    def __init__(self, initial_mcu_target, initial_mcu_family):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.stacked_widget = QStackedWidget()
        self.module_widgets = {}

        self.current_mcu_target_device = initial_mcu_target
        self.current_mcu_family = initial_mcu_family

        # Ensure defines are set for the initial state passed to ConfigurationPane
        if not set_current_mcu_defines(self.current_mcu_family):
            print(f"ERROR: ConfigurationPane __init__ failed to set defines for {self.current_mcu_family}")
            # Consider more robust error handling

        self.current_config_data = {}
        self._is_updating_mcu_globally = False  # Renamed for clarity

        # --- Initialize all module widgets ---
        self.mcu_widget = MCUConfigWidget()
        self.mcu_widget.config_updated.connect(self.on_mcu_widget_config_updated)
        self.stacked_widget.addWidget(self.mcu_widget)
        self.module_widgets["MCU"] = self.mcu_widget
        # Initial update for MCU widget itself AFTER it's fully constructed
        self.mcu_widget.update_for_target_device(self.current_mcu_target_device, self.current_mcu_family,
                                                 is_initial_call=True)

        self.rcc_widget = RCCConfigWidget()
        self.rcc_widget.config_updated.connect(self.on_rcc_config_updated_passthrough)
        self.stacked_widget.addWidget(self.rcc_widget)
        self.module_widgets["RCC"] = self.rcc_widget

        self.gpio_widget = GPIOConfigWidget()
        self.gpio_widget.config_updated.connect(lambda data: self.on_module_config_updated("GPIO", data))
        self.stacked_widget.addWidget(self.gpio_widget)
        self.module_widgets["GPIO"] = self.gpio_widget

        self.adc_widget = ADCConfigWidget()
        self.adc_widget.config_updated.connect(lambda data: self.on_module_config_updated("ADC", data))
        self.stacked_widget.addWidget(self.adc_widget)
        self.module_widgets["ADC"] = self.adc_widget

        self.dac_widget = DACConfigWidget()
        self.dac_widget.config_updated.connect(lambda data: self.on_module_config_updated("DAC", data))
        self.stacked_widget.addWidget(self.dac_widget)
        self.module_widgets["DAC"] = self.dac_widget

        self.timer_widget = TimerConfigWidget()
        self.timer_widget.config_updated.connect(lambda data: self.on_module_config_updated("TIMERS", data))
        self.stacked_widget.addWidget(self.timer_widget)
        self.module_widgets["TIMERS"] = self.timer_widget

        self.usart_widget = UARTConfigWidget()
        self.usart_widget.config_updated.connect(lambda data: self.on_module_config_updated("USART", data))
        self.stacked_widget.addWidget(self.usart_widget)
        self.module_widgets["USART"] = self.usart_widget

        self.i2c_widget = I2CConfigWidget()
        self.i2c_widget.config_updated.connect(lambda data: self.on_module_config_updated("I2C", data))
        self.stacked_widget.addWidget(self.i2c_widget)
        self.module_widgets["I2C"] = self.i2c_widget

        self.spi_widget = SPIConfigWidget()
        self.spi_widget.config_updated.connect(lambda data: self.on_module_config_updated("SPI", data))
        self.stacked_widget.addWidget(self.spi_widget)
        self.module_widgets["SPI"] = self.spi_widget

        self.dma_widget = DMAConfigWidget()
        self.dma_widget.config_updated.connect(lambda data: self.on_module_config_updated("DMA", data))
        self.stacked_widget.addWidget(self.dma_widget)
        self.module_widgets["DMA"] = self.dma_widget

        self.delay_widget = DelayConfigWidget()
        self.delay_widget.config_updated.connect(lambda data: self.on_module_config_updated("Delay", data))
        self.stacked_widget.addWidget(self.delay_widget)
        self.module_widgets["Delay"] = self.delay_widget

        self.default_widget = QLabel("Select a module to configure.")
        self.default_widget.setWordWrap(True)
        self.stacked_widget.addWidget(self.default_widget)
        self.layout.addWidget(self.stacked_widget)
        self.current_module_name = None

        self.update_all_sub_widgets_for_mcu(self.current_mcu_target_device, self.current_mcu_family,
                                            is_initial_setup=True)

    def on_mcu_widget_config_updated(self, mcu_config_data):
        # print(f"ConfigurationPane: on_mcu_widget_config_updated with data: {mcu_config_data}")
        if self._is_updating_mcu_globally:  # Prevent re-entry if this is part of a global update cycle
            # print("ConfigurationPane: Bailing from on_mcu_widget_config_updated: _is_updating_mcu_globally is True")
            return

        self.current_config_data["MCU"] = mcu_config_data  # Store the MCU config
        new_target_device = mcu_config_data.get("target_device")
        new_mcu_family = mcu_config_data.get("mcu_family")

        mcu_actually_changed = False
        if new_mcu_family and self.current_mcu_family != new_mcu_family:
            # print(f"ConfigurationPane: Family changed from {self.current_mcu_family} to {new_mcu_family}")
            self.current_mcu_family = new_mcu_family
            # Critical: Load defines for the new family. This step is vital.
            if not set_current_mcu_defines(self.current_mcu_family):
                print(f"ERROR: ConfigurationPane - Failed to set MCU defines for new family {self.current_mcu_family}.")
                # Handle this error robustly, e.g., show a message, prevent further actions.
                return
            mcu_actually_changed = True

        if new_target_device and self.current_mcu_target_device != new_target_device:
            # print(f"ConfigurationPane: Device changed from {self.current_mcu_target_device} to {new_target_device}")
            self.current_mcu_target_device = new_target_device
            mcu_actually_changed = True

        if mcu_actually_changed:
            # print(f"ConfigurationPane: MCU settings actually changed. Setting flag and emitting global signal.")
            self._is_updating_mcu_globally = True
            # This signal will be caught by MainWindow, which will then call
            # self.update_all_sub_widgets_for_mcu(...) on this ConfigurationPane instance.
            self.mcu_target_device_globally_changed.emit(self.current_mcu_target_device, self.current_mcu_family)
            self._is_updating_mcu_globally = False  # Reset flag after emitting

        # Always emit the "MCU" module's own config change for MainWindow to process its content
        # print(f"ConfigurationPane: Emitting config_changed for MCU module itself.")
        self.config_changed.emit("MCU", mcu_config_data)

    def on_rcc_config_updated_passthrough(self, rcc_data):
        # print(f"ConfigurationPane: RCC config updated passthrough.")
        if self._is_updating_mcu_globally: return

        # Ensure context is correct
        if "params" in rcc_data and isinstance(rcc_data["params"], dict):
            rcc_data["params"]["target_device"] = self.current_mcu_target_device
            rcc_data["params"]["mcu_family"] = self.current_mcu_family

        self.current_config_data["RCC"] = rcc_data
        self.config_changed.emit("RCC", rcc_data)

    def update_all_sub_widgets_for_mcu(self, mcu_device_name, mcu_family_name, is_initial_setup=False):
        # print(f"ConfigurationPane: update_all_sub_widgets_for_mcu for {mcu_device_name}, {mcu_family_name}. Initial: {is_initial_setup}")
        if self._is_updating_mcu_globally and not is_initial_setup:  # Check if already in a global update
            # print("ConfigurationPane: Bailing update_all_sub_widgets: _is_updating_mcu_globally is True (called re-entrantly)")
            return
        self._is_updating_mcu_globally = True  # Set flag to indicate global update in progress

        try:
            # Crucially, ensure global defines are set for the target family before updating children
            if not set_current_mcu_defines(mcu_family_name):
                print(
                    f"ERROR: ConfigurationPane.update_all_sub_widgets_for_mcu failed to set defines for {mcu_family_name}")
                self._is_updating_mcu_globally = False  # Reset flag
                return

            # Update current tracking variables within ConfigurationPane
            self.current_mcu_target_device = mcu_device_name
            self.current_mcu_family = mcu_family_name

            for module_key, module_widget in self.module_widgets.items():
                # print(f"ConfigurationPane: Updating sub-widget: {module_key}")
                if hasattr(module_widget, 'update_for_target_device'):
                    module_widget.update_for_target_device(
                        mcu_device_name,
                        target_family_name=mcu_family_name,
                        is_initial_call=is_initial_setup  # Pass this along
                    )

                # After updating the widget, get its (potentially new default) config.
                # This ensures that if update_for_target_device changed default values,
                # the stored config and subsequent code generation reflect this.
                if module_key != "MCU":  # MCU is the source of this change, its config is already handled
                    new_module_cfg = self.get_module_config_data(module_key)  # Fetches with current MCU context
                    if new_module_cfg is not None:
                        self.current_config_data[module_key] = new_module_cfg
                        # If this is NOT the initial setup (meaning it's a user-driven MCU change),
                        # we need to inform MainWindow that this module's config might have effectively changed
                        # due to new defaults for the new MCU.
                        if not is_initial_setup:
                            # print(f"ConfigurationPane: Emitting config_changed for {module_key} after MCU update.")
                            self.config_changed.emit(module_key, new_module_cfg)

        finally:
            self._is_updating_mcu_globally = False  # Reset flag
        # print(f"ConfigurationPane: update_all_sub_widgets_for_mcu finished.")

    def display_module_config(self, module_name):
        # print(f"ConfigurationPane: display_module_config for {module_name}")
        self.current_module_name = module_name
        if module_name in self.module_widgets:
            widget_to_display = self.module_widgets[module_name]

            # Ensure the widget is up-to-date with the current MCU before displaying
            # This catches cases where an MCU change happened while this widget wasn't active
            if hasattr(widget_to_display, 'update_for_target_device'):
                # print(f"ConfigurationPane: display_module_config - calling update_for_target_device on {module_name}")
                widget_to_display.update_for_target_device(
                    self.current_mcu_target_device,
                    target_family_name=self.current_mcu_family,
                    is_initial_call=False
                    # It's not an initial app setup, but could be first time widget shown after MCU change
                )

            if module_name == "Delay" and hasattr(widget_to_display, 'update_timer_configs'):
                timers_config = self.current_config_data.get("TIMERS", {})
                widget_to_display.update_timer_configs(timers_config)

            self.stacked_widget.setCurrentWidget(widget_to_display)
        else:
            self.stacked_widget.setCurrentWidget(self.default_widget)

    def on_module_config_updated(self, module_name, data):
        # print(f"ConfigurationPane: on_module_config_updated for {module_name}")
        if self._is_updating_mcu_globally: return

        if isinstance(data, dict):
            if "params" in data and isinstance(data["params"], dict):
                data["params"]["target_device"] = self.current_mcu_target_device
                data["params"]["mcu_family"] = self.current_mcu_family
            elif "target_device" not in data:  # For flat configs
                data["target_device"] = self.current_mcu_target_device
                data["mcu_family"] = self.current_mcu_family

        self.current_config_data[module_name] = data

        if module_name == "TIMERS":
            if "Delay" in self.module_widgets and hasattr(self.module_widgets["Delay"], 'update_timer_configs'):
                self.module_widgets["Delay"].update_timer_configs(data)

        # print(f"ConfigurationPane: Emitting config_changed for {module_name}")
        self.config_changed.emit(module_name, data)

    def get_module_config_data(self, module_name):
        # print(f"ConfigurationPane: get_module_config_data for {module_name}")
        if module_name in self.module_widgets and hasattr(self.module_widgets[module_name], 'get_config'):
            config_data = self.module_widgets[module_name].get_config()
            if isinstance(config_data, dict):
                # Ensure the MCU context is correctly set in the returned config
                if "params" in config_data and isinstance(config_data["params"], dict):
                    config_data["params"]["target_device"] = self.current_mcu_target_device
                    config_data["params"]["mcu_family"] = self.current_mcu_family
                elif "target_device" not in config_data:  # For flat configs (like MCU itself)
                    config_data["target_device"] = self.current_mcu_target_device
                    config_data["mcu_family"] = self.current_mcu_family
            # print(f"ConfigurationPane: Got config for {module_name}: keys={list(config_data.keys()) if config_data else 'None'}")
            return config_data
        # print(f"ConfigurationPane: No config found for {module_name} or widget has no get_config")
        return None

    def get_all_configurations(self):
        # print("ConfigurationPane: get_all_configurations called")
        all_configs = {}

        # Get MCU config first to establish current context
        mcu_cfg_from_widget = self.module_widgets["MCU"].get_config()
        if mcu_cfg_from_widget:
            all_configs["MCU"] = mcu_cfg_from_widget
            # Update pane's internal MCU state from the widget as the source of truth
            self.current_mcu_target_device = mcu_cfg_from_widget.get("target_device", self.current_mcu_target_device)
            self.current_mcu_family = mcu_cfg_from_widget.get("mcu_family", self.current_mcu_family)
        else:  # Fallback if MCU widget somehow failed
            all_configs["MCU"] = {"target_device": self.current_mcu_target_device,
                                  "mcu_family": self.current_mcu_family}

        # Ensure global defines are set based on the definitive MCU selection before fetching other configs
        if not set_current_mcu_defines(self.current_mcu_family):
            print(f"ERROR: get_all_configurations - Failed to set defines for {self.current_mcu_family}")
            # This is a critical error, might need to stop or return partial/error state

        # For all other modules, fetch their current config
        for module_name in self.module_widgets.keys():
            if module_name == "MCU": continue  # Already processed

            # Fetch fresh config data from each widget to ensure it's up-to-date
            # with any internal changes or defaults based on the current MCU context
            config_from_widget = self.get_module_config_data(module_name)

            if config_from_widget is not None:
                all_configs[module_name] = config_from_widget
                self.current_config_data[module_name] = config_from_widget  # Update internal store
            else:
                # If widget returns None, use previously stored config if available, or empty
                all_configs[module_name] = self.current_config_data.get(module_name, {})

        # Ensure global MCU info is also at the top level of all_configs (for MainWindow direct use)
        all_configs['target_device'] = self.current_mcu_target_device
        all_configs['mcu_family'] = self.current_mcu_family
        # print(f"ConfigurationPane: get_all_configurations returning keys: {list(all_configs.keys())}")
        return all_configs