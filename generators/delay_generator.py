from core.mcu_defines_loader import CURRENT_MCU_DEFINES


def generate_delay_code_cmsis(config, rcc_config_calculated):
    params = config.get("params", {})
    mcu_family = params.get("mcu_family", "STM32F4")
    target_device = params.get("target_device", "STM32F407VG")

    source_function_blocks = []
    init_calls = []
    rcc_clocks_to_enable = []
    error_messages = []
    default_helper_functions_code = ""

    gen_ms = params.get("generate_ms_delay", False)
    gen_us = params.get("generate_us_delay", False)
    delay_source = params.get("delay_source", "SysTick")

    if not (gen_ms or gen_us):
        return {"source_function": "// No Delay functions selected\n", "init_call": "",
                "rcc_clocks_to_enable": [], "default_helper_functions": "", "error_messages": []}

    # Get bit positions and constants from CURRENT_MCU_DEFINES
    DWT_CTRL_CYCCNTENA_Pos = CURRENT_MCU_DEFINES.get("DWT_CTRL_CYCCNTENA_Pos", 0)
    DWT_CTRL_CYCCNTENA = (1 << DWT_CTRL_CYCCNTENA_Pos)
    CoreDebug_DEMCR_TRCENA_Pos = CURRENT_MCU_DEFINES.get("CoreDebug_DEMCR_TRCENA_Pos", 24)
    CoreDebug_DEMCR_TRCENA = (1 << CoreDebug_DEMCR_TRCENA_Pos)
    TIM_CR1_CEN_Pos = CURRENT_MCU_DEFINES.get("TIM_CR1_CEN_Pos", 0);
    TIM_CR1_CEN = (1 << TIM_CR1_CEN_Pos)  # From F4 defines
    TIM_CR1_URS_Pos = CURRENT_MCU_DEFINES.get("TIM_CR1_URS_Pos", 2);
    TIM_CR1_URS = (1 << TIM_CR1_URS_Pos)
    TIM_EGR_UG_Pos = CURRENT_MCU_DEFINES.get("TIM_EGR_UG_Pos", 0);
    TIM_EGR_UG = (1 << TIM_EGR_UG_Pos)

    if delay_source == "SysTick":
        hclk_freq = rcc_config_calculated.get("hclk_freq_hz")
        if not hclk_freq:
            error_messages.append("SysTick delay: HCLK freq from RCC needed.")
        else:
            if gen_us:  # Rough SysTick based us delay
                default_helper_functions_code += f"\n// SysTick based microsecond delay (approximate)\n"
                default_helper_functions_code += f"void SysTick_Delay_us(uint32_t us) {{\n"
                default_helper_functions_code += f"    if (us == 0) return;\n"
                default_helper_functions_code += f"    uint32_t ticks_per_us = {hclk_freq} / 1000000UL; // HCLK cycles per us\n"
                default_helper_functions_code += f"    uint32_t num_loop_iterations = us * ticks_per_us / 4; // Adjust divisor by calibration\n"
                default_helper_functions_code += f"    if (num_loop_iterations == 0) num_loop_iterations = 1;\n"
                default_helper_functions_code += f"    for (volatile uint32_t i = 0; i < num_loop_iterations; ++i) {{ __NOP(); }}\n}}\n"
            if gen_ms:  # Standard SysTick ms delay
                default_helper_functions_code += "\n// SysTick based millisecond delay (blocking)\n"
                default_helper_functions_code += "volatile uint32_t g_ms_ticks_delay = 0;\n"  # Unique name
                default_helper_functions_code += "void SysTick_Handler_ForDelay(void) { g_ms_ticks_delay++; }\n"
                default_helper_functions_code += "void SysTick_Delay_ms(uint32_t ms) {\n"
                default_helper_functions_code += "    uint32_t start_ticks = g_ms_ticks_delay;\n"
                default_helper_functions_code += "    while ((g_ms_ticks_delay - start_ticks) < ms); \n}\n"
                default_helper_functions_code += "// NOTE: Call SysTick_Config(SystemCoreClock / 1000) in main.\n"
                default_helper_functions_code += "// Ensure SysTick_Handler calls SysTick_Handler_ForDelay().\n"

    elif delay_source == "DWT Cycle Counter":
        sysclk_freq = rcc_config_calculated.get("sysclk_freq_hz")
        if not sysclk_freq:
            error_messages.append("DWT delay: SystemCoreClock (SYSCLK) freq needed.")
        elif gen_us:
            dwt_init_func = "void DWT_Delay_Init(void) {\n"
            dwt_init_func += f"    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA;\n"
            dwt_init_func += f"    DWT->CYCCNT = 0;\n"  # Reset counter first
            dwt_init_func += f"    DWT->CTRL |= DWT_CTRL_CYCCNTENA;\n}}\n"
            source_function_blocks.append(dwt_init_func);
            init_calls.append("DWT_Delay_Init();")
            default_helper_functions_code += "\n// DWT Cycle Counter based microsecond delay (blocking)\n"
            default_helper_functions_code += "void DWT_Delay_us(uint32_t us) {\n"
            default_helper_functions_code += f"    uint32_t ticks_per_us = {sysclk_freq} / 1000000UL;\n"
            default_helper_functions_code += f"    uint32_t start_cyccnt = DWT->CYCCNT;\n"
            default_helper_functions_code += f"    uint32_t wait_cyccnt = us * ticks_per_us;\n"
            default_helper_functions_code += f"    while ((DWT->CYCCNT - start_cyccnt) < wait_cyccnt);\n}}\n"
        if gen_ms: error_messages.append("DWT typically for us delays. Select another source for ms.")

    elif delay_source == "TIMx (General Purpose Timer)":
        timer_instance = params.get("delay_timer_instance")
        timer_info_map_key = f"TIMER_PERIPHERALS_INFO_{mcu_family}"
        timer_info_map = CURRENT_MCU_DEFINES.get(timer_info_map_key,
                                                 CURRENT_MCU_DEFINES.get("TIMER_PERIPHERALS_INFO", {}))
        timer_info = timer_info_map.get(timer_instance, {}) if timer_instance else {}

        if not timer_instance or not timer_info:
            error_messages.append("TIMx delay: Valid timer instance needed.")
        else:
            rcc_clocks_to_enable.append(timer_info["rcc_macro"])
            timer_apb_bus = timer_info.get("bus", "APB1")
            pclk_key = "pclk1_freq_hz" if timer_apb_bus == "APB1" else "pclk2_freq_hz"
            apb_div_key = "apb1_div" if timer_apb_bus == "APB1" else "apb2_div"
            apb_clk = rcc_config_calculated.get(pclk_key, 0)
            apb_div = rcc_config_calculated.get(apb_div_key, 1)
            timer_kernel_clk = apb_clk if apb_div == 1 else apb_clk * 2

            if timer_kernel_clk == 0:
                error_messages.append(f"Kernel clock for {timer_instance} is 0Hz.")
            else:
                psc_us = (timer_kernel_clk / 1000000) - 1
                if psc_us < 0: psc_us = 0
                max_arr = 0xFFFFFFFF if timer_info.get("type") in ["GP32",
                                                                   "ADV"] and mcu_family != "STM32F1" else 0xFFFF

                init_fn = f"void {timer_instance}_Delay_Init(void) {{\n"
                init_fn += f"    // {timer_instance} Init for Delay (Kernel Clk: {timer_kernel_clk / 1e6:.2f} MHz)\n"
                init_fn += f"    {timer_instance}->PSC = {int(round(psc_us))}UL; // For 1 us tick\n"
                init_fn += f"    {timer_instance}->ARR = {max_arr}UL;\n"
                init_fn += f"    {timer_instance}->CR1 = TIM_CR1_URS; // UEV only on overflow/underflow\n"
                init_fn += f"    {timer_instance}->EGR = TIM_EGR_UG; // Load PSC & ARR\n"
                init_fn += f"    {timer_instance}->CR1 |= TIM_CR1_CEN; // Enable counter\n}}\n"
                source_function_blocks.append(init_fn);
                init_calls.append(f"{timer_instance}_Delay_Init();")

                if gen_us:
                    default_helper_functions_code += f"\n// {timer_instance} based microsecond delay (blocking)\n"
                    default_helper_functions_code += f"void {timer_instance}_Delay_us(uint16_t us) {{\n"
                    default_helper_functions_code += f"    if(us == 0) return;\n    {timer_instance}->CNT = 0;\n"
                    default_helper_functions_code += f"    while({timer_instance}->CNT < us);\n}}\n"
                if gen_ms:
                    default_helper_functions_code += f"\n// {timer_instance} based millisecond delay (blocking)\n"
                    default_helper_functions_code += f"void {timer_instance}_Delay_ms(uint16_t ms) {{\n"
                    default_helper_functions_code += f"    for (uint16_t i = 0; i < ms; i++) {{"
                    if gen_us:
                        default_helper_functions_code += f" {timer_instance}_Delay_us(1000); }}\n}}\n"
                    else:
                        default_helper_functions_code += f" /* Requires {timer_instance}_Delay_us */ volatile uint32_t k=({timer_kernel_clk}/1000)/4; while(k--);}}\n}}\n"

    elif delay_source == "Simple Loop (Blocking, Inaccurate)":
        sysclk_loop = rcc_config_calculated.get("sysclk_freq_hz", CURRENT_MCU_DEFINES.get("HSI_VALUE_HZ", 16000000))
        if gen_us:
            default_helper_functions_code += "\n// Simple loop microsecond delay (inaccurate)\n"
            default_helper_functions_code += "void Loop_Delay_us(uint32_t us) {\n"
            default_helper_functions_code += f"    uint32_t iter = us * ({sysclk_loop}/1000000UL) / 5; /* Adjust 5 by calibration */\n"
            default_helper_functions_code += "    if(iter==0) iter=1; for (volatile uint32_t i=0; i<iter; ++i) {{ __NOP(); }}\n}\n"
        if gen_ms:
            default_helper_functions_code += "\n// Simple loop millisecond delay (inaccurate)\n"
            default_helper_functions_code += "void Loop_Delay_ms(uint32_t ms) {\n"
            default_helper_functions_code += f"    uint32_t iter_ms = ({sysclk_loop}/1000UL) / 5; /* Adjust 5 */\n"
            default_helper_functions_code += "    if(iter_ms==0) iter_ms=1; for(uint32_t i=0; i<ms; ++i) {{ for(volatile uint32_t j=0; j<iter_ms; ++j) {{ __NOP(); }} }}\n}\n"

    return {"source_function": "\n".join(
        source_function_blocks) if source_function_blocks else "// No Delay specific init needed\n",
            "init_call": "\n    ".join(init_calls), "rcc_clocks_to_enable": rcc_clocks_to_enable,
            "default_helper_functions": default_helper_functions_code, "error_messages": error_messages}