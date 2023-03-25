"""Módulo para hacer loggeos."""

import logging


LOG_FORMAT = '[%(asctime)s] - [%(filename)s %(lineno)d] %(levelname)s:'
LOG_DATE_FORMAT = '%Y:%m:%d %H:%M:%S'


class LogFormatter(logging.Formatter):
    """Formateador del log."""
    grey = "\x1b[38;20m"
    blue = "\x1b[34;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: LOG_FORMAT + ' ' + grey + '%(message)s' + reset,
        logging.INFO: LOG_FORMAT + ' ' + blue + '%(message)s' + reset,
        logging.WARNING: LOG_FORMAT + ' ' + yellow + '%(message)s' + reset,
        logging.ERROR: LOG_FORMAT + ' ' + red + '%(message)s' + reset,
        logging.CRITICAL: LOG_FORMAT + ' ' + bold_red + '%(message)s' + reset,
    }

    def format(self, record):
        log_formatter = logging.Formatter(
            fmt=self.FORMATS.get(record.levelno),
            datefmt=LOG_DATE_FORMAT
        )
        return log_formatter.format(record)


formatter = LogFormatter()
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)
logger.propagate = False
