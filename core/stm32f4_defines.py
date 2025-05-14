# --- MODIFIED FILE stm32f4_defines.py ---

# Clock Source Frequencies
HSI_VALUE_HZ = 16000000
HSE_DEFAULT_HZ = 8000000

# PLL Parameters
PLLM_MIN = 2; PLLM_MAX = 63
PLLN_MIN_GENERAL = 50; PLLN_MAX_GENERAL = 432
PLLP_VALUES = [2, 4, 6, 8]
PLLQ_MIN = 2; PLLQ_MAX = 15

PLLN_RANGES_BY_DEVICE_SERIES = {
    "STM32F401": (192, 432),
    "STM32F411": (192, 432),
    "STM32F405": (50, 432),
    "STM32F407": (50, 432),
    "STM32F415": (50, 432),
    "STM32F417": (50, 432),
    "STM32F42": (50, 432),
    "STM32F43": (50, 432),
    "STM32F446": (50, 432),
    "STM32F469": (50, 432),
}


# VCO Frequencies
VCO_INPUT_MIN_HZ = 1000000; VCO_INPUT_MAX_HZ = 2000000
VCO_OUTPUT_MIN_HZ = 100000000; VCO_OUTPUT_MAX_HZ = 432000000

# Max Clock Frequencies (Simplified, consult datasheet for VOS and VDD specifics)
SYSCLK_MAX_HZ_MAP = {
    "STM32F407VG": {"VOS1_old": 168000000, "VOS2_old": 144000000},
    "STM32F401xE": {"VOS1_old": 84000000, "VOS2_old": 84000000, "VOS3_old": 60000000},
    "STM32F429ZI": {"VOS1_od": 180000000, "VOS2_od": 168000000, "VOS3_od": 144000000},
    "STM32F411xE": {"VOS1": 100000000, "VOS2": 84000000, "VOS3": 60000000},
    "STM32F446RE": {"VOS1_od": 180000000, "VOS2_od": 168000000, "VOS3_od": 144000000},
}
HCLK_MAX_HZ_MAP = SYSCLK_MAX_HZ_MAP

PCLK1_MAX_HZ_MAP = {
    "STM32F407VG": {"VOS1_old": 42000000, "VOS2_old": 36000000},
    "STM32F401xE": {"VOS1_old": 42000000, "VOS2_old": 42000000, "VOS3_old": 30000000},
    "STM32F429ZI": {"VOS1_od": 45000000, "VOS2_od": 42000000, "VOS3_od": 36000000},
    "STM32F411xE": {"VOS1": 50000000, "VOS2": 42000000, "VOS3": 30000000},
    "STM32F446RE": {"VOS1_od": 45000000, "VOS2_od": 42000000, "VOS3_od": 36000000},
}
PCLK2_MAX_HZ_MAP = {
    "STM32F407VG": {"VOS1_old": 84000000, "VOS2_old": 72000000},
    "STM32F401xE": {"VOS1_old": 84000000, "VOS2_old": 84000000, "VOS3_old": 60000000},
    "STM32F429ZI": {"VOS1_od": 90000000, "VOS2_od": 84000000, "VOS3_od": 72000000},
    "STM32F411xE": {"VOS1": 100000000, "VOS2": 84000000, "VOS3": 60000000},
    "STM32F446RE": {"VOS1_od": 90000000, "VOS2_od": 84000000, "VOS3_od": 72000000},
}

AHB_PRESCALER_MAP = {1:0b0000, 2:0b1000, 4:0b1001, 8:0b1010, 16:0b1011, 64:0b1100, 128:0b1101, 256:0b1110, 512:0b1111}
APB_PRESCALER_MAP = {1:0b000, 2:0b100, 4:0b101, 8:0b110, 16:0b111}
FLASH_LATENCY_MAP_CMSIS = {i: i for i in range(16)}
VOS_SCALE_MAP_CMSIS = {"VOS_SCALE_1": 0b11, "VOS_SCALE_2": 0b10, "VOS_SCALE_3": 0b01}

TARGET_DEVICES = {
    "STM32F407VG": {
        "cmsis_header": "stm32f407xx.h", "has_overdrive": False,
        "max_sysclk_vos1_no_od": 168000000,
        "flash_latency_ranges": [(30,0),(60,1),(90,2),(120,3),(150,4),(168,5)],
        "vos_scales_available": ["VOS_SCALE_1", "VOS_SCALE_2"],
        "vos_max_hclk": {"VOS_SCALE_1": 168000000, "VOS_SCALE_2": 144000000},
        "usart_instances": ["USART1","USART2","USART3","UART4","UART5","USART6"],
        "timer_instances": ["TIM1","TIM2","TIM3","TIM4","TIM5","TIM6","TIM7","TIM8","TIM9","TIM10","TIM11","TIM12","TIM13","TIM14"],
        "i2c_instances": ["I2C1","I2C2","I2C3"],
        "spi_instances": ["SPI1","SPI2","SPI3"],
        "can_instances": ["CAN1", "CAN2"],
        "dac_instances": ["DAC1"],
        "dma_controllers": ["DMA1", "DMA2"],
        "watchdog_instances": ["IWDG", "WWDG"],
        "max_pclk1_hz": PCLK1_MAX_HZ_MAP["STM32F407VG"]["VOS1_old"],
        "max_pclk2_hz": PCLK2_MAX_HZ_MAP["STM32F407VG"]["VOS1_old"],
    },
    "STM32F401xE": {
        "cmsis_header": "stm32f401xe.h", "has_overdrive": False,
        "max_sysclk_vos1_no_od": 84000000,
        "flash_latency_ranges": [(24,0),(48,1),(72,2),(84,2)],
        "vos_scales_available": ["VOS_SCALE_1", "VOS_SCALE_2", "VOS_SCALE_3"],
        "vos_max_hclk": {"VOS_SCALE_1": 84000000, "VOS_SCALE_2": 84000000, "VOS_SCALE_3": 60000000},
        "usart_instances": ["USART1","USART2","USART6"],
        "timer_instances": ["TIM1","TIM2","TIM3","TIM4","TIM5","TIM9","TIM10","TIM11"],
        "i2c_instances": ["I2C1","I2C2","I2C3"],
        "spi_instances": ["SPI1","SPI2","SPI3","SPI4"],
        "dac_instances": [],
        "dma_controllers": ["DMA1", "DMA2"],
        "watchdog_instances": ["IWDG", "WWDG"],
        "max_pclk1_hz": PCLK1_MAX_HZ_MAP["STM32F401xE"]["VOS1_old"],
        "max_pclk2_hz": PCLK2_MAX_HZ_MAP["STM32F401xE"]["VOS1_old"],
    },
    "STM32F411xE": {
        "cmsis_header": "stm32f411xe.h", "has_overdrive": False,
        "max_sysclk_vos1_no_od": 100000000,
        "flash_latency_ranges": [(30,0),(60,1),(90,2),(100,3)],
        "vos_scales_available": ["VOS_SCALE_1", "VOS_SCALE_2", "VOS_SCALE_3"],
        "vos_max_hclk": {"VOS_SCALE_1": 100000000, "VOS_SCALE_2": 84000000, "VOS_SCALE_3": 60000000},
        "usart_instances": ["USART1","USART2","USART6"],
        "timer_instances": ["TIM1","TIM2","TIM3","TIM4","TIM5","TIM9","TIM10","TIM11"],
        "i2c_instances": ["I2C1","I2C2","I2C3"],
        "spi_instances": ["SPI1","SPI2","SPI3","SPI4","SPI5"],
        "dac_instances": [],
        "dma_controllers": ["DMA1", "DMA2"],
        "watchdog_instances": ["IWDG", "WWDG"],
        "max_pclk1_hz": PCLK1_MAX_HZ_MAP["STM32F411xE"]["VOS1"],
        "max_pclk2_hz": PCLK2_MAX_HZ_MAP["STM32F411xE"]["VOS1"],
    },
    "STM32F429ZI": {
        "cmsis_header": "stm32f429xx.h", "has_overdrive": True,
        "max_sysclk_vos1_no_od": 168000000, "max_sysclk_vos1_od": 180000000,
        "flash_latency_ranges": [(30,0),(60,1),(90,2),(120,3),(150,4),(180,5)],
        "vos_scales_available": ["VOS_SCALE_1", "VOS_SCALE_2", "VOS_SCALE_3"],
        "vos_max_hclk": {"VOS_SCALE_1": 180000000, "VOS_SCALE_2": 168000000, "VOS_SCALE_3": 144000000},
        "usart_instances": ["USART1","USART2","USART3","UART4","UART5","USART6","UART7","UART8"],
        "timer_instances": ["TIM1","TIM2","TIM3","TIM4","TIM5","TIM6","TIM7","TIM8","TIM9","TIM10","TIM11","TIM12","TIM13","TIM14"],
        "i2c_instances": ["I2C1","I2C2","I2C3"],
        "spi_instances": ["SPI1","SPI2","SPI3","SPI4","SPI5","SPI6"],
        "can_instances": ["CAN1", "CAN2"],
        "dac_instances": ["DAC1"],
        "dma_controllers": ["DMA1", "DMA2"],
        "watchdog_instances": ["IWDG", "WWDG"],
        "max_pclk1_hz": PCLK1_MAX_HZ_MAP["STM32F429ZI"]["VOS1_od"],
        "max_pclk2_hz": PCLK2_MAX_HZ_MAP["STM32F429ZI"]["VOS1_od"],
    },
    "STM32F446RE": {
        "cmsis_header": "stm32f446xx.h", "has_overdrive": True,
        "max_sysclk_vos1_no_od": 168000000, "max_sysclk_vos1_od": 180000000,
        "flash_latency_ranges": [(30,0),(60,1),(90,2),(120,3),(150,4),(180,5)],
        "vos_scales_available": ["VOS_SCALE_1", "VOS_SCALE_2", "VOS_SCALE_3"],
        "vos_max_hclk": {"VOS_SCALE_1": 180000000, "VOS_SCALE_2": 144000000, "VOS_SCALE_3": 120000000},
        "usart_instances": ["USART1","USART2","USART3","UART4","UART5","USART6"],
        "timer_instances": ["TIM1","TIM2","TIM3","TIM4","TIM5","TIM6","TIM7","TIM8","TIM9","TIM10","TIM11","TIM12","TIM13","TIM14"],
        "i2c_instances": ["I2C1","I2C2","I2C3","FMPI2C1"],
        "spi_instances": ["SPI1","SPI2","SPI3","SPI4"],
        "can_instances": ["CAN1", "CAN2"],
        "dac_instances": ["DAC1"],
        "dma_controllers": ["DMA1", "DMA2"],
        "watchdog_instances": ["IWDG", "WWDG"],
        "max_pclk1_hz": PCLK1_MAX_HZ_MAP["STM32F446RE"]["VOS1_od"],
        "max_pclk2_hz": PCLK2_MAX_HZ_MAP["STM32F446RE"]["VOS1_od"],
    },
}

def get_plln_range(target_device_id):
    for series_key, plln_range in PLLN_RANGES_BY_DEVICE_SERIES.items():
        if series_key in target_device_id:
            return plln_range
    return (PLLN_MIN_GENERAL, PLLN_MAX_GENERAL)

def get_flash_latency(hclk_freq_hz, target_device_id, vos_scale_id="VOS_SCALE_1"):
    device_info = TARGET_DEVICES.get(target_device_id)
    if not device_info or "flash_latency_ranges" not in device_info:
        if hclk_freq_hz > 150e6: return 5;
        elif hclk_freq_hz > 120e6: return 4
        elif hclk_freq_hz > 90e6: return 3;
        elif hclk_freq_hz > 60e6: return 2
        elif hclk_freq_hz > 30e6: return 1;
        else: return 0

    hclk_mhz = hclk_freq_hz / 1e6
    sorted_ranges = sorted(device_info["flash_latency_ranges"], key=lambda x: x[0])
    for max_hclk, ws in sorted_ranges:
        if hclk_mhz <= max_hclk:
            return ws
    return sorted_ranges[-1][1] if sorted_ranges else 5

def get_required_vos(hclk_freq_hz, target_device_id, overdrive_enabled=False):
    device_info = TARGET_DEVICES.get(target_device_id)
    if not device_info or "vos_max_hclk" not in device_info or "vos_scales_available" not in device_info:
        return "VOS_SCALE_1", VOS_SCALE_MAP_CMSIS.get("VOS_SCALE_1", 0b11)

    vos_max_hclk_map = device_info["vos_max_hclk"]
    available_scales = device_info["vos_scales_available"]

    for scale_id_str in available_scales:
        max_hclk_for_this_scale = vos_max_hclk_map.get(scale_id_str, 0)
        if scale_id_str == "VOS_SCALE_1" and device_info.get("has_overdrive"):
            if overdrive_enabled:
                max_hclk_for_this_scale = device_info.get("max_sysclk_vos1_od", max_hclk_for_this_scale)
            else:
                max_hclk_for_this_scale = device_info.get("max_sysclk_vos1_no_od", max_hclk_for_this_scale)

        if hclk_freq_hz <= max_hclk_for_this_scale:
            pwr_cr_val = VOS_SCALE_MAP_CMSIS.get(scale_id_str)
            if pwr_cr_val is not None:
                actual_vos_id_to_return = scale_id_str
                if scale_id_str == "VOS_SCALE_1" and device_info.get("has_overdrive") and overdrive_enabled:
                    actual_vos_id_to_return = "VOS_SCALE_1_OD"
                return actual_vos_id_to_return, pwr_cr_val
    best_scale = available_scales[0] if available_scales else "VOS_SCALE_1"
    return best_scale, VOS_SCALE_MAP_CMSIS.get(best_scale, 0b11)

ADC_CHANNELS_MAP = {
    "STM32F407VG": ([f"IN{i}" for i in range(16)] + ["TEMP", "VREFINT", "VBAT"]),
    "STM32F401xE": ([f"IN{i}" for i in range(10)] + ["TEMP", "VREFINT", "VBAT"]),
    "STM32F411xE": ([f"IN{i}" for i in range(19)] + ["TEMP", "VREFINT", "VBAT"]),
    "STM32F429ZI": ([f"IN{i}" for i in range(19)] + ["TEMP", "VREFINT", "VBAT"]),
    "STM32F446RE": ([f"IN{i}" for i in range(19)] + ["TEMP", "VREFINT", "VBAT"]),
}
ADC_CCR_ADCPRE_Pos=16; ADC_CCR_VBATE_Pos=22; ADC_CCR_TSVREFE_Pos=23; ADC_CR1_RES_Pos=24; ADC_CR1_SCAN_Pos=8; ADC_CR1_EOCIE_Pos=5; ADC_CR1_OVRIE_Pos=26; ADC_CR2_ADON_Pos=0; ADC_CR2_CONT_Pos=1; ADC_CR2_ALIGN_Pos=11; ADC_CR2_EOCS_Pos=10; ADC_CR2_EXTEN_Pos=28; ADC_CR2_EXTEN_Msk=(0x3<<ADC_CR2_EXTEN_Pos); ADC_CR2_EXTSEL_Pos=24; ADC_CR2_EXTSEL_Msk=(0xF<<ADC_CR2_EXTSEL_Pos); ADC_CR2_SWSTART_Pos=30; ADC_SQR1_L_Pos=20

USART_PERIPHERALS_INFO = {"USART1":{"bus":"APB2","rcc_macro":"RCC_APB2ENR_USART1EN"},"USART2":{"bus":"APB1","rcc_macro":"RCC_APB1ENR_USART2EN"},"USART3":{"bus":"APB1","rcc_macro":"RCC_APB1ENR_USART3EN"},"UART4":{"bus":"APB1","rcc_macro":"RCC_APB1ENR_UART4EN"},"UART5":{"bus":"APB1","rcc_macro":"RCC_APB1ENR_UART5EN"},"USART6":{"bus":"APB2","rcc_macro":"RCC_APB2ENR_USART6EN"}, "UART7":{"bus":"APB1","rcc_macro":"RCC_APB1ENR_UART7EN"}, "UART8":{"bus":"APB1","rcc_macro":"RCC_APB1ENR_UART8EN"}}
COMMON_BAUD_RATES = [9600,19200,38400,57600,115200,230400,460800,921600,1000000,1500000,2000000]
USART_WORD_LENGTH_MAP={"8 bits":0b0,"9 bits":0b1}; USART_PARITY_MAP={"None":0b00,"Even":0b10,"Odd":0b11}; USART_STOP_BITS_MAP={"1":0b00,"0.5":0b01,"2":0b10,"1.5":0b11}; USART_HW_FLOW_CTRL_MAP={"None":0b00,"RTS":0b01,"CTS":0b10,"RTS/CTS":0b11}; USART_MODE_MAP={"RX Only":0b01,"TX Only":0b10,"TX/RX":0b11}; USART_OVERSAMPLING_MAP={"16":0,"8":1}
USART_CR1_UE_Pos=13; USART_CR1_M_Pos=12; USART_CR1_PCE_Pos=10; USART_CR1_PS_Pos=9; USART_CR1_TE_Pos=3; USART_CR1_RE_Pos=2; USART_CR1_OVER8_Pos=15; USART_CR1_RXNEIE_Pos=5; USART_CR1_TXEIE_Pos=7; USART_CR1_TCIE_Pos=6; USART_CR1_PEIE_Pos=8; USART_CR2_STOP_Pos=12; USART_CR3_RTSE_Pos=8; USART_CR3_CTSE_Pos=9; USART_BRR_DIV_Mantissa_Pos=4; USART_BRR_DIV_Fraction_Pos=0; USART_SR_RXNE_Pos=5; USART_SR_TXE_Pos=7; USART_SR_TC_Pos=6; USART_SR_RXNE=(1<<USART_SR_RXNE_Pos); USART_SR_TXE=(1<<USART_SR_TXE_Pos); USART_SR_TC=(1<<USART_SR_TC_Pos)
USART_PIN_CONFIG_SUGGESTIONS = {
    "STM32F407VG":{"USART1":{"TX":"PA9/AF7 or PB6/AF7","RX":"PA10/AF7 or PB7/AF7"},"USART2":{"TX":"PA2/AF7 or PD5/AF7","RX":"PA3/AF7 or PD6/AF7"},"USART3":{"TX":"PB10/AF7 or PC10/AF7 or PD8/AF7","RX":"PB11/AF7 or PC11/AF7 or PD9/AF7"},"UART4":{"TX":"PA0/AF8 or PC10/AF8","RX":"PA1/AF8 or PC11/AF8"},"UART5":{"TX":"PC12/AF8","RX":"PD2/AF8"},"USART6":{"TX":"PC6/AF8 or PG14/AF8","RX":"PC7/AF8 or PG9/AF8"}},
    "STM32F401xE":{"USART1":{"TX":"PA9/AF7 or PB6/AF7","RX":"PA10/AF7 or PB7/AF7"},"USART2":{"TX":"PA2/AF7","RX":"PA3/AF7"},"USART6":{"TX":"PA11/AF8","RX":"PA12/AF8"}},
    "STM32F411xE":{"USART1":{"TX":"PA9/AF7 or PB6/AF7","RX":"PA10/AF7 or PB7/AF7"},"USART2":{"TX":"PA2/AF7 or PD5/AF7","RX":"PA3/AF7 or PD6/AF7"},"USART6":{"TX":"PA11/AF8 or PC6/AF8","RX":"PA12/AF8 or PC7/AF8"}},
    "STM32F429ZI":{"USART1":{"TX":"PA9/AF7 or PB6/AF7","RX":"PA10/AF7 or PB7/AF7"},"USART2":{"TX":"PA2/AF7 or PD5/AF7","RX":"PA3/AF7 or PD6/AF7"},"USART3":{"TX":"PB10/AF7 or PC10/AF7 or PD8/AF7","RX":"PB11/AF7 or PC11/AF7 or PD9/AF7"},"UART4":{"TX":"PA0/AF8 or PC10/AF8 or PD1/AF8","RX":"PA1/AF8 or PC11/AF8 or PD0/AF8"},"UART5":{"TX":"PC12/AF8","RX":"PD2/AF8"},"USART6":{"TX":"PC6/AF8 or PG14/AF8","RX":"PC7/AF8 or PG9/AF8"}, "UART7":{"TX":"PE8/AF8 or PF7/AF8","RX":"PE7/AF8 or PF6/AF8"}, "UART8":{"TX":"PE1/AF8","RX":"PE0/AF8"}},
    "STM32F446RE":{"USART1":{"TX":"PA9/AF7 or PB6/AF7","RX":"PA10/AF7 or PB7/AF7"},"USART2":{"TX":"PA2/AF7 or PD5/AF7","RX":"PA3/AF7 or PD6/AF7"},"USART3":{"TX":"PB10/AF7 or PC10/AF7 or PD8/AF7","RX":"PB11/AF7 or PC11/AF7 or PD9/AF7"},"UART4":{"TX":"PA0/AF8 or PD1/AF8","RX":"PA1/AF8 or PD0/AF8"},"UART5":{"TX":"PC12/AF8","RX":"PD2/AF8"},"USART6":{"TX":"PC6/AF8 or PG14/AF8","RX":"PC7/AF8 or PG9/AF8"}}}

TIMER_PERIPHERALS_INFO = {"TIM1":{"type":"ADV","bus":"APB2","rcc_macro":"RCC_APB2ENR_TIM1EN","max_channels":4,"has_bdtr":True},"TIM2":{"type":"GP32","bus":"APB1","rcc_macro":"RCC_APB1ENR_TIM2EN","max_channels":4,"has_bdtr":False},"TIM3":{"type":"GP16","bus":"APB1","rcc_macro":"RCC_APB1ENR_TIM3EN","max_channels":4,"has_bdtr":False},"TIM4":{"type":"GP16","bus":"APB1","rcc_macro":"RCC_APB1ENR_TIM4EN","max_channels":4,"has_bdtr":False},"TIM5":{"type":"GP32","bus":"APB1","rcc_macro":"RCC_APB1ENR_TIM5EN","max_channels":4,"has_bdtr":False},"TIM6":{"type":"BASIC","bus":"APB1","rcc_macro":"RCC_APB1ENR_TIM6EN","max_channels":0,"has_bdtr":False},"TIM7":{"type":"BASIC","bus":"APB1","rcc_macro":"RCC_APB1ENR_TIM7EN","max_channels":0,"has_bdtr":False},"TIM8":{"type":"ADV","bus":"APB2","rcc_macro":"RCC_APB2ENR_TIM8EN","max_channels":4,"has_bdtr":True},"TIM9":{"type":"GP16","bus":"APB2","rcc_macro":"RCC_APB2ENR_TIM9EN","max_channels":2,"has_bdtr":False},"TIM10":{"type":"GP16","bus":"APB2","rcc_macro":"RCC_APB2ENR_TIM10EN","max_channels":1,"has_bdtr":False},"TIM11":{"type":"GP16","bus":"APB2","rcc_macro":"RCC_APB2ENR_TIM11EN","max_channels":1,"has_bdtr":False},"TIM12":{"type":"GP16","bus":"APB1","rcc_macro":"RCC_APB1ENR_TIM12EN","max_channels":2,"has_bdtr":False},"TIM13":{"type":"GP16","bus":"APB1","rcc_macro":"RCC_APB1ENR_TIM13EN","max_channels":1,"has_bdtr":False},"TIM14":{"type":"GP16","bus":"APB1","rcc_macro":"RCC_APB1ENR_TIM14EN","max_channels":1,"has_bdtr":False}}
TIM_CR1_CEN=(1<<0); TIM_CR1_URS_Pos = 2; TIM_CR1_URS = (1 << TIM_CR1_URS_Pos); TIM_CR1_OPM_Pos = 3; TIM_CR1_OPM = (1 << TIM_CR1_OPM_Pos); TIM_CR1_DIR=(1<<4); TIM_CR1_CMS_Pos=5; TIM_CR1_ARPE=(1<<7); TIM_CR1_CKD_Pos=8
TIM_DIER_UIE=(1<<0); TIM_DIER_CC1IE=(1<<1); TIM_DIER_CC2IE=(1<<2); TIM_DIER_CC3IE=(1<<3); TIM_DIER_CC4IE=(1<<4)
TIM_EGR_UG=(1<<0); TIM_CCMRx_OCxM_Pos=4; TIM_CCMRx_OCxPE=(1<<3); TIM_CCMRx_CCxS_Pos=0; TIM_CCMRx_ICxPSC_Pos=2; TIM_CCMRx_ICxF_Pos=4; TIM_CCER_CC1E=(1<<0); TIM_CCER_CC1P=(1<<1); TIM_BDTR_MOE=(1<<15); TIM_SMCR_SMS_Pos=0; TIM_SMCR_TS_Pos=4; TIM_SMCR_ECE=(1<<14)
TIM_COUNTER_MODES={"Up":0x00,"Down":TIM_CR1_DIR,"Center-aligned 1 (Up/Down, IRQ on Up&Down)":(0x1<<TIM_CR1_CMS_Pos),"Center-aligned 2 (Up/Down, IRQ on Down)":(0x2<<TIM_CR1_CMS_Pos),"Center-aligned 3 (Up/Down, IRQ on Up)":(0x3<<TIM_CR1_CMS_Pos)}
TIM_CLOCK_DIVISION={"1":0x0,"2":0x1,"4":0x2}
TIM_OC_MODES={"Frozen":0b000,"Active on Match":0b001,"Inactive on Match":0b010,"Toggle on Match":0b011,"Force Inactive":0b100,"Force Active":0b101,"PWM Mode 1":0b110,"PWM Mode 2":0b111}
TIM_OC_POLARITY={"High (non-inverted)":0,"Low (inverted)":1}
TIM_IC_POLARITY={"Rising Edge":0b00,"Falling Edge":0b01,"Both Edges":0b11}; TIM_IC_SELECTION={"Direct (TIx)":0b01,"Indirect (TIy)":0b10,"TRC":0b11}; TIM_IC_PRESCALER={"1 (every event)":0b00,"2 (every 2nd event)":0b01,"4 (every 4th event)":0b10,"8 (every 8th event)":0b11}
TIM_INTERNAL_CLOCK_SOURCE="Internal Clock (CK_INT)"; TIM_ETR_MODES={"ETR - Mode 1 (via ETRF, prescaled, filtered)":"ETR_MODE1","ETR - Mode 2 (via ECE, no prescaler/filter on ETR path)":"ETR_MODE2"}

I2C_PERIPHERALS_INFO = {"I2C1":{"bus":"APB1","rcc_macro":"RCC_APB1ENR_I2C1EN"},"I2C2":{"bus":"APB1","rcc_macro":"RCC_APB1ENR_I2C2EN"},"I2C3":{"bus":"APB1","rcc_macro":"RCC_APB1ENR_I2C3EN"}, "FMPI2C1":{"bus":"APB1", "rcc_macro":"RCC_APB1ENR_FMPI2C1EN"}}
I2C_CLOCK_SPEEDS_HZ={"100000 Hz (Standard Mode)":100000,"400000 Hz (Fast Mode)":400000, "1000000 Hz (Fast Mode Plus - FMPI2C)": 1000000};
I2C_DUTY_CYCLE_MODES={"2 (t_low / t_high = 2)":0,"16/9 (t_low / t_high = 16/9)":1}; I2C_ADDRESSING_MODES={"7-bit":0,"10-bit":1}
I2C_PIN_CONFIG_SUGGESTIONS = {
    "STM32F407VG":{"I2C1":{"SCL":"PB6/AF4 or PB8/AF4","SDA":"PB7/AF4 or PB9/AF4"},"I2C2":{"SCL":"PB10/AF4 or PF1/AF4","SDA":"PB11/AF4 or PF0/AF4"},"I2C3":{"SCL":"PA8/AF4","SDA":"PC9/AF4"}},
    "STM32F401xE":{"I2C1":{"SCL":"PB6/AF4 or PB8/AF4","SDA":"PB7/AF4 or PB9/AF4"},"I2C2":{"SCL":"PB10/AF4","SDA":"PB3/AF9 or PB9/AF9"},"I2C3":{"SCL":"PA8/AF4","SDA":"PB4/AF9 or PC9/AF4"}},
    "STM32F411xE":{"I2C1":{"SCL":"PB6/AF4 or PB8/AF4","SDA":"PB7/AF4 or PB9/AF4"},"I2C2":{"SCL":"PB10/AF4 or PB3/AF9","SDA":"PB3/AF9 or PB9/AF9"},"I2C3":{"SCL":"PA8/AF4","SDA":"PB4/AF9 or PC9/AF4"}},
    "STM32F429ZI":{"I2C1":{"SCL":"PB6/AF4 or PB8/AF4","SDA":"PB7/AF4 or PB9/AF4"},"I2C2":{"SCL":"PB10/AF4 or PF1/AF4 or PH4/AF4","SDA":"PB11/AF4 or PF0/AF4 or PH5/AF4"},"I2C3":{"SCL":"PA8/AF4 or PH7/AF4","SDA":"PC9/AF4 or PH8/AF4"}},
    "STM32F446RE":{"I2C1":{"SCL":"PB6/AF4 or PB8/AF4","SDA":"PB7/AF4 or PB9/AF4"},"I2C2":{"SCL":"PB10/AF4 or PF1/AF4","SDA":"PB3/AF9 or PF0/AF4"},"I2C3":{"SCL":"PA8/AF4 or PC9/AF4","SDA":"PB4/AF9 or PC9/AF4"}, "FMPI2C1":{"SCL":"PC6/AF4 or PD12/AF4", "SDA":"PC7/AF4 or PD13/AF4"}}
}
I2C_CR1_PE_Pos=0; I2C_CR1_PE=(1<<I2C_CR1_PE_Pos); I2C_CR1_SWRST_Pos=15; I2C_CR1_SWRST=(1<<I2C_CR1_SWRST_Pos); I2C_CR1_START_Pos=8; I2C_CR1_START=(1<<I2C_CR1_START_Pos); I2C_CR1_STOP_Pos=9; I2C_CR1_STOP=(1<<I2C_CR1_STOP_Pos); I2C_CR1_ACK_Pos=10; I2C_CR1_ACK=(1<<I2C_CR1_ACK_Pos); I2C_CR2_FREQ_Pos=0; I2C_CR2_FREQ_Msk=(0x3F<<I2C_CR2_FREQ_Pos); I2C_CCR_CCR_Pos=0; I2C_CCR_CCR_Msk=(0xFFF<<I2C_CCR_CCR_Pos); I2C_CCR_FS_Pos=15; I2C_CCR_FS=(1<<I2C_CCR_FS_Pos); I2C_CCR_DUTY_Pos=14; I2C_CCR_DUTY=(1<<I2C_CCR_DUTY_Pos); I2C_SR1_SB_Pos=0; I2C_SR1_SB=(1<<I2C_SR1_SB_Pos); I2C_SR1_ADDR_Pos=1; I2C_SR1_ADDR=(1<<I2C_SR1_ADDR_Pos); I2C_SR1_BTF_Pos=2; I2C_SR1_BTF=(1<<I2C_SR1_BTF_Pos); I2C_SR1_RXNE_Pos=6; I2C_SR1_RXNE=(1<<I2C_SR1_RXNE_Pos); I2C_SR1_TXE_Pos=7; I2C_SR1_TXE=(1<<I2C_SR1_TXE_Pos)

SPI_PERIPHERALS_INFO = {"SPI1":{"bus":"APB2","rcc_macro":"RCC_APB2ENR_SPI1EN"},"SPI2":{"bus":"APB1","rcc_macro":"RCC_APB1ENR_SPI2EN"},"SPI3":{"bus":"APB1","rcc_macro":"RCC_APB1ENR_SPI3EN"}, "SPI4":{"bus":"APB2","rcc_macro":"RCC_APB2ENR_SPI4EN"}, "SPI5":{"bus":"APB2","rcc_macro":"RCC_APB2ENR_SPI5EN"}, "SPI6":{"bus":"APB2","rcc_macro":"RCC_APB2ENR_SPI6EN"}}
SPI_MODES={"Master":1,"Slave":0}; SPI_DIRECTIONS={"2 Lines Full Duplex":0,"1 Line Bidirectional (Output)":1,"1 Line Bidirectional (Input)":2,"1 Line Simplex RX":3}; SPI_DATA_SIZES={"8-bit":0,"16-bit":1}; SPI_CPOL={"Low":0,"High":1}; SPI_CPHA={"1 Edge":0,"2 Edge":1}; SPI_NSS_MODES={"Software (Master/Slave)":0,"Hardware NSS Output (Master)":1,"Hardware NSS Input (Slave)":2}; SPI_BAUD_PRESCALERS={"2":0b000,"4":0b001,"8":0b010,"16":0b011,"32":0b100,"64":0b101,"128":0b110,"256":0b111}; SPI_FIRST_BIT={"MSB First":0,"LSB First":1}
SPI_PIN_CONFIG_SUGGESTIONS = {
    "STM32F407VG":{"SPI1":{"SCK":"PA5/AF5 or PB3/AF5","MISO":"PA6/AF5 or PB4/AF5","MOSI":"PA7/AF5 or PB5/AF5","NSS":"PA4/AF5 or PA15/AF5"},"SPI2":{"SCK":"PB10/AF5 or PB13/AF5 or PI1/AF5","MISO":"PB14/AF5 or PC2/AF5 or PI2/AF5","MOSI":"PB15/AF5 or PC3/AF5 or PI3/AF5","NSS":"PB9/AF5 or PB12/AF5 or PI0/AF5"},"SPI3":{"SCK":"PB3/AF6 or PC10/AF6","MISO":"PB4/AF6 or PC11/AF6","MOSI":"PB5/AF6 or PC12/AF6","NSS":"PA4/AF6 or PA15/AF6"}},
    "STM32F401xE":{"SPI1":{"SCK":"PA5/AF5 or PB3/AF5","MISO":"PA6/AF5 or PB4/AF5","MOSI":"PA7/AF5 or PB5/AF5","NSS":"PA4/AF5 or PA15/AF5"},"SPI2":{"SCK":"PB10/AF5 or PB13/AF5","MISO":"PB14/AF5 or PC2/AF5","MOSI":"PB15/AF5 or PC3/AF5","NSS":"PB9/AF5 or PB12/AF5"},"SPI3":{"SCK":"PB3/AF6 or PC10/AF6","MISO":"PB4/AF6 or PC11/AF6","MOSI":"PB5/AF6 or PC12/AF6","NSS":"PA4/AF6 or PA15/AF6"},"SPI4":{"SCK":"PE2/AF5 or PE12/AF5","MISO":"PE5/AF5 or PE13/AF5","MOSI":"PE6/AF5 or PE14/AF5","NSS":"PE4/AF5 or PE11/AF5"}},
    "STM32F411xE":{"SPI1":{"SCK":"PA5/AF5 or PB3/AF5","MISO":"PA6/AF5 or PB4/AF5","MOSI":"PA7/AF5 or PB5/AF5","NSS":"PA4/AF5 or PA15/AF5"},"SPI2":{"SCK":"PB10/AF5 or PB13/AF5 or PC7/AF5(No Remap!)","MISO":"PB14/AF5 or PC2/AF5","MOSI":"PB15/AF5 or PC3/AF5","NSS":"PB9/AF5 or PB12/AF5"},"SPI3":{"SCK":"PB3/AF6 or PC10/AF6","MISO":"PB4/AF6 or PC11/AF6","MOSI":"PB5/AF6 or PC12/AF6","NSS":"PA4/AF6 or PA15/AF6"},"SPI4":{"SCK":"PE2/AF5 or PE12/AF5","MISO":"PE5/AF5 or PE13/AF5","MOSI":"PE6/AF5 or PE14/AF5","NSS":"PE4/AF5 or PE11/AF5"}, "SPI5":{"SCK":"PE2/AF5 or PE12/AF5(Shared with SPI4)","MISO":"PE5/AF5 or PE13/AF5","MOSI":"PE6/AF5 or PE14/AF5","NSS":"PE4/AF5 or PE11/AF5"}},
    "STM32F429ZI":{"SPI1":{"SCK":"PA5/AF5 or PB3/AF5","MISO":"PA6/AF5 or PB4/AF5","MOSI":"PA7/AF5 or PB5/AF5 or PG11/AF5","NSS":"PA4/AF5 or PA15/AF5"},"SPI2":{"SCK":"PB10/AF5 or PB13/AF5 or PI1/AF5","MISO":"PB14/AF5 or PC2/AF5 or PI2/AF5","MOSI":"PB15/AF5 or PC3/AF5 or PI3/AF5","NSS":"PB9/AF5 or PB12/AF5 or PI0/AF5"},"SPI3":{"SCK":"PB3/AF6 or PC10/AF6","MISO":"PB4/AF6 or PC11/AF6","MOSI":"PB5/AF6 or PC12/AF6","NSS":"PA4/AF6 or PA15/AF6"},"SPI4":{"SCK":"PE2/AF5 or PE12/AF5","MISO":"PE5/AF5 or PE13/AF5","MOSI":"PE6/AF5 or PE14/AF5","NSS":"PE4/AF5 or PE11/AF5"},"SPI5":{"SCK":"PF7/AF5 or PH6/AF5","MISO":"PF8/AF5 or PH7/AF5","MOSI":"PF9/AF5 or PF11/AF5","NSS":"PF6/AF5 or PH5/AF5"},"SPI6":{"SCK":"PG13/AF5","MISO":"PG12/AF5","MOSI":"PG14/AF5","NSS":"PG8/AF5"}},
    "STM32F446RE":{"SPI1":{"SCK":"PA5/AF5 or PB3/AF5","MISO":"PA6/AF5 or PB4/AF5","MOSI":"PA7/AF5 or PB5/AF5","NSS":"PA4/AF5 or PA15/AF5"},"SPI2":{"SCK":"PB10/AF5 or PC7/AF5","MISO":"PB14/AF5 or PC2/AF5","MOSI":"PB15/AF5 or PC3/AF5","NSS":"PB9/AF5 or PB12/AF5"},"SPI3":{"SCK":"PB3/AF6 or PC10/AF6","MISO":"PB4/AF6 or PC11/AF6","MOSI":"PB5/AF6 or PC12/AF6","NSS":"PA4/AF6 or PA15/AF6"},"SPI4":{"SCK":"PE2/AF5 or PE12/AF5","MISO":"PE5/AF5 or PE13/AF5","MOSI":"PE6/AF5 or PE14/AF5","NSS":"PE4/AF5 or PE11/AF5"}}
}
SPI_CR1_CPHA_Pos=0; SPI_CR1_CPOL_Pos=1; SPI_CR1_MSTR_Pos=2; SPI_CR1_BR_Pos=3; SPI_CR1_SPE_Pos=6; SPI_CR1_LSBFIRST_Pos=7; SPI_CR1_SSI_Pos=8; SPI_CR1_SSM_Pos=9; SPI_CR1_RXONLY_Pos=10; SPI_CR1_DFF_Pos=11; SPI_CR1_BIDIOE_Pos=14; SPI_CR1_BIDIMODE_Pos=15
SPI_CR2_SSOE_Pos=2; SPI_CR2_TXEIE_Pos=7; SPI_CR2_RXNEIE_Pos=6; SPI_CR2_ERRIE_Pos=5
SPI_SR_RXNE_Pos=0; SPI_SR_TXE_Pos=1; SPI_SR_BSY_Pos=7; SPI_SR_RXNE=(1<<SPI_SR_RXNE_Pos); SPI_SR_TXE=(1<<SPI_SR_TXE_Pos); SPI_SR_BSY=(1<<SPI_SR_BSY_Pos)

# --- DELAY DEFINES ---
DELAY_SOURCES = ["SysTick", "DWT Cycle Counter", "TIMx (General Purpose Timer)", "Simple Loop (Blocking, Inaccurate)"]
DELAY_TIMER_CANDIDATES = ["TIM2","TIM3","TIM4","TIM5","TIM9","TIM10","TIM11","TIM12","TIM13","TIM14"]
DWT_CTRL_CYCCNTENA_Pos = 0; DWT_CTRL_CYCCNTENA = (1 << DWT_CTRL_CYCCNTENA_Pos)
CoreDebug_DEMCR_TRCENA_Pos = 24; CoreDebug_DEMCR_TRCENA = (1 << CoreDebug_DEMCR_TRCENA_Pos)

# --- DMA DEFINES ---
DMA_STREAM_REG_OFFSETS = {"LISR": 0x00, "HISR": 0x04, "LIFCR": 0x08, "HIFCR": 0x0C,
                          "S0CR": 0x10, "S0NDTR": 0x14, "S0PAR": 0x18, "S0M0AR": 0x1C, "S0M1AR": 0x20, "S0FCR": 0x24,
                          }
DMA_SxCR_EN_Pos = 0; DMA_SxCR_EN = (1 << DMA_SxCR_EN_Pos)
DMA_SxCR_CHSEL_Pos = 25; DMA_SxCR_CHSEL_Msk = (0x7 << DMA_SxCR_CHSEL_Pos)
DMA_SxCR_DIR_Pos = 6; DMA_SxCR_DIR_Msk = (0x3 << DMA_SxCR_DIR_Pos)
DMA_SxCR_CIRC_Pos = 8; DMA_SxCR_CIRC = (1 << DMA_SxCR_CIRC_Pos)
DMA_SxCR_PINC_Pos = 9; DMA_SxCR_PINC = (1 << DMA_SxCR_PINC_Pos)
DMA_SxCR_MINC_Pos = 10; DMA_SxCR_MINC = (1 << DMA_SxCR_MINC_Pos)
DMA_SxCR_PSIZE_Pos = 11; DMA_SxCR_PSIZE_Msk = (0x3 << DMA_SxCR_PSIZE_Pos)
DMA_SxCR_MSIZE_Pos = 13; DMA_SxCR_MSIZE_Msk = (0x3 << DMA_SxCR_MSIZE_Pos)
DMA_SxCR_PL_Pos = 16; DMA_SxCR_PL_Msk = (0x3 << DMA_SxCR_PL_Pos)
DMA_SxCR_PFCTRL_Pos = 5; DMA_SxCR_PFCTRL = (1 << DMA_SxCR_PFCTRL_Pos)
DMA_SxCR_TCIE_Pos = 4; DMA_SxCR_TCIE = (1 << DMA_SxCR_TCIE_Pos)
DMA_SxCR_HTIE_Pos = 3; DMA_SxCR_HTIE = (1 << DMA_SxCR_HTIE_Pos)
DMA_SxCR_TEIE_Pos = 2; DMA_SxCR_TEIE = (1 << DMA_SxCR_TEIE_Pos)
DMA_SxCR_DMEIE_Pos = 1; DMA_SxCR_DMEIE = (1 << DMA_SxCR_DMEIE_Pos)

DMA_SxFCR_FTH_Pos = 0; DMA_SxFCR_FTH_Msk = (0x3 << DMA_SxFCR_FTH_Pos)
DMA_SxFCR_DMDIS_Pos = 2; DMA_SxFCR_DMDIS = (1 << DMA_SxFCR_DMDIS_Pos)
DMA_SxFCR_FS_Pos = 3; DMA_SxFCR_FS_Msk = (0x7 << DMA_SxFCR_FS_Pos)
DMA_SxFCR_FEIE_Pos = 7; DMA_SxFCR_FEIE = (1 << DMA_SxFCR_FEIE_Pos)

DMA_FLAG_FEIF_Pos = 0
DMA_FLAG_DMEIF_Pos = 2
DMA_FLAG_TEIF_Pos = 3
DMA_FLAG_HTIF_Pos = 4
DMA_FLAG_TCIF_Pos = 5

DMA_PERIPHERALS_INFO = {
    "DMA1": {"rcc_macro": "RCC_AHB1ENR_DMA1EN", "streams": 8},
    "DMA2": {"rcc_macro": "RCC_AHB1ENR_DMA2EN", "streams": 8}
}

DMA_DIRECTIONS = {"Peripheral to Memory": 0b00, "Memory to Peripheral": 0b01, "Memory to Memory": 0b10}
DMA_MODES = {"Normal": 0, "Circular": 1, "Peripheral Flow Control": 2}
DMA_INCREMENT_MODES = {"Fixed": 0, "Increment": 1}
DMA_DATA_SIZES = {"Byte (8-bit)": 0b00, "Half-Word (16-bit)": 0b01, "Word (32-bit)": 0b10}
DMA_PRIORITIES = {"Low": 0b00, "Medium": 0b01, "High": 0b10, "Very High": 0b11}
DMA_FIFO_MODES = {"Direct Mode (FIFO Disabled)": 0, "FIFO Enabled": 1}
DMA_FIFO_THRESHOLDS = {"1/4 Full": 0b00, "1/2 Full": 0b01, "3/4 Full": 0b10, "Full": 0b11}

DMA_PERIPHERAL_MAP_F407VG = {
    "ADC1": ("DMA2", 0, 0),
    "SPI1_RX": ("DMA2", 0, 3),
    "SPI1_TX": ("DMA2", 3, 3),
    "SPI2_RX": ("DMA1", 3, 0),
    "SPI2_TX": ("DMA1", 4, 0),
    "I2C1_RX": ("DMA1", 0, 1),
    "I2C1_TX": ("DMA1", 6, 1),
    "USART1_RX": ("DMA2", 2, 4),
    "USART1_TX": ("DMA2", 7, 4),
    "USART2_RX": ("DMA1", 5, 4),
    "USART2_TX": ("DMA1", 6, 4),
    "MEM_TO_MEM_DMA2_S0": ("DMA2", 0, "M2M"),
    "MEM_TO_MEM_DMA1_S0": ("DMA1", 0, "M2M")
}
DMA_AVAILABLE_PERIPHERALS_FOR_DMA = list(DMA_PERIPHERAL_MAP_F407VG.keys())

RCC_AHB1ENR_DMA1EN_Pos = 21
RCC_AHB1ENR_DMA1EN = (1 << RCC_AHB1ENR_DMA1EN_Pos)
RCC_AHB1ENR_DMA2EN_Pos = 22
RCC_AHB1ENR_DMA2EN = (1 << RCC_AHB1ENR_DMA2EN_Pos)

# --- DAC DEFINES ---
DAC_PERIPHERALS_INFO = {
    "DAC1": {"rcc_macro": "RCC_APB1ENR_DACEN"},
}
DAC_CR_EN1_Pos = 0; DAC_CR_EN1 = (1 << DAC_CR_EN1_Pos)
DAC_CR_BOFF1_Pos = 1; DAC_CR_BOFF1 = (1 << DAC_CR_BOFF1_Pos)
DAC_CR_TEN1_Pos = 2; DAC_CR_TEN1 = (1 << DAC_CR_TEN1_Pos)
DAC_CR_TSEL1_Pos = 3; DAC_CR_TSEL1_Msk = (0x7 << DAC_CR_TSEL1_Pos)
DAC_CR_WAVE1_Pos = 6; DAC_CR_WAVE1_Msk = (0x3 << DAC_CR_WAVE1_Pos)
DAC_CR_MAMP1_Pos = 8; DAC_CR_MAMP1_Msk = (0xF << DAC_CR_MAMP1_Pos)
DAC_CR_DMAEN1_Pos = 12; DAC_CR_DMAEN1 = (1 << DAC_CR_DMAEN1_Pos)
DAC_CR_EN2_Pos = 16; DAC_CR_EN2 = (1 << DAC_CR_EN2_Pos)

DAC_TRIGGER_SOURCES = {
    "Software": 0b111,
    "TIM6_TRGO": 0b000,
    "TIM8_TRGO": 0b001,
    "TIM7_TRGO": 0b010,
    "TIM5_TRGO": 0b011,
    "TIM2_TRGO": 0b100,
    "TIM4_TRGO": 0b101,
    "EXTI_Line9": 0b110
}
DAC_WAVE_GENERATION = {"Disabled": 0b00, "Noise": 0b01, "Triangle": 0b10}
DAC_OUTPUT_BUFFER_OPTIONS = {"Enabled": 0, "Disabled (High Impedance)": 1}
DAC_DATA_ALIGNMENTS = {"8-bit Right": 0, "12-bit Left": 1, "12-bit Right": 2}
DAC_OUTPUT_PINS = {
    "STM32F407VG": {"DAC_OUT1": "PA4", "DAC_OUT2": "PA5"},
    "STM32F429ZI": {"DAC_OUT1": "PA4", "DAC_OUT2": "PA5"},
    "STM32F446RE": {"DAC_OUT1": "PA4", "DAC_OUT2": "PA5"},
}

RCC_APB1ENR_DACEN_Pos = 29
RCC_APB1ENR_DACEN = (1 << RCC_APB1ENR_DACEN_Pos)