import logging

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[41m', # Bold Red (background)
        'RESET': '\033[0m',     # Reset color
        'BOLD': '\033[1m',      # Bold
    }

    def format(self, record):
        log_message = super().format(record)
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        colored_level = f"{level_color}{self.COLORS['BOLD']}{record.levelname}{self.COLORS['RESET']}"
        log_message = log_message.replace(record.levelname, colored_level, 1)
        return log_message

def setup_logger(logging_level=logging.DEBUG):
    logger = logging.getLogger("Logger")
    logger.setLevel(logging_level)
    
    if logger.hasHandlers():
        logger.handlers.clear()

    log_format = '\033[90m\033[1m%(asctime)s\033[0m %(levelname)-8s %(message)s'
    formatter = ColoredFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging_level)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.propagate = False

    return logger
