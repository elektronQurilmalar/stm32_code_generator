from core.mcu_defines_loader import CURRENT_MCU_DEFINES


def get_adc_prescaler_val(prescaler_str, mcu_family):
    # Prescaler values can differ or map to different bits
    map_key_family = f"ADC_PRESCALER_VAL_MAP_{mcu_family}"
    map_key_generic = "ADC_PRESCALER_VAL_MAP"
    val_map = CURRENT_MCU_DEFINES.get(map_key_family, CURRENT_MCU_DEFINES.get(map_key_generic, {}))
    return val_map.get(prescaler_str, 0b01)  # Default PCLK2/4


def get_adc_resolution_val(res_str, mcu_family):
    map_key_family = f"ADC_RESOLUTION_VAL_MAP_{mcu_family}"
    map_key_generic = "ADC_RESOLUTION_VAL_MAP"
    val_map = CURRENT_MCU_DEFINES.get(map_key_family, CURRENT_MCU_DEFINES.get(map_key_generic, {}))
    return val_map.get(res_str, 0b00)  # Default 12-bit


def get_adc_sampling_time_val(st_str, mcu_family):
    map_key_family = f"ADC_SAMPLING_TIME_VAL_MAP_{mcu_family}"
    map_key_generic = "ADC_SAMPLING_TIME_VAL_MAP"
    val_map = CURRENT_MCU_DEFINES.get(map_key_family, CURRENT_MCU_DEFINES.get(map_key_generic, {}))
    return val_map.get(st_str, 0b001)  # Default 15 cycles


def get_adc_channel_val(ch_str, mcu_family, target_device):
    # Channel mapping can be very device specific within a family
    # Try target_device specific map first, then family generic, then simple "INx" parsing
    device_map_key = f"ADC_CHANNEL_STR_TO_VAL_MAP_{target_device}"
    family_map_key = f"ADC_CHANNEL_STR_TO_VAL_MAP_{mcu_family}"
    generic_map_key = "ADC_CHANNEL_STR_TO_VAL_MAP"  # For common ones like TEMP, VREF

    val_map = CURRENT_MCU_DEFINES.get(device_map_key,
                                      CURRENT_MCU_DEFINES.get(family_map_key,
                                                              CURRENT_MCU_DEFINES.get(generic_map_key, {})))

    if ch_str in val_map: return val_map[ch_str]

    if ch_str.startswith("IN"):
        try:
            return int(ch_str[2:])
        except ValueError:
            pass
    print(f"Warning: Unknown ADC channel string '{ch_str}' for {target_device}, defaulting to 0.")
    return 0


def get_adc_ext_trigger_edge_val(edge_str, mcu_family):
    map_key_family = f"ADC_EXT_TRIG_EDGE_VAL_MAP_{mcu_family}"
    map_key_generic = "ADC_EXT_TRIG_EDGE_VAL_MAP"
    val_map = CURRENT_MCU_DEFINES.get(map_key_family, CURRENT_MCU_DEFINES.get(map_key_generic, {}))
    return val_map.get(edge_str, 0b00)  # Default Disabled


def get_adc_ext_trigger_source_val(src_str, mcu_family):
    map_key_family = f"ADC_EXT_TRIG_SOURCE_VAL_MAP_{mcu_family}"
    map_key_generic = "ADC_EXT_TRIG_SOURCE_VAL_MAP"
    val_map = CURRENT_MCU_DEFINES.get(map_key_family, CURRENT_MCU_DEFINES.get(map_key_generic, {}))
    return val_map.get(src_str, 0x0)  # Default depends on family, often TIM1_CC1


def generate_adc_code_cmsis(
        config):  # rcc_config_calculated removed, ADC gets PCLK from CURRENT_MCU_DEFINES if needed by calc
    params = config.get("params", {})
    mcu_family = params.get("mcu_family", "STM32F4")  # Get from config
    target_device = params.get("target_device", "STM32F407VG")  # Get from config
    error_messages = []

    # Get bit positions from CURRENT_MCU_DEFINES
    ADC_CR1_RES_Pos = CURRENT_MCU_DEFINES.get("ADC_CR1_RES_Pos", 24)  # Default F4
    ADC_CR1_SCAN_Pos = CURRENT_MCU_DEFINES.get("ADC_CR1_SCAN_Pos", 8)
    ADC_CR1_EOCIE_Pos = CURRENT_MCU_DEFINES.get("ADC_CR1_EOCIE_Pos", 5)
    ADC_CR1_OVRIE_Pos = CURRENT_MCU_DEFINES.get("ADC_CR1_OVRIE_Pos", 26)  # F4 has this, F1 handles OVR differently

    ADC_CR2_ADON_Pos = CURRENT_MCU_DEFINES.get("ADC_CR2_ADON_Pos", 0)
    ADC_CR2_CONT_Pos = CURRENT_MCU_DEFINES.get("ADC_CR2_CONT_Pos", 1)
    ADC_CR2_ALIGN_Pos = CURRENT_MCU_DEFINES.get("ADC_CR2_ALIGN_Pos", 11)
    ADC_CR2_EOCS_Pos = CURRENT_MCU_DEFINES.get("ADC_CR2_EOCS_Pos", 10)  # F4 specific
    ADC_CR2_EXTEN_Pos = CURRENT_MCU_DEFINES.get("ADC_CR2_EXTEN_Pos", 28)
    ADC_CR2_EXTEN_Msk = CURRENT_MCU_DEFINES.get("ADC_CR2_EXTEN_Msk", (0x3 << ADC_CR2_EXTEN_Pos))
    ADC_CR2_EXTSEL_Pos = CURRENT_MCU_DEFINES.get("ADC_CR2_EXTSEL_Pos", 24)
    ADC_CR2_EXTSEL_Msk = CURRENT_MCU_DEFINES.get("ADC_CR2_EXTSEL_Msk", (0xF << ADC_CR2_EXTSEL_Pos))
    ADC_CR2_SWSTART_Pos = CURRENT_MCU_DEFINES.get("ADC_CR2_SWSTART_Pos", 30)

    ADC_SQR1_L_Pos = CURRENT_MCU_DEFINES.get("ADC_SQR1_L_Pos", 20)

    ADC_CCR_ADCPRE_Pos = CURRENT_MCU_DEFINES.get("ADC_CCR_ADCPRE_Pos", 16)  # F4
    ADC_CCR_VBATE_Pos = CURRENT_MCU_DEFINES.get("ADC_CCR_VBATE_Pos", 22)
    ADC_CCR_TSVREFE_Pos = CURRENT_MCU_DEFINES.get("ADC_CCR_TSVREFE_Pos", 23)
    # F1 specifics for CR2
    ADC_CR2_CAL_Pos = CURRENT_MCU_DEFINES.get("ADC_CR2_CAL_Pos", 2)  # F1 Calibration
    ADC_CR2_EXTTRIG_Pos = CURRENT_MCU_DEFINES.get("ADC_CR2_EXTTRIG_Pos", 20)  # F1 EXTTRIG bit

    adc_instance_str = params.get("adc_instance", "ADC1")
    adc_base = adc_instance_str

    if not params.get("enabled"):
        return {"source_function": f"// {adc_base} not enabled\n", "init_call": "", "rcc_clocks_to_enable": [],
                "error_messages": []}

    source_function = f"void {adc_base}_User_Init(void) {{\n"
    source_function += f"    // {adc_base} ({mcu_family}) Configuration (CMSIS Register Level)\n\n"

    rcc_clocks = []
    adc_rcc_map_key = f"ADC_RCC_MAP_{mcu_family}"
    adc_rcc_map = CURRENT_MCU_DEFINES.get(adc_rcc_map_key, CURRENT_MCU_DEFINES.get("ADC_RCC_MAP", {}))
    rcc_macro = adc_rcc_map.get(adc_base)
    if rcc_macro:
        rcc_clocks.append(rcc_macro)
    else:
        error_messages.append(f"RCC macro for {adc_base} on {mcu_family} not found.")

    source_function += f"    // Ensure {adc_base} is disabled before configuration\n"
    source_function += f"    if ({adc_base}->CR2 & (1UL << {ADC_CR2_ADON_Pos})) {{\n"
    source_function += f"        {adc_base}->CR2 &= ~(1UL << {ADC_CR2_ADON_Pos});\n"
    source_function += "    }\n"
    source_function += "    // Wait for ADON to be cleared (optional for some changes, good practice)\n\n"

    if mcu_family != "STM32F1":  # F2/F4 common settings in ADC_CCR
        if adc_base == "ADC1":  # CCR usually configured via ADC1
            source_function += "    // Configure ADC Common settings (ADC_CCR)\n"
            ccr_val = 0
            prescaler_val = get_adc_prescaler_val(params.get("common_prescaler", "PCLK2 / 4"), mcu_family)
            ccr_val |= (prescaler_val << ADC_CCR_ADCPRE_Pos)
            if params.get("common_vbat_enabled"): ccr_val |= (1 << ADC_CCR_VBATE_Pos)
            if params.get("common_tsens_enabled"): ccr_val |= (1 << ADC_CCR_TSVREFE_Pos)
            source_function += f"    ADC->CCR = 0x{ccr_val:08X}UL;\n\n"
    else:  # STM32F1: Prescaler is in RCC_CFGR, no VBATE/TSVREFE in CCR.
        source_function += f"    // For STM32F1, ADC prescaler is in RCC->CFGR (ADCPRE bits).\n"
        source_function += f"    // This must be configured during RCC setup.\n"
        # No direct CCR setup for these items on F1. VBAT/TEMP usually dedicated channels.

    source_function += f"    // Configure {adc_base}_CR1\n"
    cr1_val = 0
    if mcu_family != "STM32F1":  # Resolution setting for F2/F4
        res_val = get_adc_resolution_val(params.get("resolution", "12-bit"), mcu_family)
        cr1_val |= (res_val << ADC_CR1_RES_Pos)
    if params.get("scan_mode"): cr1_val |= (1 << ADC_CR1_SCAN_Pos)
    if params.get("interrupt_eoc"): cr1_val |= (1 << ADC_CR1_EOCIE_Pos)
    if params.get("interrupt_overrun") and mcu_family != "STM32F1":  # OVRIE for F2/F4
        cr1_val |= (1 << ADC_CR1_OVRIE_Pos)
    source_function += f"    {adc_base}->CR1 = 0x{cr1_val:08X}UL;\n\n"

    source_function += f"    // Configure {adc_base}_CR2\n"
    cr2_val = 0
    if params.get("data_alignment", "Right") == "Left": cr2_val |= (1 << ADC_CR2_ALIGN_Pos)
    if params.get("continuous_mode"): cr2_val |= (1 << ADC_CR2_CONT_Pos)
    if mcu_family != "STM32F1":  # EOCS for F2/F4
        cr2_val |= (1 << ADC_CR2_EOCS_Pos)

    trigger_edge_str = params.get("regular_trigger_edge", "Disabled")
    trigger_source_str = params.get("regular_trigger_source", "Software")

    if mcu_family != "STM32F1":
        cr2_val &= ~ADC_CR2_EXTEN_Msk
        cr2_val &= ~ADC_CR2_EXTSEL_Msk
        if trigger_edge_str != "Disabled" and trigger_source_str != "Software":
            edge_val = get_adc_ext_trigger_edge_val(trigger_edge_str, mcu_family)
            src_val = get_adc_ext_trigger_source_val(trigger_source_str, mcu_family)
            cr2_val |= (edge_val << ADC_CR2_EXTEN_Pos)
            cr2_val |= (src_val << ADC_CR2_EXTSEL_Pos)
    else:  # STM32F1 trigger logic
        if trigger_edge_str != "Disabled" and trigger_source_str != "Software":
            cr2_val |= (1 << ADC_CR2_EXTTRIG_Pos)  # Enable external trigger
            # EXTSEL bits for F1 are different
            src_val_f1 = get_adc_ext_trigger_source_val(trigger_source_str, mcu_family)  # Use F1 specific map
            ADC_CR2_EXTSEL_Pos_F1 = CURRENT_MCU_DEFINES.get("ADC_CR2_EXTSEL_Pos_F1", 17)  # Example, get from defines
            ADC_CR2_EXTSEL_Msk_F1 = CURRENT_MCU_DEFINES.get("ADC_CR2_EXTSEL_Msk_F1", (0x7 << 17))
            cr2_val &= ~ADC_CR2_EXTSEL_Msk_F1
            cr2_val |= (src_val_f1 << ADC_CR2_EXTSEL_Pos_F1)
        else:
            cr2_val &= ~(1 << ADC_CR2_EXTTRIG_Pos)  # Disable external trigger

    source_function += f"    {adc_base}->CR2 = 0x{cr2_val:08X}UL;\n\n"

    # STM32F1 Calibration
    if mcu_family == "STM32F1":
        source_function += f"    // Start ADC Calibration for {adc_base} (STM32F1 specific)\n"
        source_function += f"    {adc_base}->CR2 |= (1UL << {ADC_CR2_CAL_Pos});\n"
        source_function += f"    while (({adc_base}->CR2 & (1UL << {ADC_CR2_CAL_Pos}))); // Wait for calibration to complete\n\n"

    regular_channels = params.get("regular_channels", [])
    if regular_channels:
        source_function += f"    // Configure Sample Times and Regular Sequence for {adc_base}\n"
        source_function += f"    {adc_base}->SMPR1 = 0x00000000UL;\n"
        source_function += f"    {adc_base}->SMPR2 = 0x00000000UL;\n"
        sqr1_val = 0;
        sqr2_val = 0;
        sqr3_val = 0;  # Start with 0 for SQR registers

        num_conv = params.get("regular_num_conversions", len(regular_channels))
        sqr1_l_val = (num_conv - 1) & 0xF  # L[3:0] in SQR1
        sqr1_val |= (sqr1_l_val << ADC_SQR1_L_Pos)
        source_function += f"    // Number of conversions = {num_conv}\n"

        for ch_config in regular_channels:
            rank = ch_config.get("rank");
            ch_val_str = ch_config.get("channel");
            st_val_str = ch_config.get("sampling_time")
            ch_num = get_adc_channel_val(ch_val_str, mcu_family, target_device)
            st_num = get_adc_sampling_time_val(st_val_str, mcu_family)

            if 0 <= ch_num <= 9:
                source_function += f"    {adc_base}->SMPR2 |= ({st_num}UL << ({ch_num * 3})); // Ch {ch_num} ({ch_val_str}) ST: {st_val_str}\n"
            elif 10 <= ch_num <= 18:
                source_function += f"    {adc_base}->SMPR1 |= ({st_num}UL << ({(ch_num - 10) * 3})); // Ch {ch_num} ({ch_val_str}) ST: {st_val_str}\n"

            if 1 <= rank <= 6:
                sqr3_val |= (ch_num << ((rank - 1) * 5))
            elif 7 <= rank <= 12:
                sqr2_val |= (ch_num << ((rank - 7) * 5))
            elif 13 <= rank <= 16:
                sqr1_val |= (ch_num << ((rank - 13) * 5))

        source_function += f"    {adc_base}->SQR1 = 0x{sqr1_val:08X}UL;\n"
        source_function += f"    {adc_base}->SQR2 = 0x{sqr2_val:08X}UL;\n"
        source_function += f"    {adc_base}->SQR3 = 0x{sqr3_val:08X}UL;\n\n"

    source_function += f"    // Enable {adc_base}\n"
    source_function += f"    {adc_base}->CR2 |= (1UL << {ADC_CR2_ADON_Pos});\n\n"

    if mcu_family == "STM32F1":  # Second ADON write for F1
        source_function += f"    // Second ADON write for STM32F1 to wake up from power down\n"
        source_function += f"    {adc_base}->CR2 |= (1UL << {ADC_CR2_ADON_Pos});\n"
        source_function += f"    // Wait for ADC to stabilize (a few ADC clock cycles)\n\n"

    if trigger_edge_str == "Disabled" and trigger_source_str == "Software" and not params.get("continuous_mode"):
        source_function += f"    // Start first conversion (software trigger)\n"
        source_function += f"    {adc_base}->CR2 |= (1UL << {ADC_CR2_SWSTART_Pos});\n\n"

    source_function += "}\n"
    init_call = f"{adc_base}_User_Init();"

    gpio_pins_analog = []
    adc_gpio_map_key = f"ADC_PIN_MAP_{target_device}"  # e.g. ADC_PIN_MAP_STM32F407VG
    adc_gpio_map = CURRENT_MCU_DEFINES.get(adc_gpio_map_key, {})
    for ch_config in regular_channels:
        ch_name_str = ch_config.get("channel")
        # Find pin corresponding to channel string (e.g. "IN0", "PA0_C", "TEMP")
        pin_info = adc_gpio_map.get(ch_name_str)  # Expects {'port':'A', 'pin':0 } or None
        if pin_info:
            gpio_pins_analog.append({'port_char': pin_info['port'], 'pin_num': pin_info['pin'], 'module': adc_base})
        elif ch_name_str and ch_name_str.startswith("IN"):  # Basic fallback for INx if no map
            # This is a rough guess and might not be correct for all MCUs/pins
            # The adc_gpio_map is preferred
            pass

    return {"source_function": source_function, "init_call": init_call,
            "rcc_clocks_to_enable": rcc_clocks, "gpio_pins_to_configure_analog": gpio_pins_analog,
            "error_messages": error_messages}