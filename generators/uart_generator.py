# --- MODIFIED FILE generators/uart_generator.py ---
from core.mcu_defines_loader import CURRENT_MCU_DEFINES


def calculate_brr_universal(pclk_freq_hz, baud_rate, over8_mode, mcu_family):
    if pclk_freq_hz == 0 or baud_rate == 0: return None

    brr_mant_pos = CURRENT_MCU_DEFINES.get(f"USART_BRR_DIV_Mantissa_Pos_{mcu_family}",
                                           CURRENT_MCU_DEFINES.get("USART_BRR_DIV_Mantissa_Pos", 4))
    brr_frac_pos = CURRENT_MCU_DEFINES.get(f"USART_BRR_DIV_Fraction_Pos_{mcu_family}",
                                           CURRENT_MCU_DEFINES.get("USART_BRR_DIV_Fraction_Pos", 0))

    if mcu_family == "STM32F1":
        # For F1, BRR = PCLK / BAUD. USARTDIV = PCLK / (16 * BAUD). BRR holds combined int+frac.
        # The value written to BRR is such that BRR = (PCLK / BAUD).
        # Integer part of (PCLK / BAUD) goes into DIV_Mantissa[11:0] (which is BRR[15:4])
        # Fractional part * 16 goes into DIV_Fraction[3:0] (which is BRR[3:0])
        usartdiv_x16 = (float(pclk_freq_hz) * 16.0) / (16.0 * baud_rate)  # This simplifies to PCLK/BAUD
        # No, the formula for F1 is USARTDIV = fCK / (16 * BaudRate). Then BRR = USARTDIV.
        # Mantissa is the integer part of USARTDIV, Fraction is fractional part * 16.
        usartdiv = float(pclk_freq_hz) / (16.0 * baud_rate)
        div_mantissa = int(usartdiv)
        div_fraction = int(round((usartdiv - div_mantissa) * 16.0))
        if div_fraction >= 16:  # Rollover fraction to mantissa
            div_mantissa += 1
            div_fraction = 0
        return (div_mantissa << brr_mant_pos) | (div_fraction << brr_frac_pos)
    else:  # F2/F4 style
        # Denominator for USARTDIV based on oversampling
        usartdiv_denom = (8.0 * (2.0 - over8_mode) * baud_rate)
        if usartdiv_denom == 0: return None
        usartdiv = float(pclk_freq_hz) / usartdiv_denom

        div_mantissa = int(usartdiv)

        if over8_mode == 0:  # OVER16
            # Fractional part is 4 bits
            div_fraction = int(round((usartdiv - div_mantissa) * 16.0))
            if div_fraction >= 16:  # Rollover fraction to mantissa
                div_mantissa += 1
                div_fraction = 0
        else:  # OVER8
            # Fractional part is 3 bits (BRR[2:0]), bit 3 is 0.
            div_fraction_temp = int(round((usartdiv - div_mantissa) * 8.0))
            if div_fraction_temp >= 8:
                div_mantissa += 1
                div_fraction_temp = 0
            div_fraction = div_fraction_temp & 0x07  # Mask to 3 bits
            # The value in BRR[3] must be 0 for OVER8. Our frac_pos is usually 0.
            # If frac_pos was different, ensure bit 3 relative to fraction start is zero.
            # Since frac_pos is 0, this is handled by masking to 3 bits.

        return (div_mantissa << brr_mant_pos) | (div_fraction << brr_frac_pos)


def generate_uart_code_cmsis(config, rcc_config_calculated):
    params = config.get("params", {})
    instance_name = params.get("instance_name")
    mcu_family = params.get("mcu_family", "STM32F4")
    target_device = params.get("target_device", "STM32F407VG")

    error_messages = [];
    gpio_pins_to_configure_af = [];
    default_helper_functions_code = ""

    if not instance_name or not params.get("enabled"):
        return {"source_function": f"// {instance_name or 'USART'} not enabled\n", "init_call": "",
                "rcc_clocks_to_enable": [], "gpio_pins_to_configure_af": [],
                "default_helper_functions": "", "error_messages": []}

    usart_info_map_key = f"USART_PERIPHERALS_INFO_{mcu_family}"
    usart_info_map = CURRENT_MCU_DEFINES.get(usart_info_map_key, CURRENT_MCU_DEFINES.get("USART_PERIPHERALS_INFO", {}))
    instance_info = usart_info_map.get(instance_name)
    if not instance_info: error_messages.append(f"Unknown USART instance: {instance_name}"); return {
        "error_messages": error_messages}

    USART_CR1_UE_Pos = CURRENT_MCU_DEFINES.get(f"USART_CR1_UE_Pos_{mcu_family}",
                                               CURRENT_MCU_DEFINES.get("USART_CR1_UE_Pos", 13))
    USART_CR1_M_Pos = CURRENT_MCU_DEFINES.get(f"USART_CR1_M_Pos_{mcu_family}",
                                              CURRENT_MCU_DEFINES.get("USART_CR1_M_Pos", 12))
    USART_CR1_PCE_Pos = CURRENT_MCU_DEFINES.get(f"USART_CR1_PCE_Pos_{mcu_family}",
                                                CURRENT_MCU_DEFINES.get("USART_CR1_PCE_Pos", 10))
    USART_CR1_PS_Pos = CURRENT_MCU_DEFINES.get(f"USART_CR1_PS_Pos_{mcu_family}",
                                               CURRENT_MCU_DEFINES.get("USART_CR1_PS_Pos", 9))
    USART_CR1_TE_Pos = CURRENT_MCU_DEFINES.get(f"USART_CR1_TE_Pos_{mcu_family}",
                                               CURRENT_MCU_DEFINES.get("USART_CR1_TE_Pos", 3))
    USART_CR1_RE_Pos = CURRENT_MCU_DEFINES.get(f"USART_CR1_RE_Pos_{mcu_family}",
                                               CURRENT_MCU_DEFINES.get("USART_CR1_RE_Pos", 2))
    USART_CR1_OVER8_Pos = CURRENT_MCU_DEFINES.get(f"USART_CR1_OVER8_Pos_{mcu_family}",
                                                  CURRENT_MCU_DEFINES.get("USART_CR1_OVER8_Pos", 15))
    USART_CR1_RXNEIE_Pos = CURRENT_MCU_DEFINES.get(f"USART_CR1_RXNEIE_Pos_{mcu_family}",
                                                   CURRENT_MCU_DEFINES.get("USART_CR1_RXNEIE_Pos", 5))
    USART_CR1_TXEIE_Pos = CURRENT_MCU_DEFINES.get(f"USART_CR1_TXEIE_Pos_{mcu_family}",
                                                  CURRENT_MCU_DEFINES.get("USART_CR1_TXEIE_Pos", 7))
    USART_CR1_TCIE_Pos = CURRENT_MCU_DEFINES.get(f"USART_CR1_TCIE_Pos_{mcu_family}",
                                                 CURRENT_MCU_DEFINES.get("USART_CR1_TCIE_Pos", 6))
    USART_CR1_PEIE_Pos = CURRENT_MCU_DEFINES.get(f"USART_CR1_PEIE_Pos_{mcu_family}",
                                                 CURRENT_MCU_DEFINES.get("USART_CR1_PEIE_Pos", 8))
    USART_CR2_STOP_Pos = CURRENT_MCU_DEFINES.get(f"USART_CR2_STOP_Pos_{mcu_family}",
                                                 CURRENT_MCU_DEFINES.get("USART_CR2_STOP_Pos", 12))
    USART_CR3_RTSE_Pos = CURRENT_MCU_DEFINES.get(f"USART_CR3_RTSE_Pos_{mcu_family}",
                                                 CURRENT_MCU_DEFINES.get("USART_CR3_RTSE_Pos", 8))
    USART_CR3_CTSE_Pos = CURRENT_MCU_DEFINES.get(f"USART_CR3_CTSE_Pos_{mcu_family}",
                                                 CURRENT_MCU_DEFINES.get("USART_CR3_CTSE_Pos", 9))
    USART_SR_RXNE_Pos = CURRENT_MCU_DEFINES.get(f"USART_SR_RXNE_Pos_{mcu_family}",
                                                CURRENT_MCU_DEFINES.get("USART_SR_RXNE_Pos", 5))
    USART_SR_TXE_Pos = CURRENT_MCU_DEFINES.get(f"USART_SR_TXE_Pos_{mcu_family}",
                                               CURRENT_MCU_DEFINES.get("USART_SR_TXE_Pos", 7))
    USART_SR_TC_Pos = CURRENT_MCU_DEFINES.get(f"USART_SR_TC_Pos_{mcu_family}",
                                              CURRENT_MCU_DEFINES.get("USART_SR_TC_Pos", 6))
    USART_SR_RXNE = (1 << USART_SR_RXNE_Pos)  # For helper functions
    USART_SR_TXE = (1 << USART_SR_TXE_Pos)
    USART_SR_TC = (1 << USART_SR_TC_Pos)

    pclk_freq = rcc_config_calculated.get(f"pclk{instance_info['bus'][-1]}_freq_hz", 0)
    if pclk_freq == 0: error_messages.append(f"PCLK for {instance_name} is 0Hz.")
    rcc_clocks = [instance_info["rcc_macro"]] if instance_info.get("rcc_macro") else []
    if not rcc_clocks: error_messages.append(f"RCC macro for {instance_name} not found.")

    source_function = f"void {instance_name}_User_Init(void) {{\n"
    source_function += f"    // {instance_name} ({mcu_family}) Configuration (CMSIS Register Level)\n\n"

    pin_sugg_map_key = f"USART_PIN_CONFIG_SUGGESTIONS_{mcu_family}"
    pin_sugg_map_all = CURRENT_MCU_DEFINES.get(pin_sugg_map_key,
                                               CURRENT_MCU_DEFINES.get("USART_PIN_CONFIG_SUGGESTIONS", {}))
    pin_suggestions = pin_sugg_map_all.get(target_device, {}).get(instance_name, {})
    if pin_suggestions:
        source_function += f"    // Suggested GPIO for {instance_name} on {target_device} (config in GPIO_User_Init):\n"
        pin_types_to_check = ["TX", "RX"]
        hw_flow_active = params.get("hw_flow_control", "None")
        if hw_flow_active in ["CTS", "RTS/CTS"]: pin_types_to_check.append("CTS")
        if hw_flow_active in ["RTS", "RTS/CTS"]: pin_types_to_check.append("RTS")
        for pin_type in pin_types_to_check:
            if pin_type in pin_suggestions:
                pin_options = pin_suggestions[pin_type].split(" or ");
                first_option = pin_options[0];
                parts = first_option.split('/')
                if len(parts) >= 1:
                    port_char = parts[0][1];
                    pin_num = parts[0][2:]
                    af_num_str = parts[1][2:] if len(parts) == 2 and parts[1].upper().startswith("AF") else "-1"
                    af_num = int(af_num_str) if af_num_str.lstrip('-').isdigit() else -1  # Handles "-1" or AF number
                    if mcu_family == "STM32F1": af_num = -1  # F1 AF is via remap usually
                    if port_char.isalpha() and pin_num.isdigit():
                        gpio_pins_to_configure_af.append((port_char, pin_num, af_num, f"{instance_name}_{pin_type}"))
                        source_function += f"    //   {pin_type}: {first_option} (AF{af_num if af_num != -1 else 'Remap'})\n"
        source_function += "\n"

    source_function += f"    if ({instance_name}->CR1 & (1UL << {USART_CR1_UE_Pos})) {{ {instance_name}->CR1 &= ~(1UL << {USART_CR1_UE_Pos}); }} // Disable USART\n\n"

    brr_val = 0
    baud_rate = params.get("baud_rate", 115200)
    oversampling_map_key = f"USART_OVERSAMPLING_MAP_{mcu_family}"
    oversampling_map = CURRENT_MCU_DEFINES.get(oversampling_map_key,
                                               CURRENT_MCU_DEFINES.get("USART_OVERSAMPLING_MAP", {"16": 0}))
    over8_mode = oversampling_map.get(params.get("oversampling", "16"), 0)
    if mcu_family == "STM32F2": over8_mode = 0  # F2 is always OVER16

    calculated_brr = calculate_brr_universal(pclk_freq, baud_rate, over8_mode, mcu_family)
    if calculated_brr is not None:
        brr_val = calculated_brr
    else:
        error_messages.append(f"Could not calc BRR for {instance_name}. PCLK={pclk_freq}, Baud={baud_rate}")
    source_function += f"    {instance_name}->BRR = 0x{brr_val:04X}UL; // Baud: {baud_rate}, PCLK: {pclk_freq}Hz, OVER8: {over8_mode if mcu_family not in ['STM32F1', 'STM32F2'] else 'N/A'}\n\n"

    cr1_val = 0
    if mcu_family not in ["STM32F1", "STM32F2"]:  # OVER8 bit exists on F4, not F1/F2
        cr1_val |= (over8_mode << USART_CR1_OVER8_Pos)

    word_len_map_key = f"USART_WORD_LENGTH_MAP_{mcu_family}"
    word_len_map = CURRENT_MCU_DEFINES.get(word_len_map_key, CURRENT_MCU_DEFINES.get("USART_WORD_LENGTH_MAP", {}))
    cr1_val |= (word_len_map.get(params.get("word_length", "8 bits"), 0) << USART_CR1_M_Pos)

    parity_map_key = f"USART_PARITY_MAP_{mcu_family}"
    parity_map = CURRENT_MCU_DEFINES.get(parity_map_key, CURRENT_MCU_DEFINES.get("USART_PARITY_MAP", {}))
    parity_val_encoded = parity_map.get(params.get("parity", "None"), 0)  # Encoded as 0b00 None, 0b10 Even, 0b11 Odd
    if parity_val_encoded & 0b10: cr1_val |= (1 << USART_CR1_PCE_Pos)  # Parity Enable
    if parity_val_encoded & 0b01: cr1_val |= (1 << USART_CR1_PS_Pos)  # Parity Selection (Odd if PCE=1,PS=1)

    mode_map_key = f"USART_MODE_MAP_{mcu_family}"
    mode_map = CURRENT_MCU_DEFINES.get(mode_map_key, CURRENT_MCU_DEFINES.get("USART_MODE_MAP", {}))
    mode_val_encoded = mode_map.get(params.get("mode", "TX/RX"), 0b11)  # Encoded as 0b01 RX, 0b10 TX, 0b11 TX/RX
    if mode_val_encoded & 0b10: cr1_val |= (1 << USART_CR1_TE_Pos)  # TX Enable
    if mode_val_encoded & 0b01: cr1_val |= (1 << USART_CR1_RE_Pos)  # RX Enable

    if params.get("interrupt_txe"): cr1_val |= (1 << USART_CR1_TXEIE_Pos)
    if params.get("interrupt_rxne"): cr1_val |= (1 << USART_CR1_RXNEIE_Pos)
    if params.get("interrupt_tcie"): cr1_val |= (1 << USART_CR1_TCIE_Pos)
    if params.get("interrupt_peie"): cr1_val |= (1 << USART_CR1_PEIE_Pos)
    source_function += f"    {instance_name}->CR1 = 0x{cr1_val:08X}UL;\n\n"

    cr2_val = 0
    stop_bits_map_key = f"USART_STOP_BITS_MAP_{mcu_family}"
    stop_bits_map = CURRENT_MCU_DEFINES.get(stop_bits_map_key, CURRENT_MCU_DEFINES.get("USART_STOP_BITS_MAP", {}))
    cr2_val |= (stop_bits_map.get(params.get("stop_bits", "1"), 0b00) << USART_CR2_STOP_Pos)
    source_function += f"    {instance_name}->CR2 = 0x{cr2_val:08X}UL;\n\n"

    cr3_val = 0
    hw_flow_map_key = f"USART_HW_FLOW_CTRL_MAP_{mcu_family}"
    hw_flow_map = CURRENT_MCU_DEFINES.get(hw_flow_map_key, CURRENT_MCU_DEFINES.get("USART_HW_FLOW_CTRL_MAP", {}))
    hw_flow_val_encoded = hw_flow_map.get(params.get("hw_flow_control", "None"),
                                          0b00)  # Encoded: 01 RTS, 10 CTS, 11 RTS/CTS
    if hw_flow_val_encoded & 0b01: cr3_val |= (1 << USART_CR3_RTSE_Pos)
    if hw_flow_val_encoded & 0b10: cr3_val |= (1 << USART_CR3_CTSE_Pos)
    source_function += f"    {instance_name}->CR3 = 0x{cr3_val:08X}UL;\n\n"

    source_function += f"    {instance_name}->CR1 |= (1UL << {USART_CR1_UE_Pos}); // Enable USART\n\n"
    source_function += "}\n"
    init_call = f"{instance_name}_User_Init();"

    if params.get("generate_rx_byte_func"):
        default_helper_functions_code += f"\nuint8_t {instance_name}_Receive_Byte(void) {{\n"
        default_helper_functions_code += f"    while (!({instance_name}->SR & USART_SR_RXNE));\n"
        default_helper_functions_code += f"    return (uint8_t)({instance_name}->DR);\n}}\n"
    if params.get("generate_tx_byte_func"):
        default_helper_functions_code += f"\nvoid {instance_name}_Transmit_Byte(uint8_t byte) {{\n"
        default_helper_functions_code += f"    while (!({instance_name}->SR & USART_SR_TXE));\n"
        default_helper_functions_code += f"    {instance_name}->DR = byte;\n"
        default_helper_functions_code += f"    // while (!({instance_name}->SR & USART_SR_TC)); // Optional: Wait for TC\n}}\n"
    if params.get("generate_tx_string_func") and params.get("generate_tx_byte_func"):
        default_helper_functions_code += f"\nvoid {instance_name}_Transmit_String(const char* str) {{\n"
        default_helper_functions_code += f"    while (*str) {{ {instance_name}_Transmit_Byte((uint8_t)*str++); }}\n"
        default_helper_functions_code += f"    // while (!({instance_name}->SR & USART_SR_TC)); // Optional: Wait for TC\n}}\n"
    elif params.get("generate_tx_string_func") and not params.get("generate_tx_byte_func"):
        error_messages.append(f"Cannot gen {instance_name}_Transmit_String: {instance_name}_Transmit_Byte not enabled.")

    return {"source_function": source_function, "init_call": init_call,
            "rcc_clocks_to_enable": rcc_clocks, "gpio_pins_to_configure_af": gpio_pins_to_configure_af,
            "default_helper_functions": default_helper_functions_code, "error_messages": error_messages}