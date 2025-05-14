# --- NEW FILE core/stm32f1_defines.py ---

# Clock Source Frequencies
HSI_VALUE_HZ = 8000000  # Internal 8 MHz RC oscillator
HSE_DEFAULT_HZ = 8000000 # Default external crystal frequency (can be different, typically 4-16 MHz for F103, up to 25MHz for F100)

# PLL Parameters for STM32F101xx, STM32F102xx, STM32F103xx (RM0008 - RCC_CFGR)
# PLLSRC: HSE or HSI/2 (Bit 16 RCC_CFGR_PLLSRC)
# PLLXTPRE: HSE or HSE/2 (for HSE as PLLSRC) (Bit 17 RCC_CFGR_PLLXTPRE)
# PLLMUL: x2 to x16 (Bits 21:18 RCC_CFGR_PLLMULL)
PLLMUL_MAP_F1 = { # value: register_bits
    2:0b0000, 3:0b0001, 4:0b0010, 5:0b0011, 6:0b0100, 7:0b0101, 8:0b0110, 9:0b0111,
    10:0b1000, 11:0b1001, 12:0b1010, 13:0b1011, 14:0b1100, 15:0b1101, 16:0b1110,
    # 16 is also 0b1111 for some devices, check specific variant if using PLLMUL_16_alt
}
PLLMUL_MIN = 2; PLLMUL_MAX = 16 # User-facing values
PLLXTPRE_VALUES = [1, 2] # Divisor for HSE before PLL (1=not divided, 2=divided by 2)

# Max Clock Frequencies (STM32F103xx Performance Line, VDD=2.0-3.6V, RM0008 Table 10)
SYSCLK_MAX_HZ_F103 = 72000000
HCLK_MAX_HZ_F103 = SYSCLK_MAX_HZ_F103
PCLK1_MAX_HZ_F103 = 36000000  # APB1 Low-speed
PCLK2_MAX_HZ_F103 = 72000000  # APB2 High-speed (includes GPIOs, ADC, TIM1, SPI1, USART1)
ADC_CLK_MAX_HZ_F103 = 14000000 # ADC clock is from PCLK2 divided by ADCPRE (2,4,6,8)

# Max Clock Frequencies for STM32F100xx Value Line (RM0041 Table 7)
SYSCLK_MAX_HZ_F100 = 24000000
HCLK_MAX_HZ_F100 = SYSCLK_MAX_HZ_F100
PCLK1_MAX_HZ_F100 = 24000000
PCLK2_MAX_HZ_F100 = 24000000
ADC_CLK_MAX_HZ_F100 = 12000000 # Check specific datasheet, often PCLK2/2 (max 24/2 = 12MHz)

# Prescaler Maps (to register bits for RCC_CFGR)
# HPRE bits (AHB prescaler)
AHB_PRESCALER_MAP_F1 = {
    1:   0b0000, 2:   0b1000, 4:   0b1001, 8:   0b1010,
    16:  0b1011, 64:  0b1100, 128: 0b1101, 256: 0b1110,
    512: 0b1111
}
# PPRE1, PPRE2 bits (APB prescalers)
APB_PRESCALER_MAP_F1 = {
    1:  0b000, 2:  0b100, 4:  0b101, 8:  0b110, 16: 0b111
}

# Flash Latency (FLASH_ACR register, LATENCY bits)
# Value is WS count (0 for 0 WS, 1 for 1 WS, 2 for 2 WS)
# For STM32F103xx Performance Line (RM0008 Table 5):
FLASH_LATENCY_F103_MAP = {
    # WS: (min_hclk_excl, max_hclk_incl)
    0: (0, 24000000),
    1: (24000000, 48000000),
    2: (48000000, 72000000)
}
# For STM32F100xx Value Line (RM0041 Table 3):
FLASH_LATENCY_F100_MAP = {
    0: (0, 24000000), # 0 WS up to 24 MHz
}


TARGET_DEVICES_F1 = {
    "STM32F103C8": {
        "cmsis_header": "stm32f10x.h", # Or specific like stm32f103xb.h
        "max_sysclk_hz": SYSCLK_MAX_HZ_F103,
        "max_hclk_hz": HCLK_MAX_HZ_F103,
        "max_pclk1_hz": PCLK1_MAX_HZ_F103,
        "max_pclk2_hz": PCLK2_MAX_HZ_F103,
        "adc_clk_max_hz": ADC_CLK_MAX_HZ_F103,
        "flash_latency_config": FLASH_LATENCY_F103_MAP,
        "usart_instances": ["USART1", "USART2", "USART3"],
        "timer_instances": ["TIM1", "TIM2", "TIM3", "TIM4"], # General purpose + Advanced
        "i2c_instances": ["I2C1", "I2C2"],
        "spi_instances": ["SPI1", "SPI2"],
        "can_instances": ["CAN1"],
        "adc_instances": ["ADC1", "ADC2"],
        "dac_instances": [],
        "dma_controllers": ["DMA1"], # DMA1: 7 channels
        "watchdog_instances": ["IWDG", "WWDG"],
        "gpio_ports": ['A', 'B', 'C', 'D', 'E'], # Example, check datasheet for specific package
    },
    "STM32F103RB": { # Similar to C8 but more memory/pins
        "cmsis_header": "stm32f10x.h",
        "max_sysclk_hz": SYSCLK_MAX_HZ_F103,
        "max_hclk_hz": HCLK_MAX_HZ_F103,
        "max_pclk1_hz": PCLK1_MAX_HZ_F103,
        "max_pclk2_hz": PCLK2_MAX_HZ_F103,
        "adc_clk_max_hz": ADC_CLK_MAX_HZ_F103,
        "flash_latency_config": FLASH_LATENCY_F103_MAP,
        "usart_instances": ["USART1", "USART2", "USART3"],
        "timer_instances": ["TIM1", "TIM2", "TIM3", "TIM4"],
        "i2c_instances": ["I2C1", "I2C2"],
        "spi_instances": ["SPI1", "SPI2"],
        "can_instances": ["CAN1"],
        "adc_instances": ["ADC1", "ADC2"],
        "dac_instances": [],
        "dma_controllers": ["DMA1"],
        "watchdog_instances": ["IWDG", "WWDG"],
        "gpio_ports": ['A', 'B', 'C', 'D', 'E', 'F', 'G'], # Larger packages
    },
    "STM32F100RB": { # Value Line example
        "cmsis_header": "stm32f10x.h", # Or stm32f100xb.h
        "max_sysclk_hz": SYSCLK_MAX_HZ_F100,
        "max_hclk_hz": HCLK_MAX_HZ_F100,
        "max_pclk1_hz": PCLK1_MAX_HZ_F100,
        "max_pclk2_hz": PCLK2_MAX_HZ_F100,
        "adc_clk_max_hz": ADC_CLK_MAX_HZ_F100,
        "flash_latency_config": FLASH_LATENCY_F100_MAP,
        "usart_instances": ["USART1", "USART2", "USART3"], # Check RM0041
        "timer_instances": ["TIM2", "TIM3", "TIM4", "TIM6", "TIM7", "TIM15", "TIM16", "TIM17"], # TIM1 not on all F100
        "i2c_instances": ["I2C1", "I2C2"], # I2C2 on some
        "spi_instances": ["SPI1", "SPI2"],   # SPI2 on some
        "adc_instances": ["ADC1"],
        "dac_instances": ["DAC1"], # DAC on value line
        "dma_controllers": ["DMA1"], # DMA1: 7 channels
        "watchdog_instances": ["IWDG", "WWDG"],
        "gpio_ports": ['A', 'B', 'C', 'D', 'E'], # Check specific package
    },
}

def get_f1_flash_latency(hclk_freq_hz, target_device_id):
    device_info = TARGET_DEVICES_F1.get(target_device_id)
    if not device_info or "flash_latency_config" not in device_info:
        # Fallback if device or config not found (should not happen if target_device_id is valid)
        latency_map_fallback = FLASH_LATENCY_F103_MAP # Default to F103 performance line
        if "STM32F100" in target_device_id:
            latency_map_fallback = FLASH_LATENCY_F100_MAP
        for ws, (min_excl, max_incl) in latency_map_fallback.items():
            if hclk_freq_hz > min_excl and hclk_freq_hz <= max_incl: return ws
        return max(latency_map_fallback.keys())


# --- RCC Register Bits (Common for F1) ---
# RCC_CR
RCC_CR_HSION_Pos = 0; RCC_CR_HSION = (1 << RCC_CR_HSION_Pos)
RCC_CR_HSIRDY_Pos = 1; RCC_CR_HSIRDY = (1 << RCC_CR_HSIRDY_Pos)
RCC_CR_HSITRIM_Pos = 3; RCC_CR_HSITRIM_Msk = (0x1F << RCC_CR_HSITRIM_Pos)
RCC_CR_HSICAL_Pos = 8; RCC_CR_HSICAL_Msk = (0xFF << RCC_CR_HSICAL_Pos)
RCC_CR_HSEON_Pos = 16; RCC_CR_HSEON = (1 << RCC_CR_HSEON_Pos)
RCC_CR_HSERDY_Pos = 17; RCC_CR_HSERDY = (1 << RCC_CR_HSERDY_Pos)
RCC_CR_HSEBYP_Pos = 18; RCC_CR_HSEBYP = (1 << RCC_CR_HSEBYP_Pos)
RCC_CR_CSSON_Pos = 19; RCC_CR_CSSON = (1 << RCC_CR_CSSON_Pos) # Clock Security System Enable
RCC_CR_PLLON_Pos = 24; RCC_CR_PLLON = (1 << RCC_CR_PLLON_Pos)
RCC_CR_PLLRDY_Pos = 25; RCC_CR_PLLRDY = (1 << RCC_CR_PLLRDY_Pos)

# RCC_CFGR
RCC_CFGR_SW_Pos = 0; RCC_CFGR_SW_Msk = (0x3 << RCC_CFGR_SW_Pos) # System clock Switch
RCC_CFGR_SWS_Pos = 2; RCC_CFGR_SWS_Msk = (0x3 << RCC_CFGR_SWS_Pos) # System clock Switch Status
RCC_CFGR_HPRE_Pos = 4; RCC_CFGR_HPRE_Msk = (0xF << RCC_CFGR_HPRE_Pos) # AHB prescaler
RCC_CFGR_PPRE1_Pos = 8; RCC_CFGR_PPRE1_Msk = (0x7 << RCC_CFGR_PPRE1_Pos) # APB1 prescaler
RCC_CFGR_PPRE2_Pos = 11; RCC_CFGR_PPRE2_Msk = (0x7 << RCC_CFGR_PPRE2_Pos) # APB2 prescaler
RCC_CFGR_ADCPRE_Pos = 14; RCC_CFGR_ADCPRE_Msk = (0x3 << RCC_CFGR_ADCPRE_Pos) # ADC prescaler
RCC_CFGR_PLLSRC_F1_Pos = 16; RCC_CFGR_PLLSRC_F1 = (1 << RCC_CFGR_PLLSRC_F1_Pos) # PLL entry clock source
RCC_CFGR_PLLXTPRE_F1_Pos = 17; RCC_CFGR_PLLXTPRE_F1 = (1 << RCC_CFGR_PLLXTPRE_F1_Pos) # HSE divider for PLL entry
RCC_CFGR_PLLMULL_F1_Pos = 18; RCC_CFGR_PLLMULL_F1_Msk = (0xF << RCC_CFGR_PLLMULL_F1_Pos) # PLL multiplication factor
RCC_CFGR_USBPRE_Pos = 22; RCC_CFGR_USBPRE = (1 << RCC_CFGR_USBPRE_Pos) # USB prescaler (F103/F102)
RCC_CFGR_MCO_Pos = 24; RCC_CFGR_MCO_Msk = (0x7 << RCC_CFGR_MCO_Pos) # Microcontroller clock output

# RCC_APB1ENR, RCC_APB2ENR, RCC_AHBENR - Bit positions for peripheral clocks
RCC_APB2ENR_AFIOEN_Pos = 0; RCC_APB2ENR_AFIOEN = (1 << RCC_APB2ENR_AFIOEN_Pos)
RCC_APB2ENR_IOPAEN_Pos = 2; RCC_APB2ENR_IOPAEN = (1 << RCC_APB2ENR_IOPAEN_Pos)
RCC_APB2ENR_IOPBEN_Pos = 3; RCC_APB2ENR_IOPBEN = (1 << RCC_APB2ENR_IOPBEN_Pos)
# ... add other IOPxEN for C,D,E,F,G as needed
RCC_APB2ENR_ADC1EN_Pos = 9;  RCC_APB2ENR_ADC1EN = (1 << RCC_APB2ENR_ADC1EN_Pos)
RCC_APB2ENR_ADC2EN_Pos = 10; RCC_APB2ENR_ADC2EN = (1 << RCC_APB2ENR_ADC2EN_Pos) # Not on all F1
RCC_APB2ENR_TIM1EN_Pos = 11; RCC_APB2ENR_TIM1EN = (1 << RCC_APB2ENR_TIM1EN_Pos)
RCC_APB2ENR_SPI1EN_Pos = 12; RCC_APB2ENR_SPI1EN = (1 << RCC_APB2ENR_SPI1EN_Pos)
RCC_APB2ENR_USART1EN_Pos = 14;RCC_APB2ENR_USART1EN = (1 << RCC_APB2ENR_USART1EN_Pos)

RCC_APB1ENR_TIM2EN_Pos = 0; RCC_APB1ENR_TIM2EN = (1 << RCC_APB1ENR_TIM2EN_Pos)
RCC_APB1ENR_TIM3EN_Pos = 1; RCC_APB1ENR_TIM3EN = (1 << RCC_APB1ENR_TIM3EN_Pos)
RCC_APB1ENR_TIM4EN_Pos = 2; RCC_APB1ENR_TIM4EN = (1 << RCC_APB1ENR_TIM4EN_Pos)
# ... TIM5, TIM6, TIM7 etc for F100/F103 high-density ...
RCC_APB1ENR_SPI2EN_Pos = 14; RCC_APB1ENR_SPI2EN = (1 << RCC_APB1ENR_SPI2EN_Pos)
RCC_APB1ENR_SPI3EN_Pos = 15; RCC_APB1ENR_SPI3EN = (1 << RCC_APB1ENR_SPI3EN_Pos) # On some F1
RCC_APB1ENR_USART2EN_Pos = 17; RCC_APB1ENR_USART2EN = (1 << RCC_APB1ENR_USART2EN_Pos)
RCC_APB1ENR_USART3EN_Pos = 18; RCC_APB1ENR_USART3EN = (1 << RCC_APB1ENR_USART3EN_Pos)
RCC_APB1ENR_UART4EN_Pos = 19; RCC_APB1ENR_UART4EN = (1 << RCC_APB1ENR_UART4EN_Pos) # On some F1
RCC_APB1ENR_UART5EN_Pos = 20; RCC_APB1ENR_UART5EN = (1 << RCC_APB1ENR_UART5EN_Pos) # On some F1
RCC_APB1ENR_I2C1EN_Pos = 21; RCC_APB1ENR_I2C1EN = (1 << RCC_APB1ENR_I2C1EN_Pos)
RCC_APB1ENR_I2C2EN_Pos = 22; RCC_APB1ENR_I2C2EN = (1 << RCC_APB1ENR_I2C2EN_Pos)
RCC_APB1ENR_CAN1EN_Pos = 25; RCC_APB1ENR_CAN1EN = (1 << RCC_APB1ENR_CAN1EN_Pos) # bxCAN
RCC_APB1ENR_DACEN_Pos = 29; RCC_APB1ENR_DACEN = (1 << RCC_APB1ENR_DACEN_Pos) # For F100 value line DAC

RCC_AHBENR_DMA1EN_Pos = 0; RCC_AHBENR_DMA1EN = (1 << RCC_AHBENR_DMA1EN_Pos)
RCC_AHBENR_DMA2EN_Pos = 1; RCC_AHBENR_DMA2EN = (1 << RCC_AHBENR_DMA2EN_Pos) # For high-density F103

# --- FLASH_ACR ---
FLASH_ACR_LATENCY_Pos = 0; FLASH_ACR_LATENCY_Msk = (0x7 << FLASH_ACR_LATENCY_Pos) # Note: F1 has 3 bits for LATENCY (0-2WS)
FLASH_ACR_HLFCYA_Pos = 3; FLASH_ACR_HLFCYA = (1 << FLASH_ACR_HLFCYA_Pos) # Flash half cycle access enable
FLASH_ACR_PRFTBE_Pos = 4; FLASH_ACR_PRFTBE = (1 << FLASH_ACR_PRFTBE_Pos) # Prefetch buffer enable
FLASH_ACR_PRFTBS_Pos = 5; FLASH_ACR_PRFTBS = (1 << FLASH_ACR_PRFTBS_Pos) # Prefetch buffer status

# --- GPIO Defines for F1 (CRL/CRH based) ---
GPIO_F1_MODE_INPUT      = 0b00
GPIO_F1_MODE_OUTPUT_10MHZ = 0b01
GPIO_F1_MODE_OUTPUT_2MHZ  = 0b10
GPIO_F1_MODE_OUTPUT_50MHZ = 0b11

GPIO_F1_CNF_INPUT_ANALOG    = 0b00
GPIO_F1_CNF_INPUT_FLOATING  = 0b01
GPIO_F1_CNF_INPUT_PUPD      = 0b10 # Pull-up / Pull-down selected by ODR bit

GPIO_F1_CNF_OUTPUT_PP       = 0b00
GPIO_F1_CNF_OUTPUT_OD       = 0b01
GPIO_F1_CNF_AF_OUTPUT_PP    = 0b10
GPIO_F1_CNF_AF_OUTPUT_OD    = 0b11

GPIO_F1_MODE_MAP_UI = { # For mapping UI strings to F1 MODE/CNF bits
    "Input Analog":                 {"MODE": GPIO_F1_MODE_INPUT, "CNF": GPIO_F1_CNF_INPUT_ANALOG, "PULL": "NONE"},
    "Input Floating":               {"MODE": GPIO_F1_MODE_INPUT, "CNF": GPIO_F1_CNF_INPUT_FLOATING, "PULL": "NONE"},
    "Input Pull-up":                {"MODE": GPIO_F1_MODE_INPUT, "CNF": GPIO_F1_CNF_INPUT_PUPD, "PULL": "UP"},
    "Input Pull-down":              {"MODE": GPIO_F1_MODE_INPUT, "CNF": GPIO_F1_CNF_INPUT_PUPD, "PULL": "DOWN"},
    "Output Push-pull":             {"CNF_BASE": GPIO_F1_CNF_OUTPUT_PP, "IS_OUTPUT": True},
    "Output Open-drain":            {"CNF_BASE": GPIO_F1_CNF_OUTPUT_OD, "IS_OUTPUT": True},
    "Alternate Function Push-pull": {"CNF_BASE": GPIO_F1_CNF_AF_OUTPUT_PP, "IS_OUTPUT": True, "IS_AF": True},
    "Alternate Function Open-drain":{"CNF_BASE": GPIO_F1_CNF_AF_OUTPUT_OD, "IS_OUTPUT": True, "IS_AF": True},
}
GPIO_F1_SPEED_TO_MODE_BITS_MAP = { # For output modes, maps UI speed string to F1 MODE bits
    "10MHz": GPIO_F1_MODE_OUTPUT_10MHZ,
    "2MHz":  GPIO_F1_MODE_OUTPUT_2MHZ,
    "50MHz": GPIO_F1_MODE_OUTPUT_50MHZ,
}
GPIO_F1_PULL_ODR_MAP = { # For "Input Pull-up/Pull-down", maps UI string to ODR action
    "Pull-up":   {"SET_ODR": True},
    "Pull-down": {"SET_ODR": False}, # Clear ODR bit
}
GPIO_MAX_PORT_CHAR_F1 = 'G' # Can be up to G for F103 high-density, less for others.

# --- ADC Defines for F1 ---
# ADC_CR1
ADC_CR1_AWDCH_Pos = 0;  ADC_CR1_AWDCH_Msk = (0x1F << ADC_CR1_AWDCH_Pos) # Analog watchdog channel select
ADC_CR1_EOCIE_Pos = 5;  ADC_CR1_EOCIE = (1 << ADC_CR1_EOCIE_Pos)     # Interrupt enable for EOC
ADC_CR1_AWDIE_Pos = 6;  ADC_CR1_AWDIE = (1 << ADC_CR1_AWDIE_Pos)     # Analog watchdog interrupt enable
ADC_CR1_JEOCIE_Pos= 7;  ADC_CR1_JEOCIE = (1 << ADC_CR1_JEOCIE_Pos)   # Interrupt enable for JEOC
ADC_CR1_SCAN_Pos = 8;   ADC_CR1_SCAN = (1 << ADC_CR1_SCAN_Pos)       # Scan mode
ADC_CR1_AWDSGL_Pos= 9;  ADC_CR1_AWDSGL = (1 << ADC_CR1_AWDSGL_Pos)   # Enable watchdog on single/all channels
ADC_CR1_JAUTO_Pos = 10; ADC_CR1_JAUTO = (1 << ADC_CR1_JAUTO_Pos)    # Automatic injected group conversion
ADC_CR1_DISCEN_Pos= 11; ADC_CR1_DISCEN = (1 << ADC_CR1_DISCEN_Pos)  # Discontinuous mode on regular channels
ADC_CR1_JDISCEN_Pos=12; ADC_CR1_JDISCEN= (1 << ADC_CR1_JDISCEN_Pos) # Discontinuous mode on injected channels
ADC_CR1_DISCNUM_Pos=13;ADC_CR1_DISCNUM_Msk = (0x7 << ADC_CR1_DISCNUM_Pos) # Discontinuous mode channel count
ADC_CR1_JAWDEN_Pos= 22; ADC_CR1_JAWDEN = (1 << ADC_CR1_JAWDEN_Pos)  # Analog watchdog enable on injected channels
ADC_CR1_AWDEN_Pos = 23; ADC_CR1_AWDEN = (1 << ADC_CR1_AWDEN_Pos)   # Analog watchdog enable on regular channels

# ADC_CR2
ADC_CR2_ADON_Pos = 0; ADC_CR2_ADON = (1 << ADC_CR2_ADON_Pos)        # A/D Converter ON / OFF
ADC_CR2_CONT_Pos = 1; ADC_CR2_CONT = (1 << ADC_CR2_CONT_Pos)        # Continuous conversion
ADC_CR2_CAL_Pos  = 2; ADC_CR2_CAL  = (1 << ADC_CR2_CAL_Pos)         # A/D Calibration
ADC_CR2_RSTCAL_Pos=3; ADC_CR2_RSTCAL=(1 << ADC_CR2_RSTCAL_Pos)     # Reset Calibration
ADC_CR2_DMA_Pos  = 8; ADC_CR2_DMA = (1 << ADC_CR2_DMA_Pos)          # Direct memory access mode
ADC_CR2_ALIGN_Pos= 11; ADC_CR2_ALIGN= (1 << ADC_CR2_ALIGN_Pos)     # Data alignment
ADC_CR2_JEXTSEL_Pos=12;ADC_CR2_JEXTSEL_Msk=(0x7 << ADC_CR2_JEXTSEL_Pos) # External event select for injected group
ADC_CR2_JEXTTRIG_Pos=15;ADC_CR2_JEXTTRIG=(1 << ADC_CR2_JEXTTRIG_Pos)# External trigger conversion mode for injected channels
ADC_CR2_EXTSEL_Pos = 17;ADC_CR2_EXTSEL_Msk=(0x7 << ADC_CR2_EXTSEL_Pos) # External event select for regular group
ADC_CR2_EXTTRIG_Pos= 20;ADC_CR2_EXTTRIG=(1 << ADC_CR2_EXTTRIG_Pos)# External trigger conversion mode for regular channels
ADC_CR2_JSWSTART_Pos=21;ADC_CR2_JSWSTART=(1 << ADC_CR2_JSWSTART_Pos) # Start conversion of injected channels
ADC_CR2_SWSTART_Pos= 22;ADC_CR2_SWSTART=(1 << ADC_CR2_SWSTART_Pos)  # Start conversion of regular channels
ADC_CR2_TSVREFE_Pos=23;ADC_CR2_TSVREFE=(1 << ADC_CR2_TSVREFE_Pos) # Temperature sensor and VREFINT enable

# ADC_SQR1, ADC_SQR2, ADC_SQR3 sequence registers
ADC_SQR1_L_Pos = 20; ADC_SQR1_L_Msk = (0xF << ADC_SQR1_L_Pos) # Regular channel sequence length L[3:0]
# SQx bits are 5-bit wide: SQ1[4:0] to SQ16[4:0]

# ADC_SR status bits
ADC_SR_AWD_Pos = 0;  ADC_SR_AWD = (1 << ADC_SR_AWD_Pos) # Analog watchdog flag
ADC_SR_EOC_Pos = 1;  ADC_SR_EOC = (1 << ADC_SR_EOC_Pos) # End of conversion
ADC_SR_JEOC_Pos= 2;  ADC_SR_JEOC= (1 << ADC_SR_JEOC_Pos)# Injected channel end of conversion
ADC_SR_JSTRT_Pos=3;  ADC_SR_JSTRT=(1 << ADC_SR_JSTRT_Pos)# Injected channel conversion start flag
ADC_SR_STRT_Pos= 4;  ADC_SR_STRT= (1 << ADC_SR_STRT_Pos)# Regular channel conversion start flag
# Note: F1 ADC does not have an OVR bit in SR. Overrun is detected by EOC set and data not read before next conversion.
# Application must clear EOC by reading ADC_DR. If DMA is used, DMA NDF=0 with EOC=1 may indicate overrun.

ADC_CHANNELS_MAP_F1 = { # Example for STM32F103xx, 0-15 are external, 16=TEMP, 17=VREFINT
    "STM32F103C8": {f"IN{i}": i for i in range(10)} | {"TEMP": 16, "VREFINT": 17},
    "STM32F103RB": {f"IN{i}": i for i in range(16)} | {"TEMP": 16, "VREFINT": 17},
    "STM32F100RB": {f"IN{i}": i for i in range(16)} | {"TEMP": 16, "VREFINT": 17},
}
# ADC Pin map (example for STM32F103RB - LQFP64)
ADC_PIN_MAP_STM32F103RB = {
    "IN0":  {"port": 'A', "pin": 0}, "IN1":  {"port": 'A', "pin": 1},
    "IN2":  {"port": 'A', "pin": 2}, "IN3":  {"port": 'A', "pin": 3},
    "IN4":  {"port": 'A', "pin": 4}, "IN5":  {"port": 'A', "pin": 5},
    "IN6":  {"port": 'A', "pin": 6}, "IN7":  {"port": 'A', "pin": 7},
    "IN8":  {"port": 'B', "pin": 0}, "IN9":  {"port": 'B', "pin": 1},
    "IN10": {"port": 'C', "pin": 0}, "IN11": {"port": 'C', "pin": 1},
    "IN12": {"port": 'C', "pin": 2}, "IN13": {"port": 'C', "pin": 3},
    "IN14": {"port": 'C', "pin": 4}, "IN15": {"port": 'C', "pin": 5},
}
ADC_SAMPLING_TIMES_F1 = ["1.5 cycles", "7.5 cycles", "13.5 cycles", "28.5 cycles", "41.5 cycles", "55.5 cycles", "71.5 cycles", "239.5 cycles"]
ADC_SAMPLING_TIME_VAL_MAP_F1 = {st: i for i, st in enumerate(ADC_SAMPLING_TIMES_F1)}

ADC_PRESCALERS_F1 = ["PCLK2 / 2", "PCLK2 / 4", "PCLK2 / 6", "PCLK2 / 8"]
ADC_PRESCALER_VAL_MAP_F1 = {val: i for i, val in enumerate(ADC_PRESCALERS_F1)} # Maps to ADCPRE bits 00,01,10,11

ADC_EXT_TRIG_EDGE_F1 = ["Disabled", "Rising Edge", "Falling Edge", "Both Edges"] # For F1, EXTTRIG is just enable. Edge is part of EXTSEL. This is simplified for UI.
ADC_EXT_TRIG_REGULAR_F1 = ["Software", "TIM1_CC1", "TIM1_CC2", "TIM1_CC3", "TIM2_CC2", "TIM3_TRGO", "TIM4_CC4", "EXTI_11/TIM8_TRGO"] # Regular Conversion
ADC_EXT_TRIG_SOURCE_VAL_MAP_F1 = { # For EXTSEL bits
    "Software": -1, # Special case
    "TIM1_CC1": 0b000, "TIM1_CC2": 0b001, "TIM1_CC3": 0b010,
    "TIM2_CC2": 0b011, "TIM3_TRGO":0b100, "TIM4_CC4": 0b101,
    "EXTI_11/TIM8_TRGO": 0b110 # TIM8_TRGO is on high-density devices, EXTI11 otherwise for this value
    # Note: Bit 0b111 is JSWSTART (software start for injected)
}
ADC_RESOLUTIONS_F1 = ["12-bit"] # F1 ADC is always 12-bit

# --- USART Defines for F1 ---
USART_PERIPHERALS_INFO_F1 = { # Based on RCC enable bits
    "USART1": {"bus": "APB2", "rcc_macro": "RCC_APB2ENR_USART1EN"},
    "USART2": {"bus": "APB1", "rcc_macro": "RCC_APB1ENR_USART2EN"},
    "USART3": {"bus": "APB1", "rcc_macro": "RCC_APB1ENR_USART3EN"},
    "UART4":  {"bus": "APB1", "rcc_macro": "RCC_APB1ENR_UART4EN"}, # On some F1 (e.g., Connectivity Line, high-density)
    "UART5":  {"bus": "APB1", "rcc_macro": "RCC_APB1ENR_UART5EN"}, # On some F1
}
# CR1 bits (USART_CR1)
USART_CR1_SBK_Pos = 0;  USART_CR1_SBK = (1 << USART_CR1_SBK_Pos)   # Send Break
USART_CR1_RWU_Pos = 1;  USART_CR1_RWU = (1 << USART_CR1_RWU_Pos)   # Receiver wakeup
USART_CR1_RE_Pos = 2;   USART_CR1_RE = (1 << USART_CR1_RE_Pos)    # Receiver enable
USART_CR1_TE_Pos = 3;   USART_CR1_TE = (1 << USART_CR1_TE_Pos)    # Transmitter enable
USART_CR1_IDLEIE_Pos=4; USART_CR1_IDLEIE=(1 << USART_CR1_IDLEIE_Pos)# IDLE interrupt enable
USART_CR1_RXNEIE_Pos=5; USART_CR1_RXNEIE=(1 << USART_CR1_RXNEIE_Pos)# RXNE interrupt enable
USART_CR1_TCIE_Pos = 6; USART_CR1_TCIE = (1 << USART_CR1_TCIE_Pos)  # Transmission complete interrupt enable
USART_CR1_TXEIE_Pos = 7;USART_CR1_TXEIE= (1 << USART_CR1_TXEIE_Pos) # TXE interrupt enable
USART_CR1_PEIE_Pos = 8; USART_CR1_PEIE = (1 << USART_CR1_PEIE_Pos)  # PE interrupt enable
USART_CR1_PS_Pos = 9;   USART_CR1_PS = (1 << USART_CR1_PS_Pos)    # Parity selection
USART_CR1_PCE_Pos = 10; USART_CR1_PCE = (1 << USART_CR1_PCE_Pos) # Parity control enable
USART_CR1_WAKE_Pos= 11; USART_CR1_WAKE = (1 << USART_CR1_WAKE_Pos) # Wakeup method
USART_CR1_M_Pos = 12;   USART_CR1_M = (1 << USART_CR1_M_Pos)     # Word length (0=8bits, 1=9bits)
USART_CR1_UE_Pos = 13;  USART_CR1_UE = (1 << USART_CR1_UE_Pos)   # USART enable
# CR2 bits (USART_CR2)
USART_CR2_ADD_Pos = 0; USART_CR2_ADD_Msk = (0xF << USART_CR2_ADD_Pos) # Address of the USART node
USART_CR2_LBDL_Pos= 5; USART_CR2_LBDL = (1 << USART_CR2_LBDL_Pos)  # LIN break detection length
USART_CR2_LBDIE_Pos=6; USART_CR2_LBDIE= (1 << USART_CR2_LBDIE_Pos) # LIN break detection interrupt enable
USART_CR2_LBCL_Pos= 8; USART_CR2_LBCL = (1 << USART_CR2_LBCL_Pos)  # Last bit clock pulse
USART_CR2_CPHA_Pos= 9; USART_CR2_CPHA = (1 << USART_CR2_CPHA_Pos)  # Clock phase (for sync mode)
USART_CR2_CPOL_Pos= 10;USART_CR2_CPOL = (1 << USART_CR2_CPOL_Pos)  # Clock polarity (for sync mode)
USART_CR2_CLKEN_Pos=11;USART_CR2_CLKEN= (1 << USART_CR2_CLKEN_Pos) # Clock enable (for sync mode)
USART_CR2_STOP_Pos= 12;USART_CR2_STOP_Msk=(0x3 << USART_CR2_STOP_Pos) # STOP bits
USART_CR2_LINEN_Pos=14;USART_CR2_LINEN= (1 << USART_CR2_LINEN_Pos) # LIN mode enable
# CR3 bits (USART_CR3)
USART_CR3_EIE_Pos = 0;  USART_CR3_EIE = (1 << USART_CR3_EIE_Pos)    # Error interrupt enable
USART_CR3_IREN_Pos= 1;  USART_CR3_IREN = (1 << USART_CR3_IREN_Pos)   # IrDA mode enable
USART_CR3_IRLP_Pos= 2;  USART_CR3_IRLP = (1 << USART_CR3_IRLP_Pos)   # IrDA low-power
USART_CR3_HDSEL_Pos=3;  USART_CR3_HDSEL= (1 << USART_CR3_HDSEL_Pos) # Half-duplex selection
USART_CR3_NACK_Pos= 4;  USART_CR3_NACK = (1 << USART_CR3_NACK_Pos)  # Smartcard NACK enable
USART_CR3_SCEN_Pos= 5;  USART_CR3_SCEN = (1 << USART_CR3_SCEN_Pos)  # Smartcard mode enable
USART_CR3_DMAR_Pos= 6;  USART_CR3_DMAR = (1 << USART_CR3_DMAR_Pos)  # DMA enable receiver
USART_CR3_DMAT_Pos= 7;  USART_CR3_DMAT = (1 << USART_CR3_DMAT_Pos)  # DMA enable transmitter
USART_CR3_RTSE_Pos= 8;  USART_CR3_RTSE = (1 << USART_CR3_RTSE_Pos)  # RTS enable
USART_CR3_CTSE_Pos= 9;  USART_CR3_CTSE = (1 << USART_CR3_CTSE_Pos)  # CTS enable
USART_CR3_CTSIE_Pos=10; USART_CR3_CTSIE= (1 << USART_CR3_CTSIE_Pos)# CTS interrupt enable
# BRR (USART_BRR)
USART_BRR_DIV_Mantissa_Pos = 4 # DIV_Mantissa[11:0] are BRR[15:4]
USART_BRR_DIV_Fraction_Pos = 0 # DIV_Fraction[3:0] are BRR[3:0]
# SR (USART_SR)
USART_SR_PE_Pos = 0;   USART_SR_PE   = (1 << USART_SR_PE_Pos)   # Parity error
USART_SR_FE_Pos = 1;   USART_SR_FE   = (1 << USART_SR_FE_Pos)   # Framing error
USART_SR_NE_Pos = 2;   USART_SR_NE   = (1 << USART_SR_NE_Pos)   # Noise error flag
USART_SR_ORE_Pos = 3;  USART_SR_ORE  = (1 << USART_SR_ORE_Pos)  # Overrun error
USART_SR_IDLE_Pos = 4; USART_SR_IDLE = (1 << USART_SR_IDLE_Pos) # IDLE line detected
USART_SR_RXNE_Pos = 5; USART_SR_RXNE = (1 << USART_SR_RXNE_Pos) # Read data register not empty
USART_SR_TC_Pos   = 6; USART_SR_TC   = (1 << USART_SR_TC_Pos)   # Transmission complete
USART_SR_TXE_Pos  = 7; USART_SR_TXE  = (1 << USART_SR_TXE_Pos)  # Transmit data register empty
USART_SR_LBD_Pos  = 8; USART_SR_LBD  = (1 << USART_SR_LBD_Pos)  # LIN break detection flag
USART_SR_CTS_Pos  = 9; USART_SR_CTS  = (1 << USART_SR_CTS_Pos)  # CTS flag (only if CTSE=1)

# UI Maps for USART F1
USART_WORD_LENGTH_MAP_F1 = {"8 bits":0, "9 bits":1} # Value for M bit
USART_PARITY_MAP_F1 = {"None":0b00, "Even":0b10, "Odd":0b11} # PCE=bit1, PS=bit0
USART_STOP_BITS_MAP_F1 = {"1":0b00, "0.5":0b01, "2":0b10, "1.5":0b11} # For STOP bits
USART_HW_FLOW_CTRL_MAP_F1 = {"None":0b00, "RTS":0b01, "CTS":0b10, "RTS/CTS":0b11} # RTSE=bit0, CTSE=bit1
USART_MODE_MAP_F1 = {"RX Only":0b01, "TX Only":0b10, "TX/RX":0b11} # RE=bit0, TE=bit1
USART_OVERSAMPLING_MAP_F1 = {"16":0} # F1 is always oversampling by 16

# --- Timer Defines for F1 ---
TIMER_PERIPHERALS_INFO_F1 = {
    "TIM1":  {"type":"ADV",  "bus":"APB2", "rcc_macro":"RCC_APB2ENR_TIM1EN", "max_channels":4, "has_bdtr":True, "is_16bit":True},
    "TIM2":  {"type":"GP16_OR_GP32", "bus":"APB1", "rcc_macro":"RCC_APB1ENR_TIM2EN", "max_channels":4, "has_bdtr":False, "is_16bit":False}, # Can be 32-bit for counter on F103
    "TIM3":  {"type":"GP16", "bus":"APB1", "rcc_macro":"RCC_APB1ENR_TIM3EN", "max_channels":4, "has_bdtr":False, "is_16bit":True},
    "TIM4":  {"type":"GP16", "bus":"APB1", "rcc_macro":"RCC_APB1ENR_TIM4EN", "max_channels":4, "has_bdtr":False, "is_16bit":True},
    "TIM5":  {"type":"GP16_OR_GP32", "bus":"APB1", "rcc_macro":"RCC_APB1ENR_TIM5EN", "max_channels":4, "has_bdtr":False, "is_16bit":False}, # On high-density
    "TIM6":  {"type":"BASIC","bus":"APB1", "rcc_macro":"RCC_APB1ENR_TIM6EN", "max_channels":0, "has_bdtr":False, "is_16bit":True}, # For F100/F103
    "TIM7":  {"type":"BASIC","bus":"APB1", "rcc_macro":"RCC_APB1ENR_TIM7EN", "max_channels":0, "has_bdtr":False, "is_16bit":True}, # For F100/F103
    "TIM8":  {"type":"ADV",  "bus":"APB2", "rcc_macro":"RCC_APB2ENR_TIM8EN", "max_channels":4, "has_bdtr":True, "is_16bit":True}, # On high-density
    # F100 Value Line timers (RM0041)
    "TIM15": {"type":"GP16", "bus":"APB2", "rcc_macro":"RCC_APB2ENR_TIM15EN","max_channels":2,"has_bdtr":True, "is_16bit":True}, # F100 only
    "TIM16": {"type":"GP16", "bus":"APB2", "rcc_macro":"RCC_APB2ENR_TIM16EN","max_channels":1,"has_bdtr":True, "is_16bit":True}, # F100 only
    "TIM17": {"type":"GP16", "bus":"APB2", "rcc_macro":"RCC_APB2ENR_TIM17EN","max_channels":1,"has_bdtr":True, "is_16bit":True}, # F100 only
}
# Common Timer bits for F1 (verify positions from RM0008/RM0041)
TIM_CR1_CEN_Pos = 0; TIM_CR1_UDIS_Pos = 1; TIM_CR1_URS_Pos = 2; TIM_CR1_OPM_Pos = 3;
TIM_CR1_DIR_Pos = 4; TIM_CR1_CMS_Pos = 5; TIM_CR1_ARPE_Pos = 7; TIM_CR1_CKD_Pos = 8;
TIM_DIER_UIE_Pos = 0; TIM_DIER_CC1IE_Pos = 1; TIM_DIER_CC2IE_Pos = 2; TIM_DIER_CC3IE_Pos = 3; TIM_DIER_CC4IE_Pos = 4;
TIM_EGR_UG_Pos = 0;
TIM_CCMRx_OCxM_Pos = 4; # In CCMR1: OC1M bits 6:4, OC2M bits 14:12. In CCMR2: OC3M bits 6:4, OC4M bits 14:12. (offset for mode is correct)
TIM_CCMRx_OCxPE_Pos = 3; # OCxPE is bit 3 (OC1PE) or bit 11 (OC2PE) in CCMR1. etc.
TIM_CCMRx_CCxS_Pos = 0;
TIM_CCER_CC1E_Pos = 0; TIM_CCER_CC1P_Pos = 1; # Similar for CC2E/P, CC3E/P, CC4E/P at offsets 4, 8, 12
TIM_BDTR_MOE_Pos = 15; # Main Output Enable (TIM1, TIM8, TIM15/16/17)
TIM_SMCR_SMS_Pos=0; TIM_SMCR_TS_Pos=4; TIM_SMCR_ECE_Pos=14; # For external clock mode 2


# --- I2C Defines for F1 ---
I2C_PERIPHERALS_INFO_F1 = {
    "I2C1": {"bus": "APB1", "rcc_macro": "RCC_APB1ENR_I2C1EN"},
    "I2C2": {"bus": "APB1", "rcc_macro": "RCC_APB1ENR_I2C2EN"}, # Not on all F1
}
# I2C_CR1
I2C_CR1_PE_Pos = 0; I2C_CR1_SMBUS_Pos = 1; I2C_CR1_ENARP_Pos = 4; I2C_CR1_ENPEC_Pos = 5;
I2C_CR1_ENGC_Pos = 6; I2C_CR1_NOSTRETCH_Pos = 7; I2C_CR1_START_Pos = 8; I2C_CR1_STOP_Pos = 9;
I2C_CR1_ACK_Pos = 10; I2C_CR1_POS_Pos = 11; I2C_CR1_PEC_Pos = 12; I2C_CR1_SWRST_Pos = 15;
# I2C_CR2
I2C_CR2_FREQ_Pos = 0; I2C_CR2_FREQ_Msk = (0x3F << I2C_CR2_FREQ_Pos) # Peripheral clock frequency in MHz
I2C_CR2_ITERREN_Pos = 8; I2C_CR2_ITEVTEN_Pos = 9; I2C_CR2_ITBUFEN_Pos = 10;
I2C_CR2_DMAEN_Pos = 11; I2C_CR2_LAST_Pos = 12;
# I2C_CCR
I2C_CCR_CCR_Pos = 0; I2C_CCR_CCR_Msk = (0xFFF << I2C_CCR_CCR_Pos) # Clock control register value
I2C_CCR_DUTY_Pos = 14; # F1: Tlow/Thigh duty cycle in Fast mode (0 for 2, 1 for 16/9)
I2C_CCR_FS_Pos = 15;   # F1: I2C master mode selection (0=standard, 1=fast)

I2C_MIN_PCLK_MHZ_F1 = 2 # RM0008 I2C_CR2 FREQ field description

# --- SPI Defines for F1 ---
SPI_PERIPHERALS_INFO_F1 = {
    "SPI1": {"bus": "APB2", "rcc_macro": "RCC_APB2ENR_SPI1EN"},
    "SPI2": {"bus": "APB1", "rcc_macro": "RCC_APB1ENR_SPI2EN"}, # Not on all F1
    "SPI3": {"bus": "APB1", "rcc_macro": "RCC_APB1ENR_SPI3EN"}, # On some F1 (e.g. connectivity line)
}
# SPI_CR1 bit positions for F1
SPI_CR1_CPHA_Pos = 0; SPI_CR1_CPOL_Pos = 1; SPI_CR1_MSTR_Pos = 2; SPI_CR1_BR_Pos = 3; SPI_CR1_BR_Msk = (0x7 << SPI_CR1_BR_Pos);
SPI_CR1_SPE_Pos = 6; SPI_CR1_LSBFIRST_Pos = 7; SPI_CR1_SSI_Pos = 8; SPI_CR1_SSM_Pos = 9;
SPI_CR1_RXONLY_Pos = 10; SPI_CR1_DFF_Pos = 11; SPI_CR1_CRCNEXT_Pos = 12; SPI_CR1_CRCEN_Pos = 13;
SPI_CR1_BIDIOE_Pos = 14; SPI_CR1_BIDIMODE_Pos = 15;
# SPI_CR2
SPI_CR2_RXDMAEN_Pos = 0; SPI_CR2_TXDMAEN_Pos = 1; SPI_CR2_SSOE_Pos = 2;
SPI_CR2_ERRIE_Pos = 5; SPI_CR2_RXNEIE_Pos = 6; SPI_CR2_TXEIE_Pos = 7;
# SPI_SR
SPI_SR_RXNE_Pos = 0; SPI_SR_TXE_Pos = 1; SPI_SR_CHSIDE_Pos = 2; SPI_SR_UDR_Pos = 3;
SPI_SR_CRCERR_Pos = 4; SPI_SR_MODF_Pos = 5; SPI_SR_OVR_Pos = 6; SPI_SR_BSY_Pos = 7;


# --- DMA Defines for F1 ---
# F1 has DMA1 (up to 7 channels) and DMA2 (up to 5 channels on high-density)
# Configuration is per-channel using DMA_CCRx, DMA_CPARx, DMA_CMARx, DMA_CNDTRx
DMA_PERIPHERALS_INFO_F1 = {
    "DMA1": {"rcc_macro": "RCC_AHBENR_DMA1EN", "channels": 7},
    # "DMA2": {"rcc_macro": "RCC_AHBENR_DMA2EN", "channels": 5}, # If applicable for target
}
# DMA_CCRx bits (Channel x Configuration Register)
DMA_CCRx_EN_Pos = 0;    DMA_CCRx_TCIE_Pos = 1;  DMA_CCRx_HTIE_Pos = 2;  DMA_CCRx_TEIE_Pos = 3;
DMA_CCRx_DIR_Pos = 4;   DMA_CCRx_CIRC_Pos = 5;  DMA_CCRx_PINC_Pos = 6;  DMA_CCRx_MINC_Pos = 7;
DMA_CCRx_PSIZE_Pos = 8; DMA_CCRx_MSIZE_Pos = 10; DMA_CCRx_PL_Pos = 12;   DMA_CCRx_MEM2MEM_Pos = 14;
# DMA_ISR (Interrupt Status Register) and DMA_IFCR (Interrupt Flag Clear Register)
# Flags are per channel: GIFn, TCIFn, HTIFn, TEIFn (n is channel number 1-7)
# E.g. DMA_ISR_TCIF1_Pos = 1 for Channel 1 Transfer Complete flag.

# --- DAC Defines for F1 (Value Line and some others like F107) ---
DAC_PERIPHERALS_INFO_F1 = { # If DAC exists
    "DAC1": {"rcc_macro": "RCC_APB1ENR_DACEN", "channels": 2}, # DAC block, can have 2 channels
}
# DAC_CR (Control Register)
DAC_CR_EN1_Pos = 0;   DAC_CR_BOFF1_Pos = 1;  DAC_CR_TEN1_Pos = 2;
DAC_CR_TSEL1_Pos = 3; DAC_CR_TSEL1_Msk = (0x7 << DAC_CR_TSEL1_Pos);
DAC_CR_WAVE1_Pos = 6; DAC_CR_WAVE1_Msk = (0x3 << DAC_CR_WAVE1_Pos);
DAC_CR_MAMP1_Pos = 8; DAC_CR_MAMP1_Msk = (0xF << DAC_CR_MAMP1_Pos);
DAC_CR_DMAEN1_Pos = 12;
# Channel 2 bits are offset by 16 (EN2 is bit 16, etc.)
DAC_CH2_CR_OFFSET = 16

DAC_OUTPUT_PINS_F1 = {
    "STM32F100RB": {"DAC_OUT1": "PA4", "DAC_OUT2": "PA5"}, # Example
}
# DAC Trigger sources are TIM6_TRGO, TIM7_TRGO (F100), TIM3_TRGO, SWTRIG
# See RM0041 or RM0008 for DAC TSEL values.