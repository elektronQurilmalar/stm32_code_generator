# --- MODIFIED FILE generators/timer_generator.py ---

from core.mcu_defines_loader import CURRENT_MCU_DEFINES


def generate_timer_code_cmsis(config, rcc_config_calculated):
    params = config.get("params", {})
    instance_name = params.get("instance_name")
    mcu_family = params.get("mcu_family", "STM32F4")
    target_device = params.get("target_device", "STM32F407VG")

    error_messages = []
    gpio_pins_to_configure_af = [] # For OC/IC channels

    if not instance_name or not params.get("enabled"):
        return {"source_function": f"// {instance_name or 'Timer'} not enabled\n", "init_call": "",
                "rcc_clocks_to_enable": [], "gpio_pins_to_configure_af": [], "error_messages": []}

    # Get peripheral info and bit positions from CURRENT_MCU_DEFINES
    timer_info_map_key = f"TIMER_PERIPHERALS_INFO_{mcu_family}"
    timer_info_map = CURRENT_MCU_DEFINES.get(timer_info_map_key, CURRENT_MCU_DEFINES.get("TIMER_PERIPHERALS_INFO", {}))
    instance_info = timer_info_map.get(instance_name)
    if not instance_info:
        error_messages.append(f"Unknown Timer: {instance_name}")
        return {"error_messages": error_messages, "source_function": f"// Error: Unknown Timer {instance_name}\n", "init_call": ""}

    # Common CR1 bits
    TIM_CR1_CEN_Pos = CURRENT_MCU_DEFINES.get("TIM_CR1_CEN_Pos", 0);
    TIM_CR1_CEN = (1 << TIM_CR1_CEN_Pos)
    TIM_CR1_URS_Pos = CURRENT_MCU_DEFINES.get("TIM_CR1_URS_Pos", 2)
    TIM_CR1_URS = (1 << TIM_CR1_URS_Pos)
    TIM_CR1_OPM_Pos = CURRENT_MCU_DEFINES.get("TIM_CR1_OPM_Pos", 3)
    TIM_CR1_OPM = (1 << TIM_CR1_OPM_Pos)
    TIM_CR1_DIR_Pos = CURRENT_MCU_DEFINES.get("TIM_CR1_DIR_Pos", 4);
    TIM_CR1_DIR = (1 << TIM_CR1_DIR_Pos)
    TIM_CR1_CMS_Pos = CURRENT_MCU_DEFINES.get("TIM_CR1_CMS_Pos", 5)
    TIM_CR1_ARPE_Pos = CURRENT_MCU_DEFINES.get("TIM_CR1_ARPE_Pos", 7);
    TIM_CR1_ARPE = (1 << TIM_CR1_ARPE_Pos)
    TIM_CR1_CKD_Pos = CURRENT_MCU_DEFINES.get("TIM_CR1_CKD_Pos", 8)
    # DIER bits
    TIM_DIER_UIE_Pos = CURRENT_MCU_DEFINES.get("TIM_DIER_UIE_Pos", 0);
    TIM_DIER_UIE = (1 << TIM_DIER_UIE_Pos)
    TIM_DIER_CC1IE_Pos = CURRENT_MCU_DEFINES.get("TIM_DIER_CC1IE_Pos", 1); TIM_DIER_CC1IE = (1 << TIM_DIER_CC1IE_Pos)
    TIM_DIER_CC2IE_Pos = CURRENT_MCU_DEFINES.get("TIM_DIER_CC2IE_Pos", 2); TIM_DIER_CC2IE = (1 << TIM_DIER_CC2IE_Pos)
    TIM_DIER_CC3IE_Pos = CURRENT_MCU_DEFINES.get("TIM_DIER_CC3IE_Pos", 3); TIM_DIER_CC3IE = (1 << TIM_DIER_CC3IE_Pos)
    TIM_DIER_CC4IE_Pos = CURRENT_MCU_DEFINES.get("TIM_DIER_CC4IE_Pos", 4); TIM_DIER_CC4IE = (1 << TIM_DIER_CC4IE_Pos)

    # EGR bits
    TIM_EGR_UG_Pos = CURRENT_MCU_DEFINES.get("TIM_EGR_UG_Pos", 0);
    TIM_EGR_UG = (1 << TIM_EGR_UG_Pos)
    # CCMRx bits (generic positions, actual register CCMR1/2 depends on channel)
    TIM_CCMRx_OCxM_Pos = CURRENT_MCU_DEFINES.get("TIM_CCMRx_OCxM_Pos", 4)
    TIM_CCMRx_OCxPE_Pos = CURRENT_MCU_DEFINES.get("TIM_CCMRx_OCxPE_Pos", 3)
    TIM_CCMRx_CCxS_Pos = CURRENT_MCU_DEFINES.get("TIM_CCMRx_CCxS_Pos", 0)
    TIM_CCMRx_ICxPSC_Pos = CURRENT_MCU_DEFINES.get("TIM_CCMRx_ICxPSC_Pos", 2)
    TIM_CCMRx_ICxF_Pos = CURRENT_MCU_DEFINES.get("TIM_CCMRx_ICxF_Pos", 4)
    # CCER bits
    TIM_CCER_CC1E_Pos = CURRENT_MCU_DEFINES.get("TIM_CCER_CC1E_Pos", 0); TIM_CCER_CC1E = (1 << TIM_CCER_CC1E_Pos) # Example for CH1
    TIM_CCER_CC1P_Pos = CURRENT_MCU_DEFINES.get("TIM_CCER_CC1P_Pos", 1); TIM_CCER_CC1P = (1 << TIM_CCER_CC1P_Pos) # Example for CH1

    # BDTR (Advanced timers)
    TIM_BDTR_MOE_Pos = CURRENT_MCU_DEFINES.get("TIM_BDTR_MOE_Pos", 15);
    TIM_BDTR_MOE = (1 << TIM_BDTR_MOE_Pos)
    # SMCR
    TIM_SMCR_ECE_Pos = CURRENT_MCU_DEFINES.get("TIM_SMCR_ECE_Pos", 14);
    TIM_SMCR_ECE = (1 << TIM_SMCR_ECE_Pos)
    TIM_SMCR_SMS_Pos = CURRENT_MCU_DEFINES.get("TIM_SMCR_SMS_Pos", 0)
    TIM_SMCR_TS_Pos = CURRENT_MCU_DEFINES.get("TIM_SMCR_TS_Pos", 4)

    timer_type_from_config = params.get("timer_type", "GP16") # Get from config if available
    timer_bus = instance_info.get("bus", "APB1")
    rcc_clocks = [instance_info["rcc_macro"]] if instance_info.get("rcc_macro") else []
    if not rcc_clocks: error_messages.append(f"RCC macro for {instance_name} not found.")

    pclk_freq = rcc_config_calculated.get(f"pclk{timer_bus[-1]}_freq_hz", 0)
    apb_div = rcc_config_calculated.get(f"apb{timer_bus[-1]}_div", 1)
    tim_kernel_clk = pclk_freq if apb_div == 1 else pclk_freq * 2
    if pclk_freq == 0: error_messages.append(f"PCLK for {instance_name} ({timer_bus}) is 0Hz.")

    source_function = f"void {instance_name}_User_Init(void) {{\n"
    source_function += f"    // {instance_name} ({timer_type_from_config}, {mcu_family}) Init (CMSIS Register Level)\n"
    source_function += f"    // Timer Kernel Clock (approx): {tim_kernel_clk / 1e6:.2f} MHz\n\n"

    cr1_val = 0
    source_function += f"    {instance_name}->PSC = {params.get('prescaler', 0)}UL; // Prescaler\n"
    source_function += f"    {instance_name}->ARR = {params.get('period', 65535)}UL; // Auto-Reload Register\n"

    counter_modes_map_key = f"TIM_COUNTER_MODES_{mcu_family}"
    counter_modes_map = CURRENT_MCU_DEFINES.get(counter_modes_map_key, CURRENT_MCU_DEFINES.get("TIM_COUNTER_MODES", {}))
    cr1_val |= counter_modes_map.get(params.get("counter_mode", "Up"), 0)

    if params.get("auto_reload_preload", True): cr1_val |= TIM_CR1_ARPE

    clk_div_map_key = f"TIM_CLOCK_DIVISION_{mcu_family}"
    clk_div_map = CURRENT_MCU_DEFINES.get(clk_div_map_key, CURRENT_MCU_DEFINES.get("TIM_CLOCK_DIVISION", {}))
    cr1_val |= (clk_div_map.get(params.get("clock_division", "1"), 0) << TIM_CR1_CKD_Pos)
    source_function += f"    {instance_name}->CR1 = 0x{cr1_val:08X}UL;\n\n"

    smcr_val = 0
    clk_src_str = params.get("clock_source", CURRENT_MCU_DEFINES.get("TIM_INTERNAL_CLOCK_SOURCE", "Internal Clock (CK_INT)"))
    etr_modes_map_key = f"TIM_ETR_MODES_{mcu_family}"
    etr_modes_map = CURRENT_MCU_DEFINES.get(etr_modes_map_key, CURRENT_MCU_DEFINES.get("TIM_ETR_MODES", {}))

    if clk_src_str == etr_modes_map.get("ETR - Mode 2 (via ECE, no prescaler/filter on ETR path)"):
        smcr_val |= TIM_SMCR_ECE
    elif clk_src_str == etr_modes_map.get("ETR - Mode 1 (via ETRF, prescaled, filtered)"):
        smcr_val |= (0b111 << TIM_SMCR_SMS_Pos)  # External Clock Mode 1
        smcr_val |= (0b111 << TIM_SMCR_TS_Pos)   # Trigger selection: ETRF
        # Note: ETRP (prescaler) and ETF (filter) for ETR are in SMCR too, if needed.
        # ETRP: SMCR[15], ETF: SMCR[11:8]
        # Default for this simple case is no prescaler/filter on ETRF path itself.
    # Add more slave mode controller configurations here (Encoder, TIxFPx etc.) if supported by UI

    if smcr_val != 0:
        source_function += f"    {instance_name}->SMCR = 0x{smcr_val:08X}UL;\n\n"

    ccer_val = 0
    # Initialize CCMR registers to 0 or read current if appending
    # For simplicity, we assume fresh configuration here.
    ccmr1_val = 0
    ccmr2_val = 0

    for ch_cfg in params.get("channels", []):
        if not ch_cfg.get("enabled"): continue
        ch_num = ch_cfg.get("channel_number")
        ccmr_reg_idx = (ch_num - 1) // 2  # 0 for CCMR1 (Ch1,2), 1 for CCMR2 (Ch3,4)
        ccmr_half_idx = (ch_num - 1) % 2  # 0 for Ch1/3 (lower bits), 1 for Ch2/4 (upper bits)
        ccmr_shift = ccmr_half_idx * 8     # Shift by 8 for Ch2/4 in CCMR1/2

        ccmr_val_ch_bits = 0  # Bits for this specific channel within its CCMRx half

        if ch_cfg.get("mode") == "Output Compare":
            oc = ch_cfg.get("output_compare", {})
            oc_modes_map_key = f"TIM_OC_MODES_{mcu_family}"
            oc_modes_map = CURRENT_MCU_DEFINES.get(oc_modes_map_key, CURRENT_MCU_DEFINES.get("TIM_OC_MODES", {}))
            ccmr_val_ch_bits |= (oc_modes_map.get(oc.get("oc_mode", "Frozen"), 0) << TIM_CCMRx_OCxM_Pos)
            if oc.get("preload_enable", True): ccmr_val_ch_bits |= (1 << TIM_CCMRx_OCxPE_Pos)

            source_function += f"    {instance_name}->CCR{ch_num} = {oc.get('pulse', 0)}UL; // Channel {ch_num} Pulse\n"

            oc_pol_map_key = f"TIM_OC_POLARITY_{mcu_family}"
            oc_pol_map = CURRENT_MCU_DEFINES.get(oc_pol_map_key, CURRENT_MCU_DEFINES.get("TIM_OC_POLARITY", {}))
            if oc_pol_map.get(oc.get("polarity", "High (non-inverted)"), 0) == 1: # Low (inverted)
                ccer_val |= (1 << (TIM_CCER_CC1P_Pos + (ch_num - 1) * 4))  # CCxP bit

            ccer_val |= (1 << (TIM_CCER_CC1E_Pos + (ch_num - 1) * 4))  # CCxE bit

            # GPIO AF message (needs more detail about specific pins)
            gpio_pins_to_configure_af.append(f"{instance_name}_CH{ch_num}_OC") # Placeholder string for now
            source_function += f"    // Configure GPIO for {instance_name} Channel {ch_num} Output Compare AF\n"

        elif ch_cfg.get("mode") == "Input Capture":
            ic = ch_cfg.get("input_capture", {})
            ic_sel_map_key = f"TIM_IC_SELECTION_{mcu_family}"
            ic_sel_map = CURRENT_MCU_DEFINES.get(ic_sel_map_key, CURRENT_MCU_DEFINES.get("TIM_IC_SELECTION", {}))
            ccmr_val_ch_bits |= (ic_sel_map.get(ic.get("selection", "Direct (TIx)"), 0b01) << TIM_CCMRx_CCxS_Pos)

            ic_psc_map_key = f"TIM_IC_PRESCALER_{mcu_family}"
            ic_psc_map = CURRENT_MCU_DEFINES.get(ic_psc_map_key, CURRENT_MCU_DEFINES.get("TIM_IC_PRESCALER", {}))
            ccmr_val_ch_bits |= (ic_psc_map.get(ic.get("prescaler", "1 (every event)"), 0) << TIM_CCMRx_ICxPSC_Pos)

            ccmr_val_ch_bits |= ((ic.get("filter", 0) & 0xF) << TIM_CCMRx_ICxF_Pos)

            ic_pol_map_key = f"TIM_IC_POLARITY_{mcu_family}"
            ic_pol_map = CURRENT_MCU_DEFINES.get(ic_pol_map_key, CURRENT_MCU_DEFINES.get("TIM_IC_POLARITY", {}))
            pol_bits = ic_pol_map.get(ic.get("polarity", "Rising Edge"), 0b00)

            # CCER polarity bits for input capture (CCxP and CCxNP)
            # Polarity: 00=Rising, 01=Falling, 11=Both
            # CCxP (bit 1) set for falling edge.
            # CCxNP (bit 3) set for ??? (F4 uses it for Both, where CCxP also means falling)
            # This part is tricky and depends on specific MCU family's interpretation of CCxP/CCxNP for IC.
            # Simplified:
            if pol_bits & 0b01: # If falling edge is involved (Falling or Both)
                ccer_val |= (1 << (TIM_CCER_CC1P_Pos + (ch_num - 1) * 4)) # CCxP
            # For "Both Edges", some families might need CCxNP too. F4 uses CCxP=1, CCxNP=1. F1 doesn't have CCxNP.
            # Let's assume for now:
            # TIM_IC_POLARITY maps directly to combined value for CCxP and CCxNP if applicable
            # For F4, 'Both Edges' -> 0b11, so this would set CCxP and CCxNP (if CCxNP is at offset +2 from CCxP)
            # This is a simplification. Real mapping is more complex.
            # Example if CCxNP is always bit 3 of the 4-bit field:
            if pol_bits == 0b11 and mcu_family in ["STM32F4", "STM32F2"]: # "Both Edges" needs CCxNP for some families
                 ccer_val |= (1 << ( (TIM_CCER_CC1P_Pos + 2) + (ch_num-1) * 4)) # Assuming CCxNP is CCxP_Pos + 2

            ccer_val |= (1 << (TIM_CCER_CC1E_Pos + (ch_num - 1) * 4))  # CCxE bit

            gpio_pins_to_configure_af.append(f"{instance_name}_CH{ch_num}_IC") # Placeholder
            source_function += f"    // Configure GPIO for {instance_name} Channel {ch_num} Input Capture AF\n"

        # Apply ccmr_val_ch_bits to the correct CCMR register
        if ccmr_reg_idx == 0: # CCMR1
            ccmr1_val |= (ccmr_val_ch_bits << ccmr_shift)
        else: # CCMR2
            ccmr2_val |= (ccmr_val_ch_bits << ccmr_shift)

    if any(ch.get("enabled") for ch in params.get("channels", [])): # Only write if channels were configured
        if instance_info.get("max_channels", 0) >= 1:
            source_function += f"    {instance_name}->CCMR1 = 0x{ccmr1_val:08X}UL;\n"
        if instance_info.get("max_channels", 0) >= 3: # Only if CCMR2 exists
            source_function += f"    {instance_name}->CCMR2 = 0x{ccmr2_val:08X}UL;\n"
        source_function += "\n"

    if ccer_val != 0:
        source_function += f"    {instance_name}->CCER = 0x{ccer_val:08X}UL;\n\n"

    dier_val = 0
    if params.get("update_interrupt_enable", False): dier_val |= TIM_DIER_UIE
    # Add CCxIE interrupt enables if configured in UI (not currently in TimerChannelConfigWidget)
    # Example for CH1 IE:
    # if ch1_interrupt_enabled: dier_val |= TIM_DIER_CC1IE;

    if dier_val != 0:
        source_function += f"    {instance_name}->DIER = 0x{dier_val:08X}UL;\n\n"

    if params.get("has_bdtr", False): # From config params, not just instance_info
        bdtr_val = 0
        if params.get("main_output_enable", False): bdtr_val |= TIM_BDTR_MOE
        # Only write BDTR if it's an advanced timer or if MOE is explicitly set (safety)
        if bdtr_val != 0 or instance_info.get("type") == "ADV":
            source_function += f"    {instance_name}->BDTR = 0x{bdtr_val:08X}UL;\n\n"

    source_function += f"    {instance_name}->EGR = TIM_EGR_UG; // Generate an update event to re-initialize the counter and prescaler\n"
    source_function += f"    {instance_name}->CR1 |= TIM_CR1_CEN; // Enable Timer\n\n"
    source_function += "}\n"
    init_call = f"{instance_name}_User_Init();"

    return {"source_function": source_function, "init_call": init_call,
            "rcc_clocks_to_enable": rcc_clocks,
            "gpio_pins_to_configure_af": gpio_pins_to_configure_af,
            "error_messages": error_messages}