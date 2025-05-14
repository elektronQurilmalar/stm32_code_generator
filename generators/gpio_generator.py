# --- MODIFIED FILE generators/gpio_generator.py ---
from core.mcu_defines_loader import CURRENT_MCU_DEFINES


def get_port_base_name(pin_id_prefix_char):
    return f"GPIO{pin_id_prefix_char.upper()}"


def generate_f1_gpio_code(port_base, pin_num, pin_cfg, error_messages, rcc_clocks_to_enable):
    c_code_pin = ""
    # Get UI strings, providing F1-style defaults if not present
    mode_str = pin_cfg.get("mode", "Input Floating")
    pull_str = pin_cfg.get("pull", "No Pull (default)")
    speed_str = pin_cfg.get("speed", "10MHz")  # Relevant for output modes for F1
    af_remap_str = pin_cfg.get("af")

    # Get F1 specific MODE and CNF bit values from defines
    f1_mode_map_ui = CURRENT_MCU_DEFINES.get("GPIO_F1_MODE_MAP_UI", {})
    f1_speed_to_mode_bits = CURRENT_MCU_DEFINES.get("GPIO_F1_SPEED_TO_MODE_BITS_MAP", {})

    mode_bits_val = 0
    cnf_bits_val = 0

    ui_mode_config = f1_mode_map_ui.get(mode_str)
    if not ui_mode_config:
        error_messages.append(f"Unknown F1 GPIO mode string '{mode_str}' for {port_base} Pin {pin_num}")
        return f"    // ERROR: Unknown F1 GPIO mode string '{mode_str}' for Pin {pin_num}\n"

    if ui_mode_config.get("IS_OUTPUT"):  # Covers "Output..." and "Alternate Function..."
        mode_bits_val = f1_speed_to_mode_bits.get(speed_str)
        if mode_bits_val is None:
            error_messages.append(
                f"Unknown F1 speed '{speed_str}' for output mode on {port_base} Pin {pin_num}. Defaulting to 10MHz.")
            mode_bits_val = CURRENT_MCU_DEFINES.get("GPIO_F1_MODE_OUTPUT_10MHZ", 0b01)  # Fallback
        cnf_bits_val = ui_mode_config.get("CNF_BASE")
    else:  # Input modes
        mode_bits_val = ui_mode_config.get("MODE")
        cnf_bits_val = ui_mode_config.get("CNF")

    if mode_bits_val is None or cnf_bits_val is None:
        error_messages.append(f"Could not determine MODE/CNF for F1 mode '{mode_str}' for {port_base} Pin {pin_num}")
        return f"    // ERROR: Could not determine MODE/CNF for F1 mode '{mode_str}' for Pin {pin_num}\n"

    config_val_4bit = (cnf_bits_val << 2) | mode_bits_val

    reg_name = "CRL" if pin_num < 8 else "CRH"
    pin_offset_in_reg = (pin_num % 8) * 4

    c_code_pin += f"    // Configure {port_base} Pin {pin_num} ({mode_str})\n"
    c_code_pin += f"    {port_base}->{reg_name} &= ~(0xFUL << {pin_offset_in_reg}); // Clear previous 4 bits for P{pin_num}\n"
    c_code_pin += f"    {port_base}->{reg_name} |= ({config_val_4bit}UL << {pin_offset_in_reg}); // MODE={mode_bits_val:02b}, CNF={cnf_bits_val:02b}\n"

    # Handle Pull-up/Pull-down for "Input Pull-up" or "Input Pull-down" modes from UI
    if mode_str == "Input Pull-up":
        # For Input Pull-up/Pull-down mode (CNF=10), ODR bit selects pull: 1=UP, 0=DOWN
        c_code_pin += f"    {port_base}->ODR |= (1UL << {pin_num}); // Enable Pull-up\n"
    elif mode_str == "Input Pull-down":
        c_code_pin += f"    {port_base}->ODR &= ~(1UL << {pin_num}); // Enable Pull-down (by clearing ODR bit)\n"

    if ui_mode_config.get("IS_AF", False) and af_remap_str:
        c_code_pin += f"    // AF/Remap Hint for Pin {pin_num}: '{af_remap_str}'. Ensure AFIO clock & AFIO_MAPR are correctly set if remap is used.\n"
        afio_rcc_macro = CURRENT_MCU_DEFINES.get("RCC_APB2ENR_AFIOEN")  # From F1 defines
        if afio_rcc_macro and afio_rcc_macro not in rcc_clocks_to_enable:
            rcc_clocks_to_enable.append(afio_rcc_macro)

    return c_code_pin


def generate_f2_f4_gpio_code(port_base, pin_num, pin_cfg, error_messages):
    c_code_pin = ""
    mode_str = pin_cfg.get("mode", "Input")
    pull_str = pin_cfg.get("pull", "No Pull-up/Pull-down")
    speed_str = pin_cfg.get("speed", "Low")
    af_val_str = pin_cfg.get("af")

    MODE_INPUT = CURRENT_MCU_DEFINES.get("GPIO_MODE_INPUT_VAL", 0b00)
    MODE_OUTPUT = CURRENT_MCU_DEFINES.get("GPIO_MODE_OUTPUT_VAL", 0b01)
    MODE_AF = CURRENT_MCU_DEFINES.get("GPIO_MODE_AF_VAL", 0b10)
    MODE_ANALOG = CURRENT_MCU_DEFINES.get("GPIO_MODE_ANALOG_VAL", 0b11)
    OTYPE_PP = CURRENT_MCU_DEFINES.get("GPIO_OTYPE_PP_VAL", 0)
    OTYPE_OD = CURRENT_MCU_DEFINES.get("GPIO_OTYPE_OD_VAL", 1)
    SPEED_MAP = CURRENT_MCU_DEFINES.get("GPIO_OSPEED_MAP", {"Low": 0b00, "Medium": 0b01, "Fast": 0b10, "High": 0b11})
    PUPD_MAP = CURRENT_MCU_DEFINES.get("GPIO_PUPD_MAP",
                                       {"No Pull-up/Pull-down": 0b00, "Pull-up": 0b01, "Pull-down": 0b10})

    moder_val_bits = 0
    otyper_val_bit = -1

    if mode_str == "Input":
        moder_val_bits = MODE_INPUT
    elif mode_str == "Output PP":
        moder_val_bits = MODE_OUTPUT; otyper_val_bit = OTYPE_PP
    elif mode_str == "Output OD":
        moder_val_bits = MODE_OUTPUT; otyper_val_bit = OTYPE_OD
    elif mode_str == "Analog":
        moder_val_bits = MODE_ANALOG
    elif mode_str == "Alternate Function PP":
        moder_val_bits = MODE_AF; otyper_val_bit = OTYPE_PP
    elif mode_str == "Alternate Function OD":
        moder_val_bits = MODE_AF; otyper_val_bit = OTYPE_OD
    else:
        error_messages.append(f"Unknown F2/F4 mode '{mode_str}' for {port_base} Pin {pin_num}")
        return f"    // ERROR: Unknown F2/F4 mode '{mode_str}' for Pin {pin_num}\n"

    c_code_pin += f"    // Configure {port_base} Pin {pin_num} ({mode_str})\n"
    c_code_pin += f"    {port_base}->MODER &= ~(0x3UL << ({pin_num} * 2));\n"
    c_code_pin += f"    {port_base}->MODER |= ({moder_val_bits}UL << ({pin_num} * 2));\n"

    if otyper_val_bit != -1:
        if otyper_val_bit == OTYPE_OD:
            c_code_pin += f"    {port_base}->OTYPER |= (1UL << {pin_num}); // Open-Drain\n"
        else:
            c_code_pin += f"    {port_base}->OTYPER &= ~(1UL << {pin_num}); // Push-Pull\n"

    is_output_or_af = "Output" in mode_str or "Alternate Function" in mode_str
    if is_output_or_af and mode_str != "Analog" and speed_str:
        ospeedr_val = SPEED_MAP.get(speed_str)
        if ospeedr_val is not None:
            c_code_pin += f"    {port_base}->OSPEEDR &= ~(0x3UL << ({pin_num} * 2));\n"
            c_code_pin += f"    {port_base}->OSPEEDR |= ({ospeedr_val}UL << ({pin_num} * 2)); // Speed: {speed_str}\n"
        else:
            error_messages.append(f"Unknown speed '{speed_str}' for {port_base} Pin {pin_num}")

    if mode_str != "Analog":
        pupdr_val = PUPD_MAP.get(pull_str)
        if pupdr_val is not None:
            c_code_pin += f"    {port_base}->PUPDR &= ~(0x3UL << ({pin_num} * 2));\n"
            c_code_pin += f"    {port_base}->PUPDR |= ({pupdr_val}UL << ({pin_num} * 2)); // Pull: {pull_str}\n"
        else:
            error_messages.append(f"Unknown pull setting '{pull_str}' for {port_base} Pin {pin_num}")

    if "Alternate Function" in mode_str and af_val_str:
        af_num = -1
        if af_val_str.upper().startswith("AF"):
            try:
                af_num = int(af_val_str[2:])
            except ValueError:
                error_messages.append(f"Cannot parse AF num: '{af_val_str}' for {port_base} Pin {pin_num}")
        else:
            try:
                af_num = int(af_val_str)
            except ValueError:
                error_messages.append(f"AF value '{af_val_str}' not 'AFx' or int for {port_base} Pin {pin_num}")

        if 0 <= af_num <= 15:
            af_reg_idx = 0 if pin_num < 8 else 1
            pin_in_reg = pin_num % 8
            af_reg_name = f"AFR[{af_reg_idx}]"  # F2/F4 use AFR[0] and AFR[1]
            c_code_pin += f"    {port_base}->{af_reg_name} &= ~(0xFUL << ({pin_in_reg} * 4));\n"
            c_code_pin += f"    {port_base}->{af_reg_name} |= ({af_num}UL << ({pin_in_reg} * 4)); // AF{af_num}\n"
        elif af_num != -1:
            error_messages.append(f"Invalid AF num {af_num} for F2/F4 {port_base} Pin {pin_num} (must be 0-15).")
    return c_code_pin


def generate_gpio_code(config):
    pins_config = config.get("pins", {})
    mcu_family = config.get("mcu_family", "STM32F4")
    error_messages = []
    rcc_clocks_to_enable = []

    if not pins_config:
        return {"source_function": "// No GPIOs configured\n", "init_call": "",
                "rcc_clocks_to_enable": [], "error_messages": []}

    # Get family specific GPIO RCC macros if defined
    # For F1, this map is in stm32f1_defines.py (e.g., RCC_APB2ENR_IOPAEN)
    # For F2/F4, it's in stm32f4_defines.py (e.g., RCC_AHB1ENR_GPIOAEN)
    gpio_rcc_enable_map_key = f"GPIO_RCC_ENABLE_MAP_{mcu_family}"
    gpio_rcc_enable_map = CURRENT_MCU_DEFINES.get(gpio_rcc_enable_map_key,
                                                  CURRENT_MCU_DEFINES.get("GPIO_RCC_ENABLE_MAP", {}))

    ports_to_enable_chars = set()
    for pin_id in pins_config.keys():
        if not pin_id or len(pin_id) < 2:
            error_messages.append(f"Invalid pin_id: {pin_id}");
            continue
        port_char = pin_id[0].upper()

        max_port_char_cfg_key = f"GPIO_MAX_PORT_CHAR_{mcu_family}"
        default_max_char = 'K' if mcu_family == "STM32F4" else \
            ('I' if mcu_family == "STM32F2" else \
                 CURRENT_MCU_DEFINES.get("GPIO_MAX_PORT_CHAR_F1", 'G'))  # Use specific define for F1

        max_port_char_ord = ord(CURRENT_MCU_DEFINES.get(max_port_char_cfg_key, default_max_char))

        if 'A' <= port_char <= chr(max_port_char_ord):
            ports_to_enable_chars.add(port_char)
        else:
            error_messages.append(f"Invalid port char '{port_char}' in pin_id: {pin_id} for family {mcu_family}")

    for port_char_to_enable in sorted(list(ports_to_enable_chars)):
        # The key in gpio_rcc_enable_map should just be the port character 'A', 'B', etc.
        rcc_macro_port = gpio_rcc_enable_map.get(port_char_to_enable)
        if rcc_macro_port:
            if rcc_macro_port not in rcc_clocks_to_enable:
                rcc_clocks_to_enable.append(rcc_macro_port)
        else:  # Fallback construction if map is incomplete or uses different keys
            if mcu_family == "STM32F1":
                # For F1, port clocks are on APB2
                rcc_macro_port_fallback = f"RCC_APB2ENR_IOP{port_char_to_enable}EN"
            else:  # F2/F4 are on AHB1
                rcc_macro_port_fallback = f"RCC_AHB1ENR_GPIO{port_char_to_enable}EN"

            # Check if this constructed macro exists in defines
            if CURRENT_MCU_DEFINES.get(rcc_macro_port_fallback + "_Pos") is not None or \
                    CURRENT_MCU_DEFINES.get(rcc_macro_port_fallback) is not None:
                if rcc_macro_port_fallback not in rcc_clocks_to_enable:
                    rcc_clocks_to_enable.append(rcc_macro_port_fallback)
            else:
                error_messages.append(f"RCC macro for GPIO{port_char_to_enable} not found or defined for {mcu_family}.")

    c_code_func = "void GPIO_User_Init(void) {\n"
    c_code_func += f"    // GPIO Configuration ({mcu_family} - CMSIS Register Level)\n\n"

    if rcc_clocks_to_enable:
        rcc_comment_lines = ["    // Ensure GPIO Clocks are enabled (typically in RCC Init):"]

        # Group by actual register name for comments
        reg_to_macros = {}
        for macro in rcc_clocks_to_enable:
            reg = ""
            if "AHB1ENR" in macro:
                reg = "AHB1ENR"
            elif "AHBENR" in macro:
                reg = "AHBENR"  # F1
            elif "APB2ENR" in macro:
                reg = "APB2ENR"  # F1 AFIO
            # Add more if other buses are used for GPIO/AFIO clocks in some families

            if reg:
                if reg not in reg_to_macros: reg_to_macros[reg] = []
                reg_to_macros[reg].append(macro)
            else:  # Fallback if register couldn't be determined from macro name
                rcc_comment_lines.append(f"    // Unknown register for {macro}")

        for reg, macros_for_reg in reg_to_macros.items():
            if macros_for_reg:
                rcc_comment_lines.append(f"    // RCC->{reg} |= ({' | '.join(macros_for_reg)});")

        c_code_func += "\n".join(rcc_comment_lines) + "\n\n"

    # Sort pins by Port (A, B, C...) then by Pin Number (0, 1, 2...)
    sorted_pin_ids = sorted(pins_config.keys(), key=lambda pin_id_sort: (pin_id_sort[0], int(pin_id_sort[1:])))

    for pin_id in sorted_pin_ids:
        pin_cfg = pins_config[pin_id]
        if not pin_id or len(pin_id) < 2: continue  # Already checked but good to be safe
        port_char_raw = pin_id[0]
        port_base = get_port_base_name(port_char_raw)
        pin_num_str = pin_id[1:]
        try:
            pin_num = int(pin_num_str)
        except ValueError:
            error_messages.append(f"Invalid pin num in ID: {pin_id}");
            continue
        if not (0 <= pin_num <= 15):
            error_messages.append(f"Pin num out of range: {pin_id}");
            continue

        pin_code_segment = ""
        if mcu_family == "STM32F1":
            pin_code_segment = generate_f1_gpio_code(port_base, pin_num, pin_cfg, error_messages, rcc_clocks_to_enable)
        elif mcu_family in ["STM32F2", "STM32F4"]:
            pin_code_segment = generate_f2_f4_gpio_code(port_base, pin_num, pin_cfg, error_messages)
        else:
            error_messages.append(f"GPIO generation not implemented for family {mcu_family}")
            pin_code_segment = f"    // GPIO for {pin_id} - Family {mcu_family} not implemented\n"

        c_code_func += pin_code_segment  # Already includes newline from helper
        if not pin_code_segment.endswith("\n"):  # Ensure newline if helper didn't add one
            c_code_func += "\n"

    c_code_func += "}\n"

    return {"source_function": c_code_func,
            "init_call": "GPIO_User_Init();" if pins_config else "",
            "rcc_clocks_to_enable": list(set(rcc_clocks_to_enable)),
            "error_messages": error_messages}