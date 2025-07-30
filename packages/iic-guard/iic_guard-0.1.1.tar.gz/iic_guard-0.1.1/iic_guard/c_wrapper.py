import ctypes
import os
from ctypes.util import find_library

# --- Load the C library ---

# The name of the *file* on disk, without the python/platform specific suffix
# This comes from the last part of the 'name' in setup.py's Extension()
LIB_FILENAME_PREFIX = "_c_iic_guard"

_lib_path = None
# Search for the library file in the same directory as this wrapper.
# This is robust for editable installs.
_base_path = os.path.dirname(os.path.abspath(__file__))
try:
    _lib_filename = next(
        f for f in os.listdir(_base_path) 
        if f.startswith(LIB_FILENAME_PREFIX) and f.endswith(".so")
    )
    _lib_path = os.path.join(_base_path, _lib_filename)
except StopIteration:
    # If not found, fall back to ctypes' default search mechanism
    _lib_path = find_library(LIB_FILENAME_PREFIX)

if not _lib_path:
    raise ImportError(f"Could not find shared library '{LIB_FILENAME_PREFIX}'. "
                      "Make sure the project is installed correctly (e.g., 'pip install -e .')")

try:
    _lib = ctypes.CDLL(_lib_path)
except OSError as e:
    raise ImportError(f"Could not load shared library at '{_lib_path}': {e}")


# --- Define C function prototypes ---

# Opaque pointer for our iic_device_t struct
class _IICDevice(ctypes.Structure):
    pass

_IICDevicePtr = ctypes.POINTER(_IICDevice)

# int iic_open(const char* bus_path, uint8_t device_addr, iic_device_t** dev_handle);
_lib.iic_open.argtypes = [ctypes.c_char_p, ctypes.c_uint8, ctypes.POINTER(_IICDevicePtr)]
_lib.iic_open.restype = ctypes.c_int

# void iic_close(iic_device_t* dev);
_lib.iic_close.argtypes = [_IICDevicePtr]
_lib.iic_close.restype = None

# int iic_read_register(iic_device_t* dev, uint8_t reg_addr, uint8_t* value);
_lib.iic_read_register.argtypes = [_IICDevicePtr, ctypes.c_uint8, ctypes.POINTER(ctypes.c_uint8)]
_lib.iic_read_register.restype = ctypes.c_int

# int iic_write_register(iic_device_t* dev, uint8_t reg_addr, uint8_t value);
_lib.iic_write_register.argtypes = [_IICDevicePtr, ctypes.c_uint8, ctypes.c_uint8]
_lib.iic_write_register.restype = ctypes.c_int


# --- Python-friendly wrapper class ---

class I2CError(IOError):
    """Custom exception for I2C errors that includes the C errno."""
    def __init__(self, message, c_errno=None):
        self.c_errno = c_errno
        if c_errno is not None:
            super().__init__(f"{message}: [errno {c_errno}] {os.strerror(c_errno)}")
        else:
            super().__init__(message)

class I2CDevice:
    """A Python context manager for an I2C device."""
    
    def __init__(self, bus_path: str, device_addr: int):
        self._bus_path_bytes = bus_path.encode('utf-8')
        self._device_addr = device_addr
        self._dev_handle = None

    def __enter__(self):
        handle = _IICDevicePtr()
        ret = _lib.iic_open(self._bus_path_bytes, self._device_addr, ctypes.byref(handle))
        if ret != 0:
            # The C function returned an errno value directly.
            raise I2CError(f"Failed to open I2C device at {self._bus_path_bytes.decode()} on address {self._device_addr}", c_errno=ret)
        self._dev_handle = handle
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._dev_handle:
            _lib.iic_close(self._dev_handle)

    def read_register(self, reg_addr: int) -> int:
        """Reads a byte from a register."""
        if not self._dev_handle:
            raise I2CError("I2C device is not open.")
        
        read_value = ctypes.c_uint8()
        # Use a fresh errno before the call
        ctypes.set_errno(0)
        ret = _lib.iic_read_register(self._dev_handle, reg_addr, ctypes.byref(read_value))
        if ret != 0:
            # The function returned -1, get the errno it set.
            raise I2CError(f"Failed to read from register {reg_addr:#04x}", c_errno=ctypes.get_errno())
        return read_value.value

    def write_register(self, reg_addr: int, value: int):
        """Writes a byte to a register."""
        if not self._dev_handle:
            raise I2CError("I2C device is not open.")

        ctypes.set_errno(0)
        ret = _lib.iic_write_register(self._dev_handle, reg_addr, value)
        if ret != 0:
            raise I2CError(f"Failed to write to register {reg_addr:#04x}", c_errno=ctypes.get_errno())

if __name__ == "__main__":
    print("This module is not meant to be run directly anymore.") 