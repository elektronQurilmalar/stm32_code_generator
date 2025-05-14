from core.mcu_defines_loader import CURRENT_MCU_DEFINES


def generate_spi_code_cmsis(config, rcc_config_calculated):
    params = config.get("params", {})
    instance_name = params.get("instance_name")
    mcu_family = params.get("mcu_family", "STM32F4")
    target_device = params.get("target_device", "STM32F407VG")

    error_messages = [];
    gpio_pins_to_configure_af = [];
    default_helper_functions_code = ""

    if not instance_name or not params.get("enabled"):
        return {"source_function": f"// {instance_name or 'SPI'} not enabled\n", "init_call": "",
                "rcc_clocks_to_enable": [], "gpio_pins_to_configure_af": [],
                "default_helper_functions": "", "error_messages": []}

    # Get peripheral info and bit positions from CURRENT_MCU_DEFINES
    spi_info_map_key = f"SPI_PERIPHERALS_INFO_{mcu_family}"
    spi_info_map = CURRENT_MCU_DEFINES.get(spi_info_map_key, CURRENT_MCU_DEFINES.get("SPI_PERIPHERALS_INFO", {}))
    instance_info = spi_info_map.get(instance_name)
    if not instance_info: error_messages.append(f"Unknown SPI instance: {instance_name}"); return {
        "error_messages": error_messages}

    # Bit positions (with fallbacks to F4 style)
    SPI_CR1_SPE_Pos = CURRENT_MCU_DEFINES.get("SPI_CR1_SPE_Pos", 6)
    SPI_CR1_MSTR_Pos = CURRENT_MCU_DEFINES.get("SPI_CR1_MSTR_Pos", 2)
    SPI_CR1_BR_Pos = CURRENT_MCU_DEFINES.get("SPI_CR1_BR_Pos", 3)
    SPI_CR1_CPHA_Pos = CURRENT_MCU_DEFINES.get("SPI_CR1_CPHA_Pos", 0)
    SPI_CR1_CPOL_Pos = CURRENT_MCU_DEFINES.get("SPI_CR1_CPOL_Pos", 1)
    SPI_CR1_LSBFIRST_Pos = CURRENT_MCU_DEFINES.get("SPI_CR1_LSBFIRST_Pos", 7)
    SPI_CR1_SSI_Pos = CURRENT_MCU_DEFINES.get("SPI_CR1_SSI_Pos", 8)
    SPI_CR1_SSM_Pos = CURRENT_MCU_DEFINES.get("SPI_CR1_SSM_Pos", 9)
    SPI_CR1_RXONLY_Pos = CURRENT_MCU_DEFINES.get("SPI_CR1_RXONLY_Pos", 10)  # For simplex RX
    SPI_CR1_DFF_Pos = CURRENT_MCU_DEFINES.get("SPI_CR1_DFF_Pos", 11)  # Data frame format (8/16 bit)
    SPI_CR1_BIDIOE_Pos = CURRENT_MCU_DEFINES.get("SPI_CR1_BIDIOE_Pos", 14)  # Bidir output enable
    SPI_CR1_BIDIMODE_Pos = CURRENT_MCU_DEFINES.get("SPI_CR1_BIDIMODE_Pos", 15)  # Bidir mode enable
    SPI_CR1_CRCEN_Pos = CURRENT_MCU_DEFINES.get("SPI_CR1_CRCEN_Pos", 13)

    SPI_CR2_SSOE_Pos = CURRENT_MCU_DEFINES.get("SPI_CR2_SSOE_Pos", 2)  # NSS output enable (HW master)
    SPI_CR2_TXEIE_Pos = CURRENT_MCU_DEFINES.get("SPI_CR2_TXEIE_Pos", 7)
    SPI_CR2_RXNEIE_Pos = CURRENT_MCU_DEFINES.get("SPI_CR2_RXNEIE_Pos", 6)
    SPI_CR2_ERRIE_Pos = CURRENT_MCU_DEFINES.get("SPI_CR2_ERRIE_Pos", 5)

    SPI_SR_RXNE_Pos = CURRENT_MCU_DEFINES.get("SPI_SR_RXNE_Pos", 0)
    SPI_SR_TXE_Pos = CURRENT_MCU_DEFINES.get("SPI_SR_TXE_Pos", 1)
    SPI_SR_BSY_Pos = CURRENT_MCU_DEFINES.get("SPI_SR_BSY_Pos", 7)

    apb_clk_freq = rcc_config_calculated.get(f"pclk{instance_info['bus'][-1]}_freq_hz", 0)  # pclk1 or pclk2
    if apb_clk_freq == 0: error_messages.append(f"APB clock for {instance_name} is 0Hz.")

    rcc_clocks = [instance_info["rcc_macro"]] if instance_info.get("rcc_macro") else []
    if not rcc_clocks: error_messages.append(f"RCC macro for {instance_name} not found.")

    source_function = f"void {instance_name}_User_Init(void) {{\n"
    source_function += f"    // {instance_name} ({mcu_family}) Configuration (CMSIS Register Level)\n"

    # Pin suggestions
    pin_sugg_map_key = f"SPI_PIN_CONFIG_SUGGESTIONS_{mcu_family}"
    pin_sugg_map_all = CURRENT_MCU_DEFINES.get(pin_sugg_map_key,
                                               CURRENT_MCU_DEFINES.get("SPI_PIN_CONFIG_SUGGESTIONS", {}))
    pin_suggestions = pin_sugg_map_all.get(target_device, {}).get(instance_name, {})
    if pin_suggestions:
        source_function += f"    // Suggested GPIO for {instance_name} on {target_device} (config in GPIO_User_Init):\n"
        for pin_type, pin_data_str in pin_suggestions.items():
            pin_options = pin_data_str.split(" or ");
            first_option = pin_options[0];
            parts = first_option.split('/')
            if len(parts) >= 1:
                port_char = parts[0][1];
                pin_num = parts[0][2:]
                af_num = -1  # Default for F1 (remap) or if not specified
                if len(parts) == 2 and parts[1].upper().startswith("AF"):
                    try:
                        af_num = int(parts[1][2:])
                    except ValueError:
                        pass
                if mcu_family == "STM32F1": af_num = -1  # Indicate remap needed for F1
                if port_char.isalpha() and pin_num.isdigit():
                    gpio_pins_to_configure_af.append((port_char, pin_num, af_num, f"{instance_name}_{pin_type}"))
                    source_function += f"    //   {pin_type}: {first_option} (AF{af_num if af_num != -1 else 'Remap'})\n"
        source_function += "\n"

    # --- CR1 Config ---
    cr1_val = 0
    spi_modes_map_key = f"SPI_MODES_{mcu_family}"
    spi_modes_map = CURRENT_MCU_DEFINES.get(spi_modes_map_key, CURRENT_MCU_DEFINES.get("SPI_MODES", {}))
    cr1_val |= (spi_modes_map.get(params.get("mode_str", "Master"), 1) << SPI_CR1_MSTR_Pos)

    spi_dirs_map_key = f"SPI_DIRECTIONS_{mcu_family}"
    spi_dirs_map = CURRENT_MCU_DEFINES.get(spi_dirs_map_key, CURRENT_MCU_DEFINES.get("SPI_DIRECTIONS", {}))
    dir_val = spi_dirs_map.get(params.get("direction_str", "2 Lines Full Duplex"), 0)
    if dir_val == 0:
        cr1_val &= ~((1 << SPI_CR1_BIDIMODE_Pos) | (1 << SPI_CR1_RXONLY_Pos))
    elif dir_val == 1:
        cr1_val |= (1 << SPI_CR1_BIDIMODE_Pos) | (1 << SPI_CR1_BIDIOE_Pos)
    elif dir_val == 2:
        cr1_val |= (1 << SPI_CR1_BIDIMODE_Pos); cr1_val &= ~(1 << SPI_CR1_BIDIOE_Pos)
    elif dir_val == 3:
        cr1_val &= ~(1 << SPI_CR1_BIDIMODE_Pos); cr1_val |= (1 << SPI_CR1_RXONLY_Pos)

    spi_data_sizes_map = CURRENT_MCU_DEFINES.get("SPI_DATA_SIZES", {})  # Usually common
    cr1_val |= (spi_data_sizes_map.get(params.get("data_size_str", "8-bit"), 0) << SPI_CR1_DFF_Pos)

    spi_cpol_map = CURRENT_MCU_DEFINES.get("SPI_CPOL", {});
    spi_cpha_map = CURRENT_MCU_DEFINES.get("SPI_CPHA", {})
    cr1_val |= (spi_cpol_map.get(params.get("cpol_str", "Low"), 0) << SPI_CR1_CPOL_Pos)
    cr1_val |= (spi_cpha_map.get(params.get("cpha_str", "1 Edge"), 0) << SPI_CR1_CPHA_Pos)

    spi_nss_modes_map_key = f"SPI_NSS_MODES_{mcu_family}"
    spi_nss_modes_map = CURRENT_MCU_DEFINES.get(spi_nss_modes_map_key, CURRENT_MCU_DEFINES.get("SPI_NSS_MODES", {}))
    nss_val = spi_nss_modes_map.get(params.get("nss_mode_str", "Software (Master/Slave)"), 0)
    if nss_val == 0:
        cr1_val |= (1 << SPI_CR1_SSM_Pos) | (1 << SPI_CR1_SSI_Pos)
    else:
        cr1_val &= ~(1 << SPI_CR1_SSM_Pos)  # HW NSS

    spi_baud_psc_map = CURRENT_MCU_DEFINES.get("SPI_BAUD_PRESCALERS", {})
    cr1_val |= (spi_baud_psc_map.get(params.get("baud_prescaler_str", "2"), 0b000) << SPI_CR1_BR_Pos)

    spi_first_bit_map = CURRENT_MCU_DEFINES.get("SPI_FIRST_BIT", {})
    cr1_val |= (spi_first_bit_map.get(params.get("first_bit_str", "MSB First"), 0) << SPI_CR1_LSBFIRST_Pos)

    crc_poly = params.get("crc_polynomial", 0)
    if crc_poly > 0:
        cr1_val |= (1 << SPI_CR1_CRCEN_Pos); source_function += f"    {instance_name}->CRCPR = {crc_poly}UL;\n"
    else:
        source_function += f"    // CRC Disabled.\n"

    source_function += f"    {instance_name}->CR1 = 0x{cr1_val:08X}UL;\n\n"

    # --- CR2 Config ---
    cr2_val = 0
    if nss_val == 1: cr2_val |= (1 << SPI_CR2_SSOE_Pos)  # HW NSS Output for Master
    if params.get("interrupt_txe", False): cr2_val |= (1 << SPI_CR2_TXEIE_Pos)
    if params.get("interrupt_rxne", False): cr2_val |= (1 << SPI_CR2_RXNEIE_Pos)
    if params.get("interrupt_err", False): cr2_val |= (1 << SPI_CR2_ERRIE_Pos)
    source_function += f"    {instance_name}->CR2 = 0x{cr2_val:08X}UL;\n\n"

    source_function += f"    {instance_name}->CR1 |= (1UL << {SPI_CR1_SPE_Pos}); // Enable SPI\n\n"
    source_function += "}\n"
    init_call = f"{instance_name}_User_Init();"

    # Helper functions (bit positions for SR are common enough for this basic version)
    if params.get("generate_tx_byte_func") or params.get("generate_rx_byte_func") or params.get(
            "generate_tx_rx_byte_func"):
        default_helper_functions_code += f"#define {instance_name}_SPI_TIMEOUT 1000\n"
        default_helper_functions_code += f"#define {instance_name}_DUMMY_BYTE 0xFF\n"
    if params.get("generate_tx_byte_func"):
        default_helper_functions_code += f"void {instance_name}_Transmit_Byte(uint8_t byte) {{\n"
        default_helper_functions_code += f"    volatile uint32_t timeout = {instance_name}_SPI_TIMEOUT;\n"
        default_helper_functions_code += f"    while (!({instance_name}->SR & (1UL << {SPI_SR_TXE_Pos})) && timeout--);\n"
        default_helper_functions_code += f"    if(timeout==0){{/*Timeout*/return;}}\n    {instance_name}->DR = byte;\n"
        default_helper_functions_code += f"    timeout = {instance_name}_SPI_TIMEOUT;\n"
        default_helper_functions_code += f"    while(({instance_name}->SR & (1UL << {SPI_SR_BSY_Pos})) && timeout--);\n    if(timeout==0){{/*Timeout BSY*/}}\n}}\n"
    if params.get("generate_rx_byte_func"):
        default_helper_functions_code += f"uint8_t {instance_name}_Receive_Byte(void) {{\n"
        default_helper_functions_code += f"    volatile uint32_t timeout = {instance_name}_SPI_TIMEOUT;\n"
        default_helper_functions_code += f"    while (!({instance_name}->SR & (1UL << {SPI_SR_TXE_Pos})) && timeout--);\n    if(timeout==0){{return {instance_name}_DUMMY_BYTE;}}\n"
        default_helper_functions_code += f"    {instance_name}->DR = {instance_name}_DUMMY_BYTE;\n    timeout = {instance_name}_SPI_TIMEOUT;\n"
        default_helper_functions_code += f"    while (!({instance_name}->SR & (1UL << {SPI_SR_RXNE_Pos})) && timeout--);\n    if(timeout==0){{return {instance_name}_DUMMY_BYTE;}}\n"
        default_helper_functions_code += f"    return (uint8_t){instance_name}->DR;\n}}\n"
    if params.get("generate_tx_rx_byte_func"):
        default_helper_functions_code += f"uint8_t {instance_name}_TransmitReceive_Byte(uint8_t tx_byte) {{\n"
        default_helper_functions_code += f"    volatile uint32_t timeout = {instance_name}_SPI_TIMEOUT;\n"
        default_helper_functions_code += f"    while (!({instance_name}->SR & (1UL << {SPI_SR_TXE_Pos})) && timeout--);\n    if(timeout==0){{return {instance_name}_DUMMY_BYTE;}}\n"
        default_helper_functions_code += f"    {instance_name}->DR = tx_byte;\n    timeout = {instance_name}_SPI_TIMEOUT;\n"
        default_helper_functions_code += f"    while (!({instance_name}->SR & (1UL << {SPI_SR_RXNE_Pos})) && timeout--);\n    if(timeout==0){{return {instance_name}_DUMMY_BYTE;}}\n"
        default_helper_functions_code += f"    return (uint8_t){instance_name}->DR;\n}}\n"

    return {"source_function": source_function, "init_call": init_call,
            "rcc_clocks_to_enable": rcc_clocks, "gpio_pins_to_configure_af": gpio_pins_to_configure_af,
            "default_helper_functions": default_helper_functions_code, "error_messages": error_messages}