# --- MODIFIED FILE core/mcu_defines_loader.py ---
# This is a conceptual loader. In a real app, this might be more dynamic.

# Dictionaries to hold defines from each family file
F1_DEFINES = {}
F2_DEFINES = {}
F4_DEFINES = {}


def _populate_defines_dict(module, family_name_short):
    """Helper to populate defines and standardize TARGET_DEVICES key."""
    defines_dict = {'FAMILY_NAME': f"STM32{family_name_short}"}

    # Extract all module attributes
    for k in dir(module):
        if not k.startswith('_'):
            defines_dict[k] = getattr(module, k)

    # Standardize TARGET_DEVICES key
    family_specific_target_key = f"TARGET_DEVICES_{family_name_short}"  # e.g., TARGET_DEVICES_F1

    if family_specific_target_key in defines_dict:
        # If family-specific key exists, copy its value to the generic 'TARGET_DEVICES'
        # and remove the family-specific one to avoid confusion, or keep both if preferred.
        # For simplicity, we'll ensure 'TARGET_DEVICES' is always present.
        defines_dict['TARGET_DEVICES'] = defines_dict[family_specific_target_key]
        # Optionally remove the specific key if you want only one source of truth:
        # del defines_dict[family_specific_target_key]
    elif 'TARGET_DEVICES' not in defines_dict:
        # If neither generic nor specific key exists, create an empty TARGET_DEVICES
        # This might happen if a new defines file is added without this structure.
        print(
            f"Warning: Neither 'TARGET_DEVICES' nor '{family_specific_target_key}' found for STM32{family_name_short}.")
        defines_dict['TARGET_DEVICES'] = {}

    return defines_dict


def load_defines(family_name):
    """
    Loads and returns a dictionary of defines for the given family.
    This is a simplified example; a real implementation might dynamically
    import modules or parse files.
    """
    family_name_upper = family_name.upper()
    if family_name_upper == "STM32F1":
        if not F1_DEFINES:  # Load on demand
            try:
                from . import stm32f1_defines
                F1_DEFINES.update(_populate_defines_dict(stm32f1_defines, "F1"))
            except ImportError as e:
                print(f"Error: Could not load stm32f1_defines.py: {e}")
                return None
        return F1_DEFINES
    elif family_name_upper == "STM32F2":
        if not F2_DEFINES:
            try:
                from . import stm32f2_defines
                F2_DEFINES.update(_populate_defines_dict(stm32f2_defines, "F2"))
            except ImportError as e:
                print(f"Error: Could not load stm32f2_defines.py: {e}")
                return None
        return F2_DEFINES
    elif family_name_upper == "STM32F4":
        if not F4_DEFINES:
            try:
                from . import stm32f4_defines
                # F4 already uses TARGET_DEVICES, but let's use the helper for consistency
                F4_DEFINES.update(_populate_defines_dict(stm32f4_defines, "F4"))
            except ImportError as e:
                print(f"Error: Could not load stm32f4_defines.py: {e}")
                return None
        return F4_DEFINES
    else:
        print(f"Unsupported MCU family: {family_name}")
        return None


CURRENT_MCU_DEFINES = {}  # Global dictionary to hold defines for the currently selected family


def set_current_mcu_defines(family_name):
    """Sets the global CURRENT_MCU_DEFINES based on the family."""
    global CURRENT_MCU_DEFINES
    # print(f"Attempting to set MCU defines for family: {family_name}") # Debug
    defs = load_defines(family_name)
    if defs:
        CURRENT_MCU_DEFINES.clear()  # Clear old defines
        CURRENT_MCU_DEFINES.update(defs)  # Update with new ones
        # print(f"Successfully set MCU defines for {family_name}. HSI: {CURRENT_MCU_DEFINES.get('HSI_VALUE_HZ')}, TARGET_DEVICES keys: {list(CURRENT_MCU_DEFINES.get('TARGET_DEVICES', {}).keys())}") # Debug
        return True
    CURRENT_MCU_DEFINES.clear()  # Reset if loading failed
    print(f"Failed to set MCU defines for {family_name}")  # Debug
    return False


# Initialize with F4 defines by default if possible
# This initial call is important for the application startup state.
if not set_current_mcu_defines("STM32F4"):  # Default to F4
    print("Warning: Could not load default STM32F4 defines on startup.")