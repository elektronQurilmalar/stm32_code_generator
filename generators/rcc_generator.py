from core.mcu_defines_loader import CURRENT_MCU_DEFINES


def generate_rcc_code_cmsis(config, peripheral_rcc_clocks=None):  # Renamed gpio_rcc_clocks
    errors = []
    cfg_params = config.get("params", {})  # Use "params" key for consistency
    calc_data = config.get("calculated", {})
    mcu_family = cfg_params.get("mcu_family", "STM32F4")
    target_device = cfg_params.get("target_device", "STM32F407VG")

    # Get bit positions from CURRENT_MCU_DEFINES
    # RCC_CR
    RCC_CR_HSION_Pos = CURRENT_MCU_DEFINES.get("RCC_CR_HSION_Pos", 0);
    RCC_CR_HSION = (1 << RCC_CR_HSION_Pos)
    RCC_CR_HSIRDY_Pos = CURRENT_MCU_DEFINES.get("RCC_CR_HSIRDY_Pos", 1);
    RCC_CR_HSIRDY = (1 << RCC_CR_HSIRDY_Pos)
    RCC_CR_HSEON_Pos = CURRENT_MCU_DEFINES.get("RCC_CR_HSEON_Pos", 16);
    RCC_CR_HSEON = (1 << RCC_CR_HSEON_Pos)
    RCC_CR_HSERDY_Pos = CURRENT_MCU_DEFINES.get("RCC_CR_HSERDY_Pos", 17);
    RCC_CR_HSERDY = (1 << RCC_CR_HSERDY_Pos)
    RCC_CR_HSEBYP_Pos = CURRENT_MCU_DEFINES.get("RCC_CR_HSEBYP_Pos", 18);
    RCC_CR_HSEBYP = (1 << RCC_CR_HSEBYP_Pos)
    RCC_CR_PLLON_Pos = CURRENT_MCU_DEFINES.get("RCC_CR_PLLON_Pos", 24);
    RCC_CR_PLLON = (1 << RCC_CR_PLLON_Pos)
    RCC_CR_PLLRDY_Pos = CURRENT_MCU_DEFINES.get("RCC_CR_PLLRDY_Pos", 25);
    RCC_CR_PLLRDY = (1 << RCC_CR_PLLRDY_Pos)
    # RCC_PLLCFGR (F2/F4)
    RCC_PLLCFGR_PLLM_Pos = CURRENT_MCU_DEFINES.get("RCC_PLLCFGR_PLLM_Pos", 0)
    RCC_PLLCFGR_PLLN_Pos = CURRENT_MCU_DEFINES.get("RCC_PLLCFGR_PLLN_Pos", 6)
    RCC_PLLCFGR_PLLP_Pos = CURRENT_MCU_DEFINES.get("RCC_PLLCFGR_PLLP_Pos", 16)
    RCC_PLLCFGR_PLLSRC_Pos = CURRENT_MCU_DEFINES.get("RCC_PLLCFGR_PLLSRC_Pos", 22)
    RCC_PLLCFGR_PLLQ_Pos = CURRENT_MCU_DEFINES.get("RCC_PLLCFGR_PLLQ_Pos", 24)
    # RCC_CFGR (F1 PLL specific parts)
    RCC_CFGR_PLLSRC_F1_Pos = CURRENT_MCU_DEFINES.get("RCC_CFGR_PLLSRC_F1_Pos", 16)  # PLLSRC for F1
    RCC_CFGR_PLLXTPRE_F1_Pos = CURRENT_MCU_DEFINES.get("RCC_CFGR_PLLXTPRE_F1_Pos", 17)  # PLLXTPRE for F1
    RCC_CFGR_PLLMULL_F1_Pos = CURRENT_MCU_DEFINES.get("RCC_CFGR_PLLMULL_F1_Pos", 18)  # PLLMULL for F1
    # RCC_CFGR (Common)
    RCC_CFGR_SW_Pos = CURRENT_MCU_DEFINES.get("RCC_CFGR_SW_Pos", 0)
    RCC_CFGR_SWS_Pos = CURRENT_MCU_DEFINES.get("RCC_CFGR_SWS_Pos", 2)
    RCC_CFGR_HPRE_Pos = CURRENT_MCU_DEFINES.get("RCC_CFGR_HPRE_Pos", 4)
    RCC_CFGR_PPRE1_Pos = CURRENT_MCU_DEFINES.get("RCC_CFGR_PPRE1_Pos", 10)
    RCC_CFGR_PPRE2_Pos = CURRENT_MCU_DEFINES.get("RCC_CFGR_PPRE2_Pos", 13)
    # FLASH_ACR
    FLASH_ACR_LATENCY_Pos = CURRENT_MCU_DEFINES.get("FLASH_ACR_LATENCY_Pos", 0)
    FLASH_ACR_LATENCY_Msk = CURRENT_MCU_DEFINES.get("FLASH_ACR_LATENCY_Msk", 0xF)
    FLASH_ACR_PRFTEN_Pos = CURRENT_MCU_DEFINES.get("FLASH_ACR_PRFTEN_Pos", 8)  # F4: PRFTEN, F1: PRFTBE
    FLASH_ACR_ICEN_Pos = CURRENT_MCU_DEFINES.get("FLASH_ACR_ICEN_Pos", 9)
    FLASH_ACR_DCEN_Pos = CURRENT_MCU_DEFINES.get("FLASH_ACR_DCEN_Pos", 10)
    # PWR_CR (F4 VOS and Overdrive)
    PWR_CR_VOS_Pos = CURRENT_MCU_DEFINES.get("PWR_CR_VOS_Pos", 14)
    PWR_CR_ODEN_Pos = CURRENT_MCU_DEFINES.get("PWR_CR_ODEN_Pos", 16)
    PWR_CR_ODSWEN_Pos = CURRENT_MCU_DEFINES.get("PWR_CR_ODSWEN_Pos", 17)
    # PWR_CSR (F4 Overdrive Ready)
    PWR_CSR_ODRDY_Pos = CURRENT_MCU_DEFINES.get("PWR_CSR_ODRDY_Pos", 16)
    PWR_CSR_ODSWRDY_Pos = CURRENT_MCU_DEFINES.get("PWR_CSR_ODSWRDY_Pos", 17)
    # RCC APB1ENR PWREN
    RCC_APB1ENR_PWREN_Pos = CURRENT_MCU_DEFINES.get("RCC_APB1ENR_PWREN_Pos", 28)
    RCC_APB1ENR_PWREN = (1 << RCC_APB1ENR_PWREN_Pos)

    cmsis_header = CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {}).get(target_device, {}).get("cmsis_header",
                                                                                            f"stm32{mcu_family.lower()}xx.h")

    if not cfg_params or not calc_data:
        errors.append("RCC params or calculated values missing.");
        return {"error_messages": errors, "cmsis_device_header": cmsis_header}
    if calc_data.get("errors"): errors.extend(calc_data["errors"])

    c_code = "void RCC_User_Init(void) {\n"
    c_code += f"    // RCC Configuration ({mcu_family} - CMSIS Register Level)\n\n"

    # Enable HSI if needed
    if cfg_params.get("hsi_enabled", True) or \
            (cfg_params.get("pll_enabled") and cfg_params.get("pll_source") in ["HSI", "HSI/2"]):
        c_code += f"    RCC->CR |= RCC_CR_HSION;\n    while (!(RCC->CR & RCC_CR_HSIRDY));\n\n"

    # Enable HSE if needed
    if cfg_params.get("hse_enabled") and \
            (cfg_params.get("sysclk_source") == "HSE" or \
             (cfg_params.get("pll_enabled") and cfg_params.get("pll_source") == "HSE")):
        if cfg_params.get("hse_bypass", False):
            c_code += f"    RCC->CR |= RCC_CR_HSEBYP;\n"
        else:
            c_code += f"    RCC->CR &= ~RCC_CR_HSEBYP;\n"
        c_code += f"    RCC->CR |= RCC_CR_HSEON;\n"
        c_code += "    uint32_t hse_timeout = 5000;\n    while (!(RCC->CR & RCC_CR_HSERDY) && hse_timeout--) {{}}\n"
        c_code += "    if (!(RCC->CR & RCC_CR_HSERDY)) { /* Error: HSE not ready! */ }\n\n"

    # VOS and Overdrive (F4 specific generally)
    if mcu_family == "STM32F4":
        vos_pwr_val = calc_data.get("vos_scale_pwr_cr_val")
        if vos_pwr_val is not None:
            c_code += f"    RCC->APB1ENR |= RCC_APB1ENR_PWREN;\n"
            c_code += f"    PWR->CR = (PWR->CR & ~((0x3UL << {PWR_CR_VOS_Pos}))) | ({vos_pwr_val}UL << {PWR_CR_VOS_Pos}); // Set VOS\n\n"
        if calc_data.get("overdrive_active", False) and CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {}).get(target_device,
                                                                                                          {}).get(
                "has_overdrive"):
            c_code += f"    PWR->CR |= (1UL << {PWR_CR_ODEN_Pos}); while(!(PWR->CSR & (1UL << {PWR_CSR_ODRDY_Pos}))); // Enable OD\n"
            c_code += f"    PWR->CR |= (1UL << {PWR_CR_ODSWEN_Pos}); while(!(PWR->CSR & (1UL << {PWR_CSR_ODSWRDY_Pos}))); // Switch to OD\n\n"

    # Flash Latency (Common concept, register name/bits might differ)
    flash_latency_val = calc_data.get("flash_latency_val")
    prften_bit_name = "PRFTEN" if mcu_family in ["STM32F2", "STM32F4"] else "PRFTBE"  # F1 PRFTBE
    flash_acr_prften = (1 << CURRENT_MCU_DEFINES.get(f"FLASH_ACR_{prften_bit_name}_Pos", FLASH_ACR_PRFTEN_Pos))

    if flash_latency_val is not None:
        flash_acr_val = (flash_latency_val << FLASH_ACR_LATENCY_Pos) | flash_acr_prften
        if mcu_family != "STM32F1":  # ICEN/DCEN for F2/F4
            flash_acr_val |= (1 << FLASH_ACR_ICEN_Pos) | (1 << FLASH_ACR_DCEN_Pos)
        c_code += f"    FLASH->ACR = 0x{flash_acr_val:08X}UL;\n"
        c_code += f"    if ((FLASH->ACR & {FLASH_ACR_LATENCY_Msk}) != ({flash_latency_val}UL << {FLASH_ACR_LATENCY_Pos})) {{/*Error*/}}\n\n"
    else:
        errors.append("Flash latency not determined."); c_code += "    // WARNING: Flash latency not configured!\n\n"

    # PLL Config
    if cfg_params.get("pll_enabled") and cfg_params.get("sysclk_source") == "PLL":
        c_code += "    RCC->CR &= ~RCC_CR_PLLON; while(RCC->CR & RCC_CR_PLLRDY);\n\n"  # Disable PLL
        if mcu_family in ["STM32F2", "STM32F4"]:
            pllm = cfg_params.get("pllm_or_xtpre");
            plln = cfg_params.get("plln_or_mul")
            pllp_map = {"2": 0b00, "4": 0b01, "6": 0b10, "8": 0b11};
            pllp_reg = pllp_map.get(str(cfg_params.get("pllp")))
            pllq = cfg_params.get("pllq")
            pllsrc_reg = (1 << RCC_PLLCFGR_PLLSRC_Pos) if cfg_params.get("pll_source") == "HSE" else 0
            if None in [pllm, plln, pllp_reg, pllq] or not all(isinstance(x, int) for x in [pllm, plln, pllq]):
                errors.append("F2/F4 PLL M,N,P,Q invalid.");
                c_code += "    // ERROR: F2/F4 PLL M,N,P,Q invalid.\n\n"
            else:
                pllcfgr = (pllm << RCC_PLLCFGR_PLLM_Pos) | (plln << RCC_PLLCFGR_PLLN_Pos) | \
                          (pllp_reg << RCC_PLLCFGR_PLLP_Pos) | pllsrc_reg | (pllq << RCC_PLLCFGR_PLLQ_Pos)
                c_code += f"    RCC->PLLCFGR = 0x{pllcfgr:08X}UL;\n"
        elif mcu_family == "STM32F1":
            pllxtpre_f1 = (1 << RCC_CFGR_PLLXTPRE_F1_Pos) if cfg_params.get("pllm_or_xtpre",
                                                                            1) == 2 else 0  # Div by 2 if val is 2
            pllmul_f1 = (cfg_params.get("plln_or_mul", 9) - 2) & 0xF  # MUL is (val-2)
            pllsrc_f1 = (1 << RCC_CFGR_PLLSRC_F1_Pos) if cfg_params.get("pll_source") == "HSE" else 0
            cfgr_pll_bits = (pllsrc_f1 | pllxtpre_f1 | (pllmul_f1 << RCC_CFGR_PLLMULL_F1_Pos))
            # Mask for F1 PLL bits in CFGR: PLLSRC, PLLXTPRE, PLLMULL[3:0]
            f1_pll_mask = (1 << RCC_CFGR_PLLSRC_F1_Pos) | (1 << RCC_CFGR_PLLXTPRE_F1_Pos) | (
                        0xF << RCC_CFGR_PLLMULL_F1_Pos)
            c_code += f"    RCC->CFGR = (RCC->CFGR & ~{hex(f1_pll_mask)}UL) | {hex(cfgr_pll_bits)}UL;\n"

        c_code += "    RCC->CR |= RCC_CR_PLLON; uint32_t pll_timeout=5000;\n"
        c_code += "    while(!(RCC->CR & RCC_CR_PLLRDY) && pll_timeout--); if(!(RCC->CR & RCC_CR_PLLRDY)){/*Error*/}\n\n"

    # Prescalers (HPRE, PPRE1, PPRE2 in RCC_CFGR)
    prescaler_map_key_suffix = f"_{mcu_family}" if mcu_family == "STM32F1" else ""  # F1 has specific maps
    ahb_map = CURRENT_MCU_DEFINES.get(f"AHB_PRESCALER_MAP{prescaler_map_key_suffix}",
                                      CURRENT_MCU_DEFINES.get("AHB_PRESCALER_MAP", {}))
    apb_map = CURRENT_MCU_DEFINES.get(f"APB_PRESCALER_MAP{prescaler_map_key_suffix}",
                                      CURRENT_MCU_DEFINES.get("APB_PRESCALER_MAP", {}))

    hpre_val = ahb_map.get(calc_data.get("ahb_div"), 0)
    ppre1_val = apb_map.get(calc_data.get("apb1_div"), 0)
    ppre2_val = apb_map.get(calc_data.get("apb2_div"), 0)

    cfgr_prescaler_mask = (0xF << RCC_CFGR_HPRE_Pos) | (0x7 << RCC_CFGR_PPRE1_Pos) | (0x7 << RCC_CFGR_PPRE2_Pos)
    cfgr_prescaler_val = (hpre_val << RCC_CFGR_HPRE_Pos) | (ppre1_val << RCC_CFGR_PPRE1_Pos) | (
                ppre2_val << RCC_CFGR_PPRE2_Pos)
    c_code += f"    RCC->CFGR = (RCC->CFGR & ~{hex(cfgr_prescaler_mask)}UL) | {hex(cfgr_prescaler_val)}UL;\n\n"  # Apply prescalers

    # SYSCLK Switch
    sysclk_sw_val = 0;
    sysclk_sws_val = 0
    sysclk_source = cfg_params.get("sysclk_source", "HSI")
    sw_map_key = f"RCC_CFGR_SW_VALS_{mcu_family}"  # e.g. RCC_CFGR_SW_VALS_STM32F1
    sw_map = CURRENT_MCU_DEFINES.get(sw_map_key, CURRENT_MCU_DEFINES.get("RCC_CFGR_SW_VALS", {}))  # Fallback generic
    sws_map_key = f"RCC_CFGR_SWS_VALS_{mcu_family}"
    sws_map = CURRENT_MCU_DEFINES.get(sws_map_key, CURRENT_MCU_DEFINES.get("RCC_CFGR_SWS_VALS", {}))

    sysclk_sw_val = sw_map.get(sysclk_source, sw_map.get("HSI", 0))  # Default HSI if invalid
    sysclk_sws_val = sws_map.get(sysclk_source, sws_map.get("HSI", 0))

    # Sanity checks for SYSCLK source
    if sysclk_source == "HSE" and not cfg_params.get("hse_enabled"):
        errors.append("HSE SYSCLK, but HSE not enabled. Fallback HSI.");
        sysclk_sw_val = sw_map.get("HSI");
        sysclk_sws_val = sws_map.get("HSI")
    if sysclk_source == "PLL" and not cfg_params.get("pll_enabled"):
        errors.append("PLL SYSCLK, but PLL not enabled. Fallback HSI.");
        sysclk_sw_val = sw_map.get("HSI");
        sysclk_sws_val = sws_map.get("HSI")

    cfgr_sw_mask = (0x3 << RCC_CFGR_SW_Pos)  # SW bits are usually 0-1
    c_code += f"    RCC->CFGR = (RCC->CFGR & ~{hex(cfgr_sw_mask)}UL) | ({sysclk_sw_val}UL << {RCC_CFGR_SW_Pos});\n"
    c_code += f"    uint32_t sw_timeout=5000; while((RCC->CFGR & (0x3UL << {RCC_CFGR_SWS_Pos})) != ({sysclk_sws_val}UL << {RCC_CFGR_SWS_Pos}) && sw_timeout--);\n"
    c_code += f"    if((RCC->CFGR & (0x3UL << {RCC_CFGR_SWS_Pos})) != ({sysclk_sws_val}UL << {RCC_CFGR_SWS_Pos})){{/*Error*/}}\n\n"

    # Peripheral clocks (collected from other modules)
    if peripheral_rcc_clocks:
        # Group clocks by bus register (AHB1ENR, APB1ENR, APB2ENR etc.)
        bus_clocks = {"AHB1": [], "AHB2": [], "AHB3": [], "APB1": [], "APB2": []}  # Add more buses if needed
        for clock_macro_str in peripheral_rcc_clocks:
            # Determine bus from macro name (e.g. RCC_AHB1ENR_GPIOAEN -> AHB1)
            # This is a simplification; a robust way is to have this info in defines.
            if "AHB1ENR" in clock_macro_str:
                bus_clocks["AHB1"].append(clock_macro_str)
            elif "AHB2ENR" in clock_macro_str:
                bus_clocks["AHB2"].append(clock_macro_str)
            elif "AHB3ENR" in clock_macro_str:
                bus_clocks["AHB3"].append(clock_macro_str)
            elif "APB1ENR" in clock_macro_str:
                bus_clocks["APB1"].append(clock_macro_str)
            elif "APB2ENR" in clock_macro_str:
                bus_clocks["APB2"].append(clock_macro_str)
            # F1 has AHBENR (not AHB1/2/3)
            elif "AHBENR" in clock_macro_str and mcu_family == "STM32F1":
                bus_clocks["AHB1"].append(clock_macro_str)  # Map F1 AHB to AHB1 logic here

        for bus_name, macros in bus_clocks.items():
            if macros:
                enr_reg_name = f"{bus_name}ENR"  # e.g. AHB1ENR
                if mcu_family == "STM32F1" and bus_name == "AHB1": enr_reg_name = "AHBENR"  # F1 specific

                c_code += f"    // Enable clocks for {bus_name} peripherals\n"
                # Create ORed mask for all macros on this bus
                or_mask_str = " | ".join(macros)
                c_code += f"    RCC->{enr_reg_name} |= ({or_mask_str});\n"
                c_code += f"    volatile uint32_t dummy_read_{enr_reg_name.lower()} = RCC->{enr_reg_name}; (void)dummy_read_{enr_reg_name.lower()};\n\n"  # Delay after clock enable

    c_code += "}\n"
    return {"source_function": c_code, "init_call": "RCC_User_Init()",
            "system_core_clock_update_needed": True, "error_messages": errors, "cmsis_device_header": cmsis_header}