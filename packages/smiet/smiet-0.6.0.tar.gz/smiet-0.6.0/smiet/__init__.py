import logging

from . import units
from . import numpy

# Define public API as the fewest amount of objects required to apply template synthesis
__all__ = [
    "units"
]

# Set up smiet logger
class ColoredFormatter(logging.Formatter):
    COLOR_CODES = {
        logging.DEBUG: "\033[94m",  # Blue
        logging.INFO: "\033[92m",  # Green
        logging.WARNING: "\033[93m",  # Yellow
        logging.ERROR: "\033[91m",  # Red
        logging.CRITICAL: "\033[95m",  # Magenta
    }

    RESET_CODE = "\033[0m"

    def format(self, record):
        # Get the color code for the log level
        color_code = self.COLOR_CODES.get(record.levelno)

        # Format the message
        message = super().format(record)

        # Add the color
        message = f"{color_code}{message}{self.RESET_CODE}"
        return message


# Make StreamHandler with the colored formatter
handler = logging.StreamHandler()
handler.setFormatter(
    ColoredFormatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
)
handler.setLevel(1)

# Add handler to logger
logger = logging.getLogger("smiet")
logger.addHandler(handler)
logger.propagate = False  # do not pass message on to root logger
