# Clock Source Frequencies (RM0033)
HSI_VALUE_HZ = 16000000  # Internal 16 MHz RC oscillator
HSE_DEFAULT_HZ = 8000000  # Default external crystal (can be 4-26 MHz for F2)

# PLL Parameters for STM32F2xx (RM0033 - RCC_PLLCFGR)
# VCO_IN = HSE_OR_HSI / PLLM  (must be 1-2 MHz, typically 1MHz or 2MHz)
# VCO_OUT = VCO_IN * PLLN     (must be 192-432 MHz)
# SYSCLK = VCO_OUT / PLLP
# USB OTG FS, SDIO, RNG clk = VCO_OUT / PLLQ (PLLQ >= 2)

PLLM_MIN = 2;
PLLM_MAX = 63  # Bits 5:0
PLLN_MIN_GENERAL = 192; # RM0033 Table 20 (fVCO_OUT range) implies N should result in 192-432MHz VCO_OUT
PLLN_MAX_GENERAL = 432
PLLN_MIN_F2 = PLLN_MIN_GENERAL # Alias for consistency if specific F2 values differ later
PLLN_MAX_F2 = PLLN_MAX_GENERAL
PLLP_VALUES = [2, 4, 6, 8]  # Bits 17:16 (00: /2, 01: /4, 10: /6, 11: /8)
PLLQ_MIN = 2;
PLLQ_MAX = 15  # Bits 27:24

# VCO Frequencies (RM0033 Table 20)
VCO_INPUT_MIN_HZ = 1000000;
VCO_INPUT_MAX_HZ = 2000000  # Recommended range for PLLM division
VCO_OUTPUT_MIN_HZ = 192000000; # f_VCO_OUT for main PLL
VCO_OUTPUT_MAX_HZ = 432000000

# Max Clock Frequencies (STM32F20x/F21x, VDD=2.7-3.6V, RM0033 Table 19)
SYSCLK_MAX_HZ_F2 = 120000000
HCLK_MAX_HZ_F2 = SYSCLK_MAX_HZ_F2
PCLK1_MAX_HZ_F2 = 30000000  # APB1
PCLK2_MAX_HZ_F2 = 60000000  # APB2
ADC_CLK_MAX_HZ_F2 = 30000000  # PCLK2 divided by ADCPRE (min /2 => 60/2=30MHz)

# Prescaler Maps (RCC_CFGR bits - same as F4 for these)
AHB_PRESCALER_MAP = {  # HPRE bits 7:4 (used for F2 as well)
    1: 0b0000, 2: 0b1000, 4: 0b1001, 8: 0b1010,
    16: 0b1011, 64: 0b1100, 128: 0b1101, 256: 0b1110,
    512: 0b1111
}
APB_PRESCALER_MAP = {  # PPRE1 bits 12:10, PPRE2 bits 15:13 (used for F2 as well)
    1: 0b000, 2: 0b100, 4: 0b101, 8: 0b110, 16: 0b111
}

# Flash Latency (FLASH_ACR register, LATENCY bits)
# For STM32F20x/F21x (VDD = 2.7V to 3.6V, RM0033 Table 6):
FLASH_LATENCY_F2_MAP = {
    # WS: (min_hclk_excl_Hz, max_hclk_incl_Hz) -> Use direct Hz values
    0: (0, 30000000),
    1: (30000000, 60000000),
    2: (60000000, 90000000),
    3: (90000000, 120000000),
}

TARGET_DEVICES_F2 = {
    "STM32F205VC": {  # Example F2 device
        "cmsis_header": "stm32f2xx.h",
        "max_sysclk_hz": SYSCLK_MAX_HZ_F2,
        "max_hclk_hz": HCLK_MAX_HZ_F2,
        "max_pclk1_hz": PCLK1_MAX_HZ_F2,
        "max_pclk2_hz": PCLK2_MAX_HZ_F2,
        "adc_clk_max_hz": ADC_CLK_MAX_HZ_F2,
        "flash_latency_config": FLASH_LATENCY_F2_MAP,
        "usart_instances": ["USART1", "USART2", "USART3", "UART4", "UART5", "USART6"],
        "timer_instances": ["TIM1", "TIM2", "TIM3", "TIM4", "TIM5", "TIM6", "TIM7", "TIM8", "TIM9", "TIM10", "TIM11",
                            "TIM12", "TIM13", "TIM14"],
        "i2c_instances": ["I2C1", "I2C2", "I2C3"],
        "spi_instances": ["SPI1", "SPI2", "SPI3"],  # SPI3 can be I2S3
        "can_instances": ["CAN1", "CAN2"],
        "adc_instances": ["ADC1", "ADC2", "ADC3"],
        "dac_instances": ["DAC1"],  # DAC block with 2 channels
        "dma_controllers": ["DMA1", "DMA2"],  # DMA1: 8 streams, DMA2: 8 streams
        "watchdog_instances": ["IWDG", "WWDG"],
        "gpio_ports": ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],  # Up to port I
    },
    "STM32F207VG": {  # Similar, often more features like Ethernet
        "cmsis_header": "stm32f2xx.h",
        "max_sysclk_hz": SYSCLK_MAX_HZ_F2,
        "max_hclk_hz": HCLK_MAX_HZ_F2,
        "max_pclk1_hz": PCLK1_MAX_HZ_F2,
        "max_pclk2_hz": PCLK2_MAX_HZ_F2,
        "adc_clk_max_hz": ADC_CLK_MAX_HZ_F2,
        "flash_latency_config": FLASH_LATENCY_F2_MAP,
        "usart_instances": ["USART1", "USART2", "USART3", "UART4", "UART5", "USART6"],
        "timer_instances": ["TIM1", "TIM2", "TIM3", "TIM4", "TIM5", "TIM6", "TIM7", "TIM8", "TIM9", "TIM10", "TIM11",
                            "TIM12", "TIM13", "TIM14"],
        "i2c_instances": ["I2C1", "I2C2", "I2C3"],
        "spi_instances": ["SPI1", "SPI2", "SPI3"],
        "can_instances": ["CAN1", "CAN2"],
        "adc_instances": ["ADC1", "ADC2", "ADC3"],
        "dac_instances": ["DAC1"],
        "dma_controllers": ["DMA1", "DMA2"],
        "watchdog_instances": ["IWDG", "WWDG"],
        "gpio_ports": ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
    },
}


def get_f2_flash_latency(hclk_freq_hz, target_device_id,
                         vos_scale_id=None):  # vos_scale_id not used for F2 latency tables
    device_info = TARGET_DEVICES_F2.get(target_device_id)
    latency_map_to_use = FLASH_LATENCY_F2_MAP
    if device_info and "flash_latency_config" in device_info:
        latency_map_to_use = device_info["flash_latency_config"]

    hclk_mhz_int = int(hclk_freq_hz)
    for ws, (min_hz_excl, max_hz_incl) in latency_map_to_use.items():
        if hclk_mhz_int > min_hz_excl and hclk_mhz_int <= max_hz_incl:
            return ws
    if hclk_mhz_int <= latency_map_to_use.get(0, (0, 0))[1]: return 0

    return max(latency_map_to_use.keys()) if latency_map_to_use else 3


# --- RCC Register Bits (Common for F2 - RM0033) ---
# RCC_CR
RCC_CR_HSION_Pos = 0;
RCC_CR_HSIRDY_Pos = 1;
RCC_CR_HSEON_Pos = 16;
RCC_CR_HSERDY_Pos = 17;
RCC_CR_HSEBYP_Pos = 18;
RCC_CR_CSSON_Pos = 19;
RCC_CR_PLLON_Pos = 24;
RCC_CR_PLLRDY_Pos = 25;
RCC_CR_PLLI2SON_Pos = 26;
RCC_CR_PLLI2SRDY_Pos = 27;

# RCC_PLLCFGR (F2 specific fields if different from F4, for main PLL they are similar)
RCC_PLLCFGR_PLLM_Pos = 0;
RCC_PLLCFGR_PLLM_Msk = (0x3F << RCC_PLLCFGR_PLLM_Pos);
RCC_PLLCFGR_PLLN_Pos = 6;
RCC_PLLCFGR_PLLN_Msk = (0x1FF << RCC_PLLCFGR_PLLN_Pos);  # 9 bits for N
RCC_PLLCFGR_PLLP_Pos = 16;
RCC_PLLCFGR_PLLP_Msk = (0x3 << RCC_PLLCFGR_PLLP_Pos);
RCC_PLLCFGR_PLLSRC_Pos = 22;
RCC_PLLCFGR_PLLSRC = (1 << RCC_PLLCFGR_PLLSRC_Pos);  # 0: HSI, 1: HSE
RCC_PLLCFGR_PLLQ_Pos = 24;
RCC_PLLCFGR_PLLQ_Msk = (0xF << RCC_PLLCFGR_PLLQ_Pos);

# RCC_CFGR
RCC_CFGR_SW_Pos = 0;
RCC_CFGR_SWS_Pos = 2;
RCC_CFGR_HPRE_Pos = 4;
RCC_CFGR_PPRE1_Pos = 10;
RCC_CFGR_PPRE2_Pos = 13;
RCC_CFGR_RTCPRE_Pos = 16;
RCC_CFGR_MCO1_Pos = 21;
RCC_CFGR_MCO1PRE_Pos = 24;
RCC_CFGR_MCO2_Pos = 30;
RCC_CFGR_MCO2PRE_Pos = 27;

# FLASH_ACR (F2 specific - RM0033)
FLASH_ACR_LATENCY_Pos = 0;
FLASH_ACR_LATENCY_Msk = 0xF;
FLASH_ACR_PRFTEN_Pos = 8;
FLASH_ACR_PRFTEN = (1 << FLASH_ACR_PRFTEN_Pos);
FLASH_ACR_ICEN_Pos = 9;
FLASH_ACR_ICEN = (1 << FLASH_ACR_ICEN_Pos);
FLASH_ACR_DCEN_Pos = 10;
FLASH_ACR_DCEN = (1 << FLASH_ACR_DCEN_Pos);
FLASH_ACR_ICRST_Pos = 11;
FLASH_ACR_ICRST = (1 << FLASH_ACR_ICRST_Pos);
FLASH_ACR_DCRST_Pos = 12;
FLASH_ACR_DCRST = (1 << FLASH_ACR_DCRST_Pos);

RCC_APB1ENR_PWREN_Pos = 28;
RCC_APB1ENR_PWREN = (1 << RCC_APB1ENR_PWREN_Pos)

# --- GPIO Defines for F2 (Similar to F4) ---
GPIO_MAX_PORT_CHAR_F2 = 'I'

# --- ADC Defines for F2 (Similar to F4 for basic setup) ---
ADC_CHANNELS_MAP_STM32F2 = { # Default, can be overridden by device-specific map
    f"IN{i}": i for i in range(16)
} | {"TEMP": 16, "VREFINT": 17, "VBAT": 18}

ADC_PIN_MAP_STM32F207VG = { # Example, replace with actual map if needed
    "IN0":  {"port": 'A', "pin": 0}, "IN1":  {"port": 'A', "pin": 1},
    "IN2":  {"port": 'A', "pin": 2}, "IN3":  {"port": 'A', "pin": 3},
    "IN4":  {"port": 'A', "pin": 4}, "IN5":  {"port": 'A', "pin": 5},
    "IN6":  {"port": 'A', "pin": 6}, "IN7":  {"port": 'A', "pin": 7},
    "IN8":  {"port": 'B', "pin": 0}, "IN9":  {"port": 'B', "pin": 1},
    "IN10": {"port": 'C', "pin": 0}, "IN11": {"port": 'C', "pin": 1},
    "IN12": {"port": 'C', "pin": 2}, "IN13": {"port": 'C', "pin": 3},
    "IN14": {"port": 'C', "pin": 4}, "IN15": {"port": 'C', "pin": 5},
}

ADC_SAMPLING_TIMES_F2 = ["3 cycles", "15 cycles", "28 cycles", "56 cycles", "84 cycles", "112 cycles", "144 cycles", "480 cycles"]
ADC_SAMPLING_TIME_VAL_MAP_F2 = {st: i for i, st in enumerate(ADC_SAMPLING_TIMES_F2)}
ADC_PRESCALERS_F2 = ["PCLK2 / 2", "PCLK2 / 4", "PCLK2 / 6", "PCLK2 / 8"]
ADC_PRESCALER_VAL_MAP_F2 = {"PCLK2 / 2":0b00, "PCLK2 / 4":0b01, "PCLK2 / 6":0b10, "PCLK2 / 8":0b11}
ADC_RESOLUTIONS_F2 = ["12-bit", "10-bit", "8-bit", "6-bit"]
ADC_RESOLUTION_VAL_MAP_F2 = {"12-bit":0b00, "10-bit":0b01, "8-bit":0b10, "6-bit":0b11}
ADC_EXT_TRIG_EDGE_F2 = ["Disabled", "Rising Edge", "Falling Edge", "Both Edges"]
ADC_EXT_TRIG_EDGE_VAL_MAP_F2 = {"Disabled":0b00, "Rising Edge":0b01, "Falling Edge":0b10, "Both Edges":0b11}
ADC_EXT_TRIG_REGULAR_F2 = ["Software", "TIM1_CC1", "TIM1_CC2", "TIM1_CC3", "TIM2_CC2", "TIM2_CC3", "TIM2_CC4", "TIM2_TRGO", "TIM3_CC1", "TIM3_TRGO", "TIM4_CC4", "TIM5_CC1", "TIM5_CC2", "TIM5_CC3", "TIM8_CC1", "TIM8_TRGO", "EXTI_11"]
ADC_EXT_TRIG_SOURCE_VAL_MAP_F2 = {src: i for i, src in enumerate(ADC_EXT_TRIG_REGULAR_F2[1:])} # Software handled by disabled edge
ADC_EXT_TRIG_SOURCE_VAL_MAP_F2["Software"] = -1 # Special handling for no trigger

# ADC_CCR bits (ADCPRE is in CCR for F2)
ADC_CCR_ADCPRE_Pos = 16; ADC_CCR_ADCPRE_Msk = (0x3 << ADC_CCR_ADCPRE_Pos)
ADC_CCR_VBATE_Pos = 22; ADC_CCR_VBATE = (1 << ADC_CCR_VBATE_Pos)
ADC_CCR_TSVREFE_Pos = 23; ADC_CCR_TSVREFE = (1 << ADC_CCR_TSVREFE_Pos)
ADC_CCR_MULTI_Pos = 0; ADC_CCR_MULTI_Msk = (0x1F << ADC_CCR_MULTI_Pos)

# --- USART Defines for F2 (Largely similar to F4) ---
USART_PERIPHERALS_INFO_F2 = {
    "USART1": {"bus": "APB2", "rcc_macro": "RCC_APB2ENR_USART1EN"},
    "USART2": {"bus": "APB1", "rcc_macro": "RCC_APB1ENR_USART2EN"},
    "USART3": {"bus": "APB1", "rcc_macro": "RCC_APB1ENR_USART3EN"},
    "UART4": {"bus": "APB1", "rcc_macro": "RCC_APB1ENR_UART4EN"},
    "UART5": {"bus": "APB1", "rcc_macro": "RCC_APB1ENR_UART5EN"},
    "USART6": {"bus": "APB2", "rcc_macro": "RCC_APB2ENR_USART6EN"},
}
USART_OVERSAMPLING_MAP_F2 = {"16": 0}

# --- Timer Defines for F2 ---
TIMER_PERIPHERALS_INFO_F2 = {
    "TIM1": {"type": "ADV", "bus": "APB2", "rcc_macro": "RCC_APB2ENR_TIM1EN", "max_channels": 4, "has_bdtr": True, "is_16bit": True},
    "TIM2": {"type": "GP32", "bus": "APB1", "rcc_macro": "RCC_APB1ENR_TIM2EN", "max_channels": 4, "has_bdtr": False, "is_16bit": False},
    "TIM3": {"type": "GP16", "bus": "APB1", "rcc_macro": "RCC_APB1ENR_TIM3EN", "max_channels": 4, "has_bdtr": False, "is_16bit": True},
    "TIM4": {"type": "GP16", "bus": "APB1", "rcc_macro": "RCC_APB1ENR_TIM4EN", "max_channels": 4, "has_bdtr": False, "is_16bit": True},
    "TIM5": {"type": "GP32", "bus": "APB1", "rcc_macro": "RCC_APB1ENR_TIM5EN", "max_channels": 4, "has_bdtr": False, "is_16bit": False},
    "TIM6": {"type": "BASIC", "bus": "APB1", "rcc_macro": "RCC_APB1ENR_TIM6EN", "max_channels": 0, "has_bdtr": False, "is_16bit": True},
    "TIM7": {"type": "BASIC", "bus": "APB1", "rcc_macro": "RCC_APB1ENR_TIM7EN", "max_channels": 0, "has_bdtr": False, "is_16bit": True},
    "TIM8": {"type": "ADV", "bus": "APB2", "rcc_macro": "RCC_APB2ENR_TIM8EN", "max_channels": 4, "has_bdtr": True, "is_16bit": True},
    "TIM9": {"type": "GP16", "bus": "APB2", "rcc_macro": "RCC_APB2ENR_TIM9EN", "max_channels": 2, "has_bdtr": False, "is_16bit": True},
    "TIM10": {"type": "GP16", "bus": "APB2", "rcc_macro": "RCC_APB2ENR_TIM10EN", "max_channels": 1, "has_bdtr": False, "is_16bit": True},
    "TIM11": {"type": "GP16", "bus": "APB2", "rcc_macro": "RCC_APB2ENR_TIM11EN", "max_channels": 1, "has_bdtr": False, "is_16bit": True},
    "TIM12": {"type": "GP16", "bus": "APB1", "rcc_macro": "RCC_APB1ENR_TIM12EN", "max_channels": 2, "has_bdtr": False, "is_16bit": True},
    "TIM13": {"type": "GP16", "bus": "APB1", "rcc_macro": "RCC_APB1ENR_TIM13EN", "max_channels": 1, "has_bdtr": False, "is_16bit": True},
    "TIM14": {"type": "GP16", "bus": "APB1", "rcc_macro": "RCC_APB1ENR_TIM14EN", "max_channels": 1, "has_bdtr": False, "is_16bit": True},
}

# --- I2C Defines for F2 (Largely similar to F4 for basic setup) ---
I2C_PERIPHERALS_INFO_F2 = {
    "I2C1": {"bus": "APB1", "rcc_macro": "RCC_APB1ENR_I2C1EN"},
    "I2C2": {"bus": "APB1", "rcc_macro": "RCC_APB1ENR_I2C2EN"},
    "I2C3": {"bus": "APB1", "rcc_macro": "RCC_APB1ENR_I2C3EN"},
}
I2C_MIN_PCLK_MHZ_F2 = 2

# --- SPI Defines for F2 (Largely similar to F4 for basic setup) ---
SPI_PERIPHERALS_INFO_F2 = {
    "SPI1": {"bus": "APB2", "rcc_macro": "RCC_APB2ENR_SPI1EN"},
    "SPI2": {"bus": "APB1", "rcc_macro": "RCC_APB1ENR_SPI2EN"},
    "SPI3": {"bus": "APB1", "rcc_macro": "RCC_APB1ENR_SPI3EN"},
}

# --- DMA Defines for F2 ---
DMA_PERIPHERALS_INFO_F2 = {
    "DMA1": {"rcc_macro": "RCC_AHB1ENR_DMA1EN", "streams": 8},
    "DMA2": {"rcc_macro": "RCC_AHB1ENR_DMA2EN", "streams": 8}
}

# --- DAC Defines for F2 ---
DAC_PERIPHERALS_INFO_F2 = {
    "DAC1": {"rcc_macro": "RCC_APB1ENR_DACEN", "channels": 2},
}
DAC_OUTPUT_PINS_F2 = {
    "STM32F205VC": {"DAC_OUT1": "PA4", "DAC_OUT2": "PA5"},
    "STM32F207VG": {"DAC_OUT1": "PA4", "DAC_OUT2": "PA5"},
}