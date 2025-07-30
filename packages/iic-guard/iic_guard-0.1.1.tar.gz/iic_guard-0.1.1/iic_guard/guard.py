import time
import yaml
import logging
from typing import Dict, Set

from .config import AppConfig, to_int
from .c_wrapper import I2CDevice, I2CError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RegisterGuard:
    def __init__(self, config: AppConfig):
        self._config = config
        self._bus = config.device.bus
        self._address = to_int(config.device.address)

        # Convert register lists/dicts to integer for faster processing
        self._log_on_change_regs: Set[int] = {to_int(r) for r in config.guard.log_on_change}
        self._enforce_regs: Dict[int, int] = {to_int(k): to_int(v) for k, v in config.guard.enforce_values.items()}
        
        # Combine all registers we need to read
        self._monitored_regs: Set[int] = self._log_on_change_regs.union(self._enforce_regs.keys())
        
        # In-memory cache to store the last known value of registers
        self._register_cache: Dict[int, int] = {}

    def run(self):
        """Starts the monitoring and guarding loop."""
        logging.info(f"Starting I2C guard for {self._bus} at address {self._address:#04x}")
        logging.info(f"Monitoring {len(self._monitored_regs)} registers every {self._config.guard.check_interval_seconds}s")
        
        with I2CDevice(self._bus, self._address) as dev:
            # Initial population of the cache
            self._populate_initial_state(dev)
            
            # Main monitoring loop
            while True:
                self._check_and_correct(dev)
                time.sleep(self._config.guard.check_interval_seconds)

    def _populate_initial_state(self, dev: I2CDevice):
        """Reads the initial state of all monitored registers."""
        logging.info("Reading initial state of all monitored registers...")
        for reg in self._monitored_regs:
            try:
                self._register_cache[reg] = dev.read_register(reg)
            except I2CError as e:
                logging.warning(f"Failed to read initial value for register {reg:#04x}: {e}")
        logging.info("Initial state population complete.")

    def _check_and_correct(self, dev: I2CDevice):
        """Performs a single check cycle for all monitored registers."""
        for reg in self._monitored_regs:
            try:
                current_value = dev.read_register(reg)
                last_known_value = self._register_cache.get(reg)

                # If the value has changed, log it.
                if last_known_value is not None and current_value != last_known_value:
                    logging.info(f"CHANGE DETECTED on register {reg:#04x}: was {last_known_value:#04x}, is now {current_value:#04x}")
                
                self._register_cache[reg] = current_value

                # If this register's value needs to be enforced, check it.
                if reg in self._enforce_regs:
                    required_value = self._enforce_regs[reg]
                    if current_value != required_value:
                        logging.warning(f"VALUE MISMATCH on register {reg:#04x}: is {current_value:#04x}, should be {required_value:#04x}. ENFORCING.")
                        try:
                            dev.write_register(reg, required_value)
                            # Update cache with the value we just wrote
                            self._register_cache[reg] = required_value
                        except I2CError as e:
                            logging.error(f"Failed to enforce value on register {reg:#04x}: {e}")

            except I2CError as e:
                logging.warning(f"Failed to read register {reg:#04x} during check: {e}")

def load_config_from_yaml(path: str) -> AppConfig:
    """Loads, parses, and validates the YAML configuration file."""
    logging.info(f"Loading configuration from {path}")
    with open(path, 'r') as f:
        raw_config = yaml.safe_load(f)
    return AppConfig.model_validate(raw_config) 