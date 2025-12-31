import logging

import click


class ColorFormatter(logging.Formatter):
    _format = '%(asctime)s %(levelname)s %(message)s'
    _datefmt = '%Y-%m-%d %H:%M:%S'

    log_colors: dict[int, list[tuple[str, str]]] = {
        logging.DEBUG: [
            ('%(levelname)s', 'cyan'),
        ],
        logging.INFO: [
            ('%(levelname)s', 'green'),
        ],
        logging.WARNING: [
            ('%(levelname)s', 'yellow'),
            ('%(message)s', 'yellow'),
        ],
        logging.ERROR: [
            ('%(levelname)s', 'red'),
            ('%(message)s', 'red'),
        ],
        logging.CRITICAL: [
            ('%(levelname)s', 'bright_red'),
            ('%(message)s', 'bright_red'),
        ],
    }

    def format(self, record: logging.LogRecord):
        log_fmt = self._format

        color_handlers: list[tuple[str, str]] = self.log_colors.get(record.levelno, [])
        for text, color in color_handlers:
            log_fmt = log_fmt.replace(text, click.style(str(text), fg=color))

        formatter = logging.Formatter(log_fmt, datefmt=self._datefmt)
        return formatter.format(record)


def init_logger(log_level: int):
    color_formatter = ColorFormatter()

    handler = logging.StreamHandler()
    handler.setFormatter(color_formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)
    logging.basicConfig(level=log_level, format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    logger = logging.getLogger('uvicorn.access')
    handler = logging.StreamHandler()
    handler.setFormatter(color_formatter)
    logger.addHandler(handler)
