from core.mcu_defines_loader import CURRENT_MCU_DEFINES


def calculate_i2c_timing(pclk1_freq_hz, i2c_clk_speed_hz, duty_cycle_is_16_9, mcu_family):
    if pclk1_freq_hz == 0 or i2c_clk_speed_hz == 0:
        return {"error": "PCLK1 or I2C clock speed is zero."}
    ccr_val = 0;
    fs_bit = 0;
    duty_bit = 0

    # F1 timing is different from F2/F4 for CCR calculation
    if mcu_family == "STM32F1":
        if i2c_clk_speed_hz > 100000: fs_bit = 1  # Fast mode
        # F1 CCR calculation:
        # Standard: CCR = PCLK1 / (2 * SCL)
        # Fast: CCR = PCLK1 / (3 * SCL) for DUTY=0 (Tlow/Thigh=2)
        # Fast: CCR = PCLK1 / (25 * SCL) for DUTY=1 (Tlow/Thigh=16/9)
        if fs_bit == 0:  # Standard Mode
            ccr_val = int(round(pclk1_freq_hz / (2 * i2c_clk_speed_hz)))
            if ccr_val < 0x04: ccr_val = 0x04  # Min value for standard mode
        else:  # Fast Mode
            if duty_cycle_is_16_9:  # Tlow/Thigh = 16/9
                duty_bit = 1
                ccr_val = int(round(pclk1_freq_hz / (25 * i2c_clk_speed_hz)))
            else:  # Tlow/Thigh = 2
                duty_bit = 0
                ccr_val = int(round(pclk1_freq_hz / (3 * i2c_clk_speed_hz)))
            if ccr_val < 0x01: ccr_val = 0x01  # Min value for fast mode
    else:  # F2/F4 style (similar, but check RM for exact differences if any)
        if i2c_clk_speed_hz <= 100000:  # Standard Mode
            ccr_val = int(round(pclk1_freq_hz / (2 * i2c_clk_speed_hz)))
            if ccr_val < 0x04: ccr_val = 0x04
            fs_bit = 0
        else:  # Fast Mode
            fs_bit = 1
            if duty_cycle_is_16_9:
                duty_bit = 1; ccr_val = int(round(pclk1_freq_hz / (25 * i2c_clk_speed_hz)))
            else:
                duty_bit = 0; ccr_val = int(round(pclk1_freq_hz / (3 * i2c_clk_speed_hz)))
            if ccr_val < 0x01: ccr_val = 0x01

    max_rise_time_ns = 1000 if i2c_clk_speed_hz <= 100000 else 300  # Standard vs Fast
    tpclk1_ns = (1.0 / pclk1_freq_hz) * 1e9 if pclk1_freq_hz > 0 else float('inf')
    trise_val = int(round(max_rise_time_ns / tpclk1_ns)) + 1 if tpclk1_ns > 0 and tpclk1_ns != float('inf') else 2

    max_trise_from_pclk = (pclk1_freq_hz // 1000000) + 1 if pclk1_freq_hz > 0 else 2
    if mcu_family == "STM32F1":  # F1 TRISE has max of PCLK_MHz + 1
        if trise_val > max_trise_from_pclk: trise_val = max_trise_from_pclk
    else:  # F2/F4 limit to 6 bits
        if trise_val > 0x3F: trise_val = 0x3F
    if trise_val == 0 and pclk1_freq_hz > 0: trise_val = 1  # Min value for TRISE

    I2C_CCR_CCR_Msk = CURRENT_MCU_DEFINES.get("I2C_CCR_CCR_Msk", 0xFFF)  # Default F4
    return {"ccr_val": ccr_val & I2C_CCR_CCR_Msk, "fs_bit": fs_bit, "duty_bit": duty_bit,
            "trise_val": trise_val & (0x3F if mcu_family != "STM32F1" else 0xFF), "error": None}


def generate_i2c_code_cmsis(config, rcc_config_calculated):
    params = config.get("params", {})
    instance_name = params.get("instance_name")
    mcu_family = params.get("mcu_family", "STM32F4")
    target_device = params.get("target_device", "STM32F407VG")

    error_messages = [];
    gpio_pins_to_configure_af = [];
    default_helper_functions_code = ""

    if not instance_name or not params.get("enabled"):
        return {"source_function": f"// {instance_name or 'I2C'} not enabled\n", "init_call": "",
                "rcc_clocks_to_enable": [], "gpio_pins_to_configure_af": [],
                "default_helper_functions": "", "error_messages": []}

    # Get peripheral info and bit positions from CURRENT_MCU_DEFINES
    i2c_info_map_key = f"I2C_PERIPHERALS_INFO_{mcu_family}"
    i2c_info_map = CURRENT_MCU_DEFINES.get(i2c_info_map_key, CURRENT_MCU_DEFINES.get("I2C_PERIPHERALS_INFO", {}))
    instance_info = i2c_info_map.get(instance_name)
    if not instance_info: error_messages.append(f"Unknown I2C instance: {instance_name}"); return {
        "error_messages": error_messages}

    I2C_CR1_PE_Pos = CURRENT_MCU_DEFINES.get("I2C_CR1_PE_Pos", 0)
    I2C_CR1_SWRST_Pos = CURRENT_MCU_DEFINES.get("I2C_CR1_SWRST_Pos", 15)
    I2C_CR2_FREQ_Pos = CURRENT_MCU_DEFINES.get("I2C_CR2_FREQ_Pos", 0)
    I2C_CR2_FREQ_Msk = CURRENT_MCU_DEFINES.get("I2C_CR2_FREQ_Msk", 0x3F)
    I2C_CCR_FS_Pos = CURRENT_MCU_DEFINES.get("I2C_CCR_FS_Pos", 15)
    I2C_CCR_DUTY_Pos = CURRENT_MCU_DEFINES.get("I2C_CCR_DUTY_Pos", 14)  # Not on F1
    I2C_CCR_CCR_Pos = CURRENT_MCU_DEFINES.get("I2C_CCR_CCR_Pos", 0)
    I2C_CR1_ENGC_Pos = CURRENT_MCU_DEFINES.get("I2C_CR1_ENGC_Pos", 6)
    I2C_CR1_NOSTRETCH_Pos = CURRENT_MCU_DEFINES.get("I2C_CR1_NOSTRETCH_Pos", 7)
    I2C_CR1_ITEVTEN_Pos = CURRENT_MCU_DEFINES.get("I2C_CR1_ITEVTEN_Pos", 9)  # F1 is bit 9, F4 bit 10
    I2C_CR1_ITBUFEN_Pos = CURRENT_MCU_DEFINES.get("I2C_CR1_ITBUFEN_Pos", 10)  # F1 is bit 10, F4 bit 9
    I2C_CR1_ITERREN_Pos = CURRENT_MCU_DEFINES.get("I2C_CR1_ITERREN_Pos", 8)
    I2C_OAR1_ADDMODE_Pos = CURRENT_MCU_DEFINES.get("I2C_OAR1_ADDMODE_Pos", 15)  # 10-bit mode select

    pclk1_freq = rcc_config_calculated.get("pclk1_freq_hz", 0)
    if instance_info["bus"] != "APB1": error_messages.append(
        f"I2C {instance_name} unexpected bus: {instance_info['bus']}.")
    if pclk1_freq == 0: error_messages.append(f"PCLK1 for {instance_name} is 0Hz. Check RCC.")

    rcc_clocks = [instance_info["rcc_macro"]] if instance_info.get("rcc_macro") else []
    if not rcc_clocks: error_messages.append(f"RCC macro for {instance_name} not found.")

    source_function = f"void {instance_name}_User_Init(void) {{\n"
    source_function += f"    // {instance_name} ({mcu_family}) Configuration (CMSIS Register Level)\n\n"

    pin_sugg_map_key = f"I2C_PIN_CONFIG_SUGGESTIONS_{mcu_family}"
    pin_sugg_map = CURRENT_MCU_DEFINES.get(pin_sugg_map_key, CURRENT_MCU_DEFINES.get("I2C_PIN_CONFIG_SUGGESTIONS", {}))
    pin_suggestions = pin_sugg_map.get(target_device, {}).get(instance_name, {})
    if pin_suggestions:  # Populate AF pins
        source_function += f"    // Suggested GPIO for {instance_name} on {target_device} (config in GPIO_User_Init):\n"
        for pin_type, pin_data_str in pin_suggestions.items():  # SCL, SDA
            pin_options = pin_data_str.split(" or ")  # "PB6/AF4 or PB8/AF4"
            first_option = pin_options[0]  # Take first option "PB6/AF4"
            parts = first_option.split('/')
            if len(parts) >= 1:
                pin_name_only = parts[0]  # "PB6"
                port_char = pin_name_only[1];
                pin_num = pin_name_only[2:]
                af_num = 4  # Default I2C AF for F4, F1 uses remap
                if len(parts) == 2 and parts[1].upper().startswith("AF"):
                    try:
                        af_num = int(parts[1][2:])
                    except ValueError:
                        pass
                if mcu_family == "STM32F1": af_num = -1  # Use -1 or special string for F1 remap
                if port_char.isalpha() and pin_num.isdigit():
                    gpio_pins_to_configure_af.append((port_char, pin_num, af_num, f"{instance_name}_{pin_type}"))
                    source_function += f"    //   {pin_type}: {first_option} (Open-Drain, AF{af_num if af_num != -1 else 'Remap'})\n"
        source_function += "\n"

    source_function += f"    if ({instance_name}->CR1 & (1UL << {I2C_CR1_PE_Pos})) {{ {instance_name}->CR1 &= ~(1UL << {I2C_CR1_PE_Pos}); }}\n"
    source_function += f"    {instance_name}->CR1 |= (1UL << {I2C_CR1_SWRST_Pos});\n"
    source_function += f"    {instance_name}->CR1 &= ~(1UL << {I2C_CR1_SWRST_Pos});\n\n"

    pclk1_mhz = pclk1_freq // 1000000
    min_pclk_mhz = CURRENT_MCU_DEFINES.get("I2C_MIN_PCLK_MHZ", 2)
    if not (min_pclk_mhz <= pclk1_mhz <= 50):  # F407 max PCLK for I2C is 50MHz
        error_messages.append(f"PCLK1 ({pclk1_mhz}MHz) for I2C out of range ({min_pclk_mhz}-50MHz for F4).")

    source_function += f"    {instance_name}->CR2 = ({instance_name}->CR2 & ~{I2C_CR2_FREQ_Msk}) | ({pclk1_mhz if pclk1_mhz >= min_pclk_mhz else min_pclk_mhz}UL << {I2C_CR2_FREQ_Pos});\n\n"

    i2c_speeds_map_key = f"I2C_CLOCK_SPEEDS_HZ_{mcu_family}"
    i2c_speeds_map = CURRENT_MCU_DEFINES.get(i2c_speeds_map_key, CURRENT_MCU_DEFINES.get("I2C_CLOCK_SPEEDS_HZ", {}))
    i2c_speed_hz = i2c_speeds_map.get(params.get("clock_speed_str", "100000 Hz (Standard Mode)"), 100000)

    duty_is_16_9 = False
    if i2c_speed_hz > 100000 and mcu_family != "STM32F1":  # Duty cycle bit relevant for F2/F4 Fast Mode
        duty_modes_map_key = f"I2C_DUTY_CYCLE_MODES_{mcu_family}"
        duty_modes_map = CURRENT_MCU_DEFINES.get(duty_modes_map_key,
                                                 CURRENT_MCU_DEFINES.get("I2C_DUTY_CYCLE_MODES", {}))
        duty_is_16_9 = (duty_modes_map.get(params.get("duty_cycle_str"), 0) == 1)

    timing_calc = calculate_i2c_timing(pclk1_freq, i2c_speed_hz, duty_is_16_9, mcu_family) if pclk1_freq > 0 else {
        "error": "PCLK1=0"}
    if timing_calc.get("error"): error_messages.append(f"I2C timing error for {instance_name}: {timing_calc['error']}")

    ccr_reg_val = 0
    if timing_calc.get("fs_bit"): ccr_reg_val |= (1 << I2C_CCR_FS_Pos)
    if (timing_calc.get("duty_bit") and mcu_family != "STM32F1"):
        ccr_reg_val |= (1 << I2C_CCR_DUTY_Pos)  # DUTY bit not on F1
    ccr_reg_val |= (timing_calc.get("ccr_val", 0x04) << I2C_CCR_CCR_Pos)
    source_function += f"    {instance_name}->CCR = 0x{ccr_reg_val:04X}UL; // SCL: {i2c_speed_hz}Hz, PCLK1: {pclk1_freq / 1e6:.1f}MHz\n\n"

    trise_val = timing_calc.get("trise_val", (pclk1_mhz if pclk1_mhz > 0 else 2) + 1)
    source_function += f"    {instance_name}->TRISE = {trise_val}UL;\n\n"

    cr1_val_temp = 0
    if params.get("general_call_address_enabled"): cr1_val_temp |= (1 << I2C_CR1_ENGC_Pos)
    if not params.get("clock_stretching_enabled", True): cr1_val_temp |= (
                1 << I2C_CR1_NOSTRETCH_Pos)  # NOSTRETCH bit might vary
    if params.get("interrupt_event_enabled"): cr1_val_temp |= (1 << I2C_CR1_ITEVTEN_Pos)
    if params.get("interrupt_buffer_enabled"): cr1_val_temp |= (1 << I2C_CR1_ITBUFEN_Pos)
    if params.get("interrupt_error_enabled"): cr1_val_temp |= (1 << I2C_CR1_ITERREN_Pos)
    source_function += f"    {instance_name}->CR1 = ({instance_name}->CR1 & ~((1<<I2C_CR1_ENGC_Pos)|(1<<I2C_CR1_NOSTRETCH_Pos)|(1<<I2C_CR1_ITEVTEN_Pos)|(1<<I2C_CR1_ITBUFEN_Pos)|(1<<I2C_CR1_ITERREN_Pos))) | 0x{cr1_val_temp:08X}UL;\n\n"

    addr_mode_str = params.get("addressing_mode_str", "7-bit")
    addr_modes_map_key = f"I2C_ADDRESSING_MODES_{mcu_family}"
    addr_modes_map = CURRENT_MCU_DEFINES.get(addr_modes_map_key, CURRENT_MCU_DEFINES.get("I2C_ADDRESSING_MODES", {}))
    addr_mode_bit_val = addr_modes_map.get(addr_mode_str, 0)  # 0 for 7-bit, 1 for 10-bit (conceptual)
    own_addr1 = params.get("own_address1", 0x00)
    oar1_val = 0
    if addr_mode_bit_val == 0:  # 7-bit
        oar1_val = (own_addr1 & 0x7F) << 1
    else:  # 10-bit
        oar1_val = (own_addr1 & 0x3FF)
    oar1_val |= (1 << I2C_OAR1_ADDMODE_Pos)  # Set ADDMODE for 10-bit
    oar1_val |= (1 << 14)  # Bit 14 must be kept at 1 by software for I2C
    source_function += f"    {instance_name}->OAR1 = 0x{oar1_val:08X}UL;\n\n"

    if params.get("dual_address_mode_enabled", False) and mcu_family != "STM32F1":  # OAR2 not on all F1
        own_addr2 = params.get("own_address2", 0x00) & 0x7F
        oar2_val = (own_addr2 << 1) | (1 << 0)  # ENDUAL bit to enable OAR2
        source_function += f"    {instance_name}->OAR2 = 0x{oar2_val:08X}UL;\n\n"
    else:
        source_function += f"    {instance_name}->OAR2 = 0x00000000UL; // OAR2 Disabled\n\n"

    source_function += f"    {instance_name}->CR1 |= (1UL << {I2C_CR1_PE_Pos}); // Enable I2C\n\n"
    source_function += "}\n"
    init_call = f"{instance_name}_User_Init();"

    # Helper functions are mostly standard, but bit names/availability might change slightly
    if params.get("generate_master_tx_func") or params.get("generate_master_rx_func"):
        timeout_def = f"#define {instance_name}_I2C_TIMEOUT 100000 // Basic I2C timeout\n"
    if timeout_def not in default_helper_functions_code: default_helper_functions_code += timeout_def

    # Bit positions for SR1/CR1 helpers
    I2C_SR1_SB_Pos_H = CURRENT_MCU_DEFINES.get("I2C_SR1_SB_Pos", 0)
    I2C_SR1_ADDR_Pos_H = CURRENT_MCU_DEFINES.get("I2C_SR1_ADDR_Pos", 1)
    I2C_SR1_TXE_Pos_H = CURRENT_MCU_DEFINES.get("I2C_SR1_TXE_Pos", 7)
    I2C_SR1_RXNE_Pos_H = CURRENT_MCU_DEFINES.get("I2C_SR1_RXNE_Pos", 6)
    I2C_SR1_BTF_Pos_H = CURRENT_MCU_DEFINES.get("I2C_SR1_BTF_Pos", 2)
    I2C_CR1_START_Pos_H = CURRENT_MCU_DEFINES.get("I2C_CR1_START_Pos", 8)
    I2C_CR1_STOP_Pos_H = CURRENT_MCU_DEFINES.get("I2C_CR1_STOP_Pos", 9)
    I2C_CR1_ACK_Pos_H = CURRENT_MCU_DEFINES.get("I2C_CR1_ACK_Pos", 10)

    if params.get("generate_master_tx_func"):
        default_helper_functions_code += f"\nint {instance_name}_Master_Transmit(uint8_t addr, uint8_t* data, uint16_t size) {{\n"
    default_helper_functions_code += f"    volatile uint32_t timeout = {instance_name}_I2C_TIMEOUT;\n"
    default_helper_functions_code += f"    {instance_name}->CR1 |= (1UL << {I2C_CR1_START_Pos_H});\n"
    default_helper_functions_code += f"    while (!({instance_name}->SR1 & (1UL << {I2C_SR1_SB_Pos_H})) && timeout--) {{ if(timeout==0) return 1; }}\n"
    default_helper_functions_code += f"    {instance_name}->DR = (addr << 1) & ~0x01; // Address + W\n"
    default_helper_functions_code += f"    timeout = {instance_name}_I2C_TIMEOUT;\n"
    default_helper_functions_code += f"    while (!({instance_name}->SR1 & (1UL << {I2C_SR1_ADDR_Pos_H})) && timeout--) {{ if(timeout==0) {{ {instance_name}->CR1 |= (1UL << {I2C_CR1_STOP_Pos_H}); return 1; }} }}\n"
    default_helper_functions_code += f"    (void){instance_name}->SR1; (void){instance_name}->SR2; // Clear ADDR\n"
    default_helper_functions_code += f"    for (uint16_t i=0; i<size; i++) {{\n"
    default_helper_functions_code += f"        timeout = {instance_name}_I2C_TIMEOUT;\n"
    default_helper_functions_code += f"        while(!({instance_name}->SR1 & (1UL << {I2C_SR1_TXE_Pos_H})) && timeout--) {{ if(timeout==0) {{ {instance_name}->CR1 |= (1UL << {I2C_CR1_STOP_Pos_H}); return 1; }} }}\n"
    default_helper_functions_code += f"        {instance_name}->DR = data[i];\n    }}\n"
    default_helper_functions_code += f"    timeout = {instance_name}_I2C_TIMEOUT;\n"
    default_helper_functions_code += f"    while(!({instance_name}->SR1 & (1UL << {I2C_SR1_BTF_Pos_H})) && timeout--) {{ if(timeout==0) {{ {instance_name}->CR1 |= (1UL << {I2C_CR1_STOP_Pos_H}); return 1; }} }}\n"
    default_helper_functions_code += f"    {instance_name}->CR1 |= (1UL << {I2C_CR1_STOP_Pos_H});\n    return 0;\n}}\n"

    if params.get("generate_master_rx_func"):
        default_helper_functions_code += f"\nint {instance_name}_Master_Receive(uint8_t addr, uint8_t* data, uint16_t size) {{\n"
    default_helper_functions_code += f"    if(size==0) return 0;\n    volatile uint32_t timeout = {instance_name}_I2C_TIMEOUT;\n"
    default_helper_functions_code += f"    {instance_name}->CR1 |= (1UL << {I2C_CR1_ACK_Pos_H});\n"
    default_helper_functions_code += f"    {instance_name}->CR1 |= (1UL << {I2C_CR1_START_Pos_H});\n"
    default_helper_functions_code += f"    while (!({instance_name}->SR1 & (1UL << {I2C_SR1_SB_Pos_H})) && timeout--) {{ if(timeout==0) return 1; }}\n"
    default_helper_functions_code += f"    {instance_name}->DR = (addr << 1) | 0x01; // Address + R\n"
    default_helper_functions_code += f"    timeout = {instance_name}_I2C_TIMEOUT;\n"
    default_helper_functions_code += f"    while (!({instance_name}->SR1 & (1UL << {I2C_SR1_ADDR_Pos_H})) && timeout--) {{ if(timeout==0) {{ {instance_name}->CR1 |= (1UL << {I2C_CR1_STOP_Pos_H}); return 1; }} }}\n"
    default_helper_functions_code += f"    (void){instance_name}->SR1; (void){instance_name}->SR2; // Clear ADDR\n"
    default_helper_functions_code += f"    for(uint16_t i=0; i<size; i++) {{\n"
    default_helper_functions_code += f"        if(i == size-1) {{ {instance_name}->CR1 &= ~(1UL << {I2C_CR1_ACK_Pos_H}); {instance_name}->CR1 |= (1UL << {I2C_CR1_STOP_Pos_H}); }}\n"
    default_helper_functions_code += f"        timeout = {instance_name}_I2C_TIMEOUT;\n"
    default_helper_functions_code += f"        while(!({instance_name}->SR1 & (1UL << {I2C_SR1_RXNE_Pos_H})) && timeout--) {{ if(timeout==0) {{ {instance_name}->CR1 |= (1UL << {I2C_CR1_STOP_Pos_H}); return 1; }} }}\n"
    default_helper_functions_code += f"        data[i] = {instance_name}->DR;\n    }}\n    return 0;\n}}\n"

    return {"source_function": source_function, "init_call": init_call, "rcc_clocks_to_enable": rcc_clocks,
            "gpio_pins_to_configure_af": gpio_pins_to_configure_af,
            "default_helper_functions": default_helper_functions_code, "error_messages": error_messages}