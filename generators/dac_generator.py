from core.mcu_defines_loader import CURRENT_MCU_DEFINES


def generate_dac_code_cmsis(config):
    params = config.get("params", {})  # Generator now gets full config, params are inside
    dac_instance_name = params.get("dac_instance", "DAC")
    channels_config = params.get("channels", [])
    mcu_family = params.get("mcu_family", "STM32F4")
    target_device = params.get("target_device", "STM32F407VG")

    error_messages = []
    rcc_clocks_to_enable = []
    source_function = ""
    init_call = ""
    gpio_pins_to_configure_analog = []

    if not params.get("enabled") or not channels_config:
        return {"source_function": f"// {dac_instance_name} not enabled or no channels configured\n",
                "init_call": "", "rcc_clocks_to_enable": [],
                "gpio_pins_to_configure_analog": [], "error_messages": []}

    # Check DAC availability on target
    target_mcu_info = CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {}).get(target_device, {})
    dac_instances_on_mcu = target_mcu_info.get("dac_instances", [])
    if not dac_instances_on_mcu:
        error_messages.append(f"DAC peripheral is not available on {target_device}.")
        return {"source_function": f"// DAC not available on {target_device}\n", "error_messages": error_messages}

    # Get DAC peripheral info (RCC macro, bit positions)
    dac_info_map_key = f"DAC_PERIPHERALS_INFO_{mcu_family}"
    dac_info_map = CURRENT_MCU_DEFINES.get(dac_info_map_key, CURRENT_MCU_DEFINES.get("DAC_PERIPHERALS_INFO", {}))
    # Assume dac_instances_on_mcu[0] is the name of the DAC block (e.g., "DAC1")
    dac_block_name_for_rcc = dac_instances_on_mcu[0]
    dac_block_info = dac_info_map.get(dac_block_name_for_rcc, {})

    rcc_macro = dac_block_info.get("rcc_macro")
    if rcc_macro:
        rcc_clocks_to_enable.append(rcc_macro)
    else:
        error_messages.append(f"RCC macro not found for DAC on {target_device}")

    # Get bit positions from CURRENT_MCU_DEFINES (with fallbacks to F4 style if not found)
    DAC_CR_EN1_Pos = CURRENT_MCU_DEFINES.get("DAC_CR_EN1_Pos", 0)
    DAC_CR_BOFF1_Pos = CURRENT_MCU_DEFINES.get("DAC_CR_BOFF1_Pos", 1)
    DAC_CR_TEN1_Pos = CURRENT_MCU_DEFINES.get("DAC_CR_TEN1_Pos", 2)
    DAC_CR_TSEL1_Pos = CURRENT_MCU_DEFINES.get("DAC_CR_TSEL1_Pos", 3)
    DAC_CR_WAVE1_Pos = CURRENT_MCU_DEFINES.get("DAC_CR_WAVE1_Pos", 6)
    DAC_CR_DMAEN1_Pos = CURRENT_MCU_DEFINES.get("DAC_CR_DMAEN1_Pos", 12)
    # CR offset for channel 2 (usually +16 for EN2, BOFF2 etc.)
    DAC_CH2_CR_OFFSET = CURRENT_MCU_DEFINES.get("DAC_CH2_CR_OFFSET", 16)

    source_function += f"void {dac_instance_name}_User_Init(void) {{\n"
    source_function += f"    // {dac_instance_name} ({mcu_family}) Configuration (CMSIS Register Level)\n\n"
    cr_val = 0

    for ch_cfg in channels_config:
        if not ch_cfg.get("enabled"): continue
        channel_id = ch_cfg.get("channel_id")
        cr_offset = 0 if channel_id == 1 else DAC_CH2_CR_OFFSET

        ob_str = ch_cfg.get("output_buffer_str", "Enabled")
        ob_options_key = f"DAC_OUTPUT_BUFFER_OPTIONS_{mcu_family}"
        ob_options = CURRENT_MCU_DEFINES.get(ob_options_key, CURRENT_MCU_DEFINES.get("DAC_OUTPUT_BUFFER_OPTIONS", {}))
        if ob_options.get(ob_str, 0) == 1:  # Buffer Disabled
            cr_val |= (1 << (DAC_CR_BOFF1_Pos + cr_offset))

        if ch_cfg.get("trigger_enabled"):
            cr_val |= (1 << (DAC_CR_TEN1_Pos + cr_offset))
            tsel_str = ch_cfg.get("trigger_source_str", "Software")
            tsel_map_key = f"DAC_TRIGGER_SOURCES_{mcu_family}"
            tsel_map = CURRENT_MCU_DEFINES.get(tsel_map_key, CURRENT_MCU_DEFINES.get("DAC_TRIGGER_SOURCES", {}))
            tsel_bits = tsel_map.get(tsel_str, 0b111)  # Default Software
            cr_val |= (tsel_bits << (DAC_CR_TSEL1_Pos + cr_offset))

        wave_str = ch_cfg.get("wave_generation_str", "Disabled")
        wave_map_key = f"DAC_WAVE_GENERATION_{mcu_family}"
        wave_map = CURRENT_MCU_DEFINES.get(wave_map_key, CURRENT_MCU_DEFINES.get("DAC_WAVE_GENERATION", {}))
        wave_bits = wave_map.get(wave_str, 0b00)
        if wave_bits != 0b00:
            cr_val |= (wave_bits << (DAC_CR_WAVE1_Pos + cr_offset))
            if not (cr_val & (1 << (DAC_CR_TEN1_Pos + cr_offset))):
                error_messages.append(f"DAC Ch{channel_id}: Wave generation requires Trigger to be enabled.")

        if ch_cfg.get("dma_enabled"): cr_val |= (1 << (DAC_CR_DMAEN1_Pos + cr_offset))
        cr_val |= (1 << (DAC_CR_EN1_Pos + cr_offset))  # Enable Channel

        dac_output_pins_map_key = f"DAC_OUTPUT_PINS_{mcu_family}"
        dac_output_pins_map = CURRENT_MCU_DEFINES.get(dac_output_pins_map_key,
                                                      CURRENT_MCU_DEFINES.get("DAC_OUTPUT_PINS", {}))
        pin_str = dac_output_pins_map.get(target_device, {}).get(f"DAC_OUT{channel_id}")
        if pin_str:
            port_char = pin_str[1];
            pin_num_str = pin_str[2:]
            if port_char.isalpha() and pin_num_str.isdigit():
                gpio_pins_to_configure_analog.append({'port_char': port_char, 'pin_num': int(pin_num_str),
                                                      'module': f'{dac_instance_name}_CH{channel_id}'})
                source_function += f"    // DAC Channel {channel_id} output: {pin_str} (Ensure GPIO is Analog mode)\n"
        else:
            error_messages.append(f"Output pin for DAC Ch{channel_id} not defined for {target_device}.")

    source_function += f"    DAC->CR = 0x{cr_val:08X}UL;\n\n"

    for ch_cfg in channels_config:  # Example initial values
        if ch_cfg.get("enabled"):
            channel_id = ch_cfg.get("channel_id")
            if not ch_cfg.get("dma_enabled") and wave_map.get(ch_cfg.get("wave_generation_str"), 0) == 0:
                dhr_reg_name = f"DHR12R{channel_id}"  # Default 12-bit right
                # Could use DAC_DATA_ALIGNMENTS to choose DHR8R1, DHR12L1 etc.
                source_function += f"    DAC->{dhr_reg_name} = 2048; // Example: Set Ch{channel_id} to mid-scale\n"
    if any(ch.get("enabled") for ch in channels_config): source_function += "\n"

    source_function += "}\n"
    init_call = f"{dac_instance_name}_User_Init();" if params.get("enabled") else ""

    return {"source_function": source_function, "init_call": init_call,
            "rcc_clocks_to_enable": list(set(rcc_clocks_to_enable)),
            "gpio_pins_to_configure_analog": gpio_pins_to_configure_analog,
            "error_messages": error_messages}