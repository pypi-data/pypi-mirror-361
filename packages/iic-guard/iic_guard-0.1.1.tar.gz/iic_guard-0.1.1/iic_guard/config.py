from pydantic import BaseModel, Field
from typing import List, Dict, Union

def to_int(val: Union[int, str]) -> int:
    """Converts a string (hex or dec) or int to an int."""
    if isinstance(val, str):
        return int(val, 0) # Use base 0 to auto-detect hex (0x) or decimal
    return val

class DeviceConfig(BaseModel):
    """Configuration for the target I2C device."""
    bus: str = Field(
        ...,
        description="Path to the I2C bus, e.g., '/dev/i2c-1'."
    )
    address: Union[int, str] = Field(
        ...,
        description="I2C device address (e.g., 68 or '0x44')."
    )

class GuardConfig(BaseModel):
    """Configuration for the register guarding behavior."""
    check_interval_seconds: float = Field(
        1.0,
        description="Time in seconds between register checks."
    )
    log_on_change: List[Union[int, str]] = Field(
        default_factory=list,
        description="List of register addresses to monitor. A log message will be printed if their value changes."
    )
    enforce_values: Dict[Union[int, str], Union[int, str]] = Field(
        default_factory=dict,
        description="A map of register addresses to their required values. These will be forcibly written if a different value is detected."
    )

class AppConfig(BaseModel):
    """The main configuration model for the iic_guard application."""
    device: DeviceConfig
    guard: GuardConfig

# Example usage (for testing and reference):
def get_example_config() -> AppConfig:
    return AppConfig(
        device=DeviceConfig(bus="/dev/i2c-1", address=0x42),
        guard=GuardConfig(
            check_interval_seconds=0.5,
            log_on_change=[0x01, 0x02, "0x0A"],
            enforce_values={
                0x10: 0xFF,
                "0x11": "0xAB"
            }
        )
    )

def get_config_template() -> str:
    """Returns a heavily commented YAML config template string."""
    return """\
# -------------------------------------------------------------------
# iic_guard Configuration File
# -------------------------------------------------------------------
# This file defines the behavior of the I2C register guard daemon.
# You can generate this template using: iic_guard --generate-config

device:
  # bus: The file path to the I2C bus your device is on.
  # On most Linux systems, this will be something like "/dev/i2c-1".
  # Required.
  bus: /dev/i2c-1

  # address: The 7-bit I2C address of your target device.
  # You can use a simple integer (e.g., 68) or a hex string (e.g., "0x44").
  # Required.
  address: 0x42

guard:
  # check_interval_seconds: How often, in seconds, the daemon should check the registers.
  # Floating point values are allowed (e.g., 0.5 for 500ms).
  # Default: 1.0
  check_interval_seconds: 1.0

  # log_on_change: A list of registers to monitor.
  # If the value of a register in this list changes between checks, a log message
  # will be printed. The value will NOT be changed back.
  # Use this for registers you want to observe but not control.
  # Addresses can be integers or hex strings.
  log_on_change:
    - 0x01
    - "0x0A"

  # enforce_values: A dictionary of registers and the values they MUST hold.
  # If a register in this map is found to have a different value, the daemon will
  # log a warning and immediately write the required value back to the device.
  # Use this for critical registers that must not change.
  # Keys (addresses) and values can be integers or hex strings.
  enforce_values:
    0x10: 0xFF
    "0x2F": "0xAB"
""" 