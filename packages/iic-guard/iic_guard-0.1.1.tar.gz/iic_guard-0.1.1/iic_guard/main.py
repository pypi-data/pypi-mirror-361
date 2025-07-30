import argparse
import sys
import logging
import daemon
import os

from .guard import RegisterGuard, load_config_from_yaml
from .config import get_config_template

def main():
    """Main application entrypoint."""
    parser = argparse.ArgumentParser(
        description="A daemon to monitor and protect I2C device registers.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Usage examples:
  # Run the guard in the foreground for testing
  iic-guard --config my_config.yaml

  # Run as a background daemon, logging to a file
  iic-guard -c my_config.yaml --daemon --logfile /var/log/iic-guard.log --pidfile /var/run/iic-guard.pid

  # Generate a new config template to standard output
  iic-guard --generate-config > my_config.yaml
"""
    )
    parser.add_argument(
        "-c", "--config",
        default="config.yaml",
        help="Path to the configuration file (default: %(default)s)."
    )
    parser.add_argument(
        "-d", "--daemon",
        action="store_true",
        help="Run the application as a background daemon."
    )
    parser.add_argument(
        "-p", "--pidfile",
        default="/tmp/iic-guard.pid",
        help="Path to the PID file when running as a daemon (default: %(default)s)."
    )
    parser.add_argument(
        "-l", "--logfile",
        default=None,
        help="Path to a log file. If not specified, logs go to stdout/stderr."
    )
    parser.add_argument(
        "--generate-config",
        action="store_true",
        help="Print a new configuration file template to stdout and exit."
    )
    
    args = parser.parse_args()

    if args.generate_config:
        print(get_config_template())
        sys.exit(0)

    # --- Daemonization and Logging Setup ---

    # Configure logging
    log_stream = open(args.logfile, 'a+') if args.logfile else sys.stdout
    logging.basicConfig(
        stream=log_stream, 
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    daemon_context = daemon.DaemonContext(
        working_directory=os.getcwd(),
        pidfile=args.pidfile if args.daemon else None,
        stdout=log_stream,
        stderr=log_stream,
    )

    if not args.daemon:
        # If not running as a daemon, prevent the context from forking
        daemon_context.detach_process = False
        # And ensure logs go to the console if no logfile is specified
        if not args.logfile:
            daemon_context.stdout = sys.stdout
            daemon_context.stderr = sys.stderr

    # --- Application Start ---

    try:
        with daemon_context:
            logging.info("--- iic-guard starting ---")
            
            try:
                config = load_config_from_yaml(args.config)
            except FileNotFoundError:
                logging.error(f"Configuration file not found at '{args.config}'")
                sys.exit(1)
            except Exception as e:
                logging.error(f"Failed to load or parse configuration: {e}")
                sys.exit(1)
                
            guard = RegisterGuard(config)
            
            guard.run()

    except Exception as e:
        # This will catch errors during daemonization itself
        logging.critical(f"Failed to start daemon: {e}", exc_info=True)
        sys.exit(1)
