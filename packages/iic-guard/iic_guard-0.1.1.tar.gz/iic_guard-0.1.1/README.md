# iic-guard: I2C Register Watchdog

[![PyPI version](https://img.shields.io/pypi/v/iic-guard.svg)](https://pypi.org/project/iic-guard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight daemon to continuously monitor and protect I2C device registers on embedded Linux systems.

`iic-guard` solves the problem of critical I2C device registers being unexpectedly reset or changed by other processes. It runs as a background service, checks registers at a configurable interval, and can forcibly write correct values back if a mismatch is detected, ensuring your hardware remains in a known-good state.

## Features

- **Value Enforcement:** Automatically rewrites correct values to registers if they change.
- **Change Logging:** Monitors and logs value changes for debugging without enforcing them.
- **Daemonization:** Runs as a proper background service with PID file management and logging.
- **Flexible Configuration:** Uses a simple, human-readable YAML file.
- **Robust and Efficient:** Built with a C core for minimal overhead on embedded systems.

## Installation

The project is packaged and available on PyPI.

```bash
# It is recommended to install in a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install from PyPI
pip install iic-guard
```
*For local installation during development, see the Development section below.*

## Usage

#### 1. Generate a Configuration File

First, generate a template configuration file. The comments inside explain what each field does.
```bash
iic-guard --generate-config > config.yaml
```

#### 2. Edit the Configuration

Modify `config.yaml` to match your hardware. Set the I2C bus, device address, and the registers you want to monitor or enforce.

#### 3. Run the Daemon

##### Foreground Mode (for Testing)
Run in the foreground to see logs printed directly to your terminal:
```bash
iic-guard -c config.yaml
```

##### Background Daemon Mode (for Production)
Use the `--daemon` flag to run as a background service. This is the recommended way to run on a production device.
```bash
# Run as a background daemon
sudo iic-guard -c /etc/iic-guard/config.yaml \\
               --daemon \\
               --pidfile /var/run/iic-guard.pid \\
               --logfile /var/log/iic-guard.log
```
*Note: Using paths in `/var/run` and `/var/log` may require `sudo` permissions.*

## Development and Contributing

Contributions are welcome! Please feel free to open an issue or pull request.

To install in editable mode for development:
```bash
# Clone the repository
# git clone https://github.com/serhaturtis/iic-guard.git
# cd iic-guard

# Create venv and install in editable mode
python -m venv .venv
source .venv/bin/activate
pip install -e ./iic_guard
```
After making changes to the C source (`.c` or `.h` files), you must run `pip install -e ./iic_guard` again to recompile the C extension. 
