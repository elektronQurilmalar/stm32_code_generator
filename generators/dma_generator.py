from core.mcu_defines_loader import CURRENT_MCU_DEFINES


def generate_dma_code_cmsis(config):
    params = config.get("params", {})  # Full config passed, params inside
    mcu_family = params.get("mcu_family", "STM32F4")
    target_device = params.get("target_device", "STM32F407VG")
    dma_items_config = params.get("dma_items", [])  # Renamed from "streams"

    error_messages = []
    rcc_clocks_to_enable = set()
    source_functions = []
    init_calls = []

    if not dma_items_config:
        return {"source_function": "// No DMA items configured\n", "init_call": "",
                "rcc_clocks_to_enable": [], "error_messages": []}

    dma_init_func_name = f"DMA_User_Init"
    dma_init_code = f"void {dma_init_func_name}(void) {{\n"
    dma_init_code += f"    // DMA Configuration ({mcu_family} - CMSIS Register Level)\n\n"

    # Get bit positions and maps from CURRENT_MCU_DEFINES
    # F2/F4 Stream specific (SxCR)
    DMA_SxCR_EN_Pos = CURRENT_MCU_DEFINES.get("DMA_SxCR_EN_Pos", 0)
    DMA_SxCR_CHSEL_Pos = CURRENT_MCU_DEFINES.get("DMA_SxCR_CHSEL_Pos", 25)
    DMA_SxCR_CHSEL_Msk = CURRENT_MCU_DEFINES.get("DMA_SxCR_CHSEL_Msk", (0x7 << 25))
    DMA_SxCR_PFCTRL_Pos = CURRENT_MCU_DEFINES.get("DMA_SxCR_PFCTRL_Pos", 5)
    DMA_SxCR_CIRC_Pos = CURRENT_MCU_DEFINES.get("DMA_SxCR_CIRC_Pos", 8)
    # F1 Channel specific (CCRx) - names are different, map them conceptually
    DMA_CCRx_EN_Pos = CURRENT_MCU_DEFINES.get("DMA_CCRx_EN_Pos", 0)  # F1: EN in CCR
    DMA_CCRx_CIRC_Pos = CURRENT_MCU_DEFINES.get("DMA_CCRx_CIRC_Pos", 5)  # F1: CIRC in CCR

    # Common concepts (positions might differ slightly but map to same idea)
    DMA_DIR_Pos = CURRENT_MCU_DEFINES.get(f"DMA_DIR_Pos_{mcu_family}", CURRENT_MCU_DEFINES.get("DMA_SxCR_DIR_Pos", 6))
    DMA_DIR_Msk = CURRENT_MCU_DEFINES.get(f"DMA_DIR_Msk_{mcu_family}",
                                          CURRENT_MCU_DEFINES.get("DMA_SxCR_DIR_Msk", (0x3 << 6)))
    DMA_DIRECTIONS = CURRENT_MCU_DEFINES.get("DMA_DIRECTIONS", {})

    DMA_MINC_Pos = CURRENT_MCU_DEFINES.get(f"DMA_MINC_Pos_{mcu_family}",
                                           CURRENT_MCU_DEFINES.get("DMA_SxCR_MINC_Pos", 10))
    DMA_PINC_Pos = CURRENT_MCU_DEFINES.get(f"DMA_PINC_Pos_{mcu_family}",
                                           CURRENT_MCU_DEFINES.get("DMA_SxCR_PINC_Pos", 9))
    DMA_INCREMENT_MODES = CURRENT_MCU_DEFINES.get("DMA_INCREMENT_MODES", {})

    DMA_MSIZE_Pos = CURRENT_MCU_DEFINES.get(f"DMA_MSIZE_Pos_{mcu_family}",
                                            CURRENT_MCU_DEFINES.get("DMA_SxCR_MSIZE_Pos", 13))
    DMA_PSIZE_Pos = CURRENT_MCU_DEFINES.get(f"DMA_PSIZE_Pos_{mcu_family}",
                                            CURRENT_MCU_DEFINES.get("DMA_SxCR_PSIZE_Pos", 11))
    DMA_DATA_SIZES = CURRENT_MCU_DEFINES.get("DMA_DATA_SIZES", {})

    DMA_PL_Pos = CURRENT_MCU_DEFINES.get(f"DMA_PL_Pos_{mcu_family}", CURRENT_MCU_DEFINES.get("DMA_SxCR_PL_Pos", 16))
    DMA_PRIORITIES = CURRENT_MCU_DEFINES.get("DMA_PRIORITIES", {})

    DMA_TCIE_Pos = CURRENT_MCU_DEFINES.get(f"DMA_TCIE_Pos_{mcu_family}",
                                           CURRENT_MCU_DEFINES.get("DMA_SxCR_TCIE_Pos", 4))
    DMA_HTIE_Pos = CURRENT_MCU_DEFINES.get(f"DMA_HTIE_Pos_{mcu_family}",
                                           CURRENT_MCU_DEFINES.get("DMA_SxCR_HTIE_Pos", 3))
    DMA_TEIE_Pos = CURRENT_MCU_DEFINES.get(f"DMA_TEIE_Pos_{mcu_family}",
                                           CURRENT_MCU_DEFINES.get("DMA_SxCR_TEIE_Pos", 2))

    # F2/F4 FIFO specific
    DMA_SxFCR_DMDIS_Pos = CURRENT_MCU_DEFINES.get("DMA_SxFCR_DMDIS_Pos", 2)
    DMA_SxFCR_FTH_Pos = CURRENT_MCU_DEFINES.get("DMA_SxFCR_FTH_Pos", 0)
    DMA_SxFCR_FEIE_Pos = CURRENT_MCU_DEFINES.get("DMA_SxFCR_FEIE_Pos", 7)
    DMA_DMEIE_Pos = CURRENT_MCU_DEFINES.get("DMA_DMEIE_Pos", 1)  # In SxCR for F2/F4
    DMA_FIFO_MODES = CURRENT_MCU_DEFINES.get("DMA_FIFO_MODES", {})
    DMA_FIFO_THRESHOLDS = CURRENT_MCU_DEFINES.get("DMA_FIFO_THRESHOLDS", {})

    dma_item_label = "Stream" if mcu_family in ["STM32F2", "STM32F4"] else "Channel"

    for item_cfg in dma_items_config:
        if not item_cfg.get("enabled"): continue

        dma_controller = item_cfg.get("dma_controller", "DMA1")
        item_id_num = item_cfg.get("id_num", 0)  # Stream or Channel number
        item_ptr_cmsis = f"{dma_controller}_{dma_item_label}{item_id_num}"  # e.g. DMA1_Stream0 or DMA1_Channel1

        dma_info_map_key = f"DMA_PERIPHERALS_INFO_{mcu_family}"
        dma_info_map = CURRENT_MCU_DEFINES.get(dma_info_map_key, CURRENT_MCU_DEFINES.get("DMA_PERIPHERALS_INFO", {}))
        dma_ctrl_info = dma_info_map.get(dma_controller, {})
        if dma_ctrl_info.get("rcc_macro"):
            rcc_clocks_to_enable.add(dma_ctrl_info["rcc_macro"])
        else:
            error_messages.append(f"RCC macro not found for {dma_controller}"); continue

        dma_init_code += f"    // --- Configure {dma_controller} {dma_item_label} {item_id_num} ---\n"

        # Common config register (SxCR for F2/F4, CCRx for F1)
        cr_reg_name = "CR" if mcu_family in ["STM32F2", "STM32F4"] else "CCR"  # For F1, DMA_Channel_TypeDef has CCR
        en_bit_pos = DMA_SxCR_EN_Pos if mcu_family in ["STM32F2", "STM32F4"] else DMA_CCRx_EN_Pos

        dma_init_code += f"    // Ensure {dma_item_label} {item_id_num} is disabled\n"
        dma_init_code += f"    if ({item_ptr_cmsis}->{cr_reg_name} & (1UL << {en_bit_pos})) {{\n"
        dma_init_code += f"        {item_ptr_cmsis}->{cr_reg_name} &= ~(1UL << {en_bit_pos});\n    }}\n"
        dma_init_code += f"    while({item_ptr_cmsis}->{cr_reg_name} & (1UL << {en_bit_pos})); // Wait for EN bit to clear\n\n"

        # Clear interrupt flags (logic depends on family: LISR/HISR for F2/F4, ISR/IFCR for F1)
        # This part needs careful implementation per family's flag registers. Simplified for now.
        if mcu_family in ["STM32F2", "STM32F4"]:  # F2/F4 flag clearing (example for stream 0-3)
            flag_clear_reg = f"{dma_controller}->LIFCR" if item_id_num < 4 else f"{dma_controller}->HIFCR"
            flag_clear_offset = (item_id_num % 4) * 6 + (item_id_num % 4) // 2 * 4  # Approximate offset logic
            base_flag_mask = (0x3D << flag_clear_offset)  # Mask for TC,HT,TE,DME,FE related to stream
            dma_init_code += f"    {flag_clear_reg} = {hex(base_flag_mask)}; // Clear Stream {item_id_num} flags\n\n"
        elif mcu_family == "STM32F1":  # F1 flag clearing (DMA_IFCR)
            # GIFn, TCIFn, HTIFn, TEIFn (n = channel number 1-7)
            ch_idx_for_flags = item_id_num  # Assuming UI uses 0-6 for F1 channels
            flag_mask_f1 = (0xF << (ch_idx_for_flags * 4))  # Clears all 4 flags for channel
            dma_init_code += f"    {dma_controller}->IFCR = {hex(flag_mask_f1)}; // Clear Channel {item_id_num + 1} flags\n\n"

        cr_val = 0
        if mcu_family in ["STM32F2", "STM32F4"]:  # Stream Channel Selection for F2/F4
            cr_val |= (int(item_cfg.get("stream_channel_str", "0")) << DMA_SxCR_CHSEL_Pos) & DMA_SxCR_CHSEL_Msk

        cr_val |= (DMA_DIRECTIONS.get(item_cfg.get("direction_str"), 0b00) << DMA_DIR_Pos) & DMA_DIR_Msk

        mode_str = item_cfg.get("mode_str", "Normal")
        dma_modes_key = f"DMA_MODES_{mcu_family}"
        dma_modes_map = CURRENT_MCU_DEFINES.get(dma_modes_key, CURRENT_MCU_DEFINES.get("DMA_MODES", {}))

        if dma_modes_map.get(mode_str) == 1:  # Circular
            circ_pos = DMA_SxCR_CIRC_Pos if mcu_family in ["STM32F2", "STM32F4"] else DMA_CCRx_CIRC_Pos
            cr_val |= (1 << circ_pos)
        elif dma_modes_map.get(mode_str) == 2 and mcu_family in ["STM32F2", "STM32F4"]:  # Peripheral Flow Control
            cr_val |= (1 << DMA_SxCR_PFCTRL_Pos)

        if DMA_INCREMENT_MODES.get(item_cfg.get("mem_inc_str"), 1): cr_val |= (1 << DMA_MINC_Pos)
        if DMA_INCREMENT_MODES.get(item_cfg.get("periph_inc_str"), 0): cr_val |= (1 << DMA_PINC_Pos)

        cr_val |= (DMA_DATA_SIZES.get(item_cfg.get("periph_data_size_str"), 0b00) << DMA_PSIZE_Pos)
        cr_val |= (DMA_DATA_SIZES.get(item_cfg.get("mem_data_size_str"), 0b00) << DMA_MSIZE_Pos)
        cr_val |= (DMA_PRIORITIES.get(item_cfg.get("priority_str"), 0b00) << DMA_PL_Pos)

        if item_cfg.get("tc_interrupt"): cr_val |= (1 << DMA_TCIE_Pos)
        if item_cfg.get("ht_interrupt"): cr_val |= (1 << DMA_HTIE_Pos)
        if item_cfg.get("te_interrupt"): cr_val |= (1 << DMA_TEIE_Pos)
        if mcu_family in ["STM32F2", "STM32F4"] and item_cfg.get("dme_interrupt"):
            cr_val |= (1 << DMA_DMEIE_Pos)  # DMEIE in SxCR for F2/F4

        dma_init_code += f"    {item_ptr_cmsis}->{cr_reg_name} = 0x{cr_val:08X}UL;\n"

        if mcu_family in ["STM32F2", "STM32F4"]:  # FIFO Config for F2/F4
            fcr_val = 0
            if DMA_FIFO_MODES.get(item_cfg.get("fifo_mode_str"), 0) == 1:  # FIFO Enabled
                fcr_val &= ~(1 << DMA_SxFCR_DMDIS_Pos)
                fcr_val |= (DMA_FIFO_THRESHOLDS.get(item_cfg.get("fifo_threshold_str"), 0b00) << DMA_SxFCR_FTH_Pos)
                if item_cfg.get("fe_interrupt"): fcr_val |= (1 << DMA_SxFCR_FEIE_Pos)
            else:
                fcr_val |= (1 << DMA_SxFCR_DMDIS_Pos)  # Direct Mode
            dma_init_code += f"    {item_ptr_cmsis}->FCR = 0x{fcr_val:08X}UL;\n"

        # Peripheral & Memory Addresses (Names differ by family)
        par_reg_name = "PAR" if mcu_family in ["STM32F2", "STM32F4"] else "CPAR"
        mar_reg_name = "M0AR" if mcu_family in ["STM32F2", "STM32F4"] else "CMAR"
        ndtr_reg_name = "NDTR" if mcu_family in ["STM32F2", "STM32F4"] else "CNDTR"

        dma_init_code += f"    // Set Peripheral address (e.g., &(ADC1->DR))\n"
        dma_init_code += f"    // {item_ptr_cmsis}->{par_reg_name} = (uint32_t)PERIPHERAL_ADDRESS_HERE;\n"
        dma_init_code += f"    // Set Memory address (e.g., (uint32_t)my_buffer))\n"
        dma_init_code += f"    // {item_ptr_cmsis}->{mar_reg_name} = (uint32_t)MEMORY_BUFFER_ADDRESS_HERE;\n"
        dma_init_code += f"    // Set number of data items\n"
        dma_init_code += f"    // {item_ptr_cmsis}->{ndtr_reg_name} = NUMBER_OF_DATA_ITEMS_HERE;\n\n"
        dma_init_code += f"    // To start transfer: {item_ptr_cmsis}->{cr_reg_name} |= (1UL << {en_bit_pos});\n\n"

    dma_init_code += "}\n"
    if any(s.get("enabled") for s in dma_items_config):
        source_functions.append(dma_init_code)
        init_calls.append(f"{dma_init_func_name}();")
    else:
        source_functions.append(
            f"// No enabled DMA {dma_item_label.lower()}s to configure.\nvoid DMA_User_Init(void) {{}}\n")

    return {"source_function": "\n".join(source_functions), "init_call": "\n    ".join(init_calls),
            "rcc_clocks_to_enable": list(rcc_clocks_to_enable), "error_messages": error_messages}