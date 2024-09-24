# main.py

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from src.gui.main_window import MainWindow

import tempfile
from datetime import datetime

log_file = os.path.expanduser('~/DictationApp_log.txt')

def exception_hook(exctype, value, traceback):
    with open(os.path.expanduser('~/DictationApp_error.txt'), 'w') as f:
        f.write(f"An error occurred: {exctype.__name__}: {value}\n")
    sys.__excepthook__(exctype, value, traceback)

sys.excepthook = exception_hook

def log_info(message):
    with open(log_file, 'a') as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} - {message}\n")

log_info("Application started")
log_info(f"Executable path: {sys.executable}")
log_info(f"Current working directory: {os.getcwd()}")
log_info(f"Python path: {sys.path}")

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_file),
                        logging.StreamHandler(sys.stdout)
                    ])

logging.info('Logging initialized')

try:
    logging.info('Application started')
    logging.info(f'Current working directory: {os.getcwd()}')
    logging.info(f'Python path: {sys.path}')
except Exception as e:
    print(f"Error logging initial information: {e}", file=sys.stderr)

def main():
    logging.info("Starting application")
    logging.info('Application started')
    logging.info(f'Current working directory: {os.getcwd()}')
    logging.info(f'Python path: {sys.path}')
    try:
        app = QApplication(sys.argv)
        logging.info("QApplication created")
        main_window = MainWindow()
        logging.info("MainWindow created")
        main_window.show()
        logging.info("MainWindow shown")
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"Error in main: {str(e)}", exc_info=True)

    logging.info('Initializing GUI')
    # GUI initialization code here
    logging.info('GUI initialized')

    logging.info('Loading resources')
    # Resource loading code here
    logging.info('Resources loaded')

    logging.info("Environment variables:")
    for key, value in os.environ.items():
        logging.info(f"{key}: {value}")

    try:
        logging.info('Application running')
    except Exception as e:
        logging.exception(f"An error occurred: {e}")

    log_info("Main application code running")

if __name__ == "__main__":
    main()
