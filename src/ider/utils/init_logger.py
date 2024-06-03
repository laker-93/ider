import logging
import logging.handlers as handlers
import os
from pathlib import Path


def initialise_logger(app_name: str, level: str="DEBUG", **kwargs) -> logging.Logger:
    """
    Initialises the logger for the application with default handlers
    :param app_name:
    :param level:
    :param kwargs:
    :return:
    """
    logger = logging.getLogger()
    logger.setLevel(level)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # create formatter
    columns = [
        "%(asctime)s",
        app_name,
        "%(levelname)s",
        "%(process)d",
        "%(thread)d",
        "[%(filename)s-%(funcName)s():%(lineno)d]",
        "%(message)s",
    ]
    delimiter = kwargs.get("delimiter", "|")

    log_file_format = delimiter.join(columns)
    formatter = logging.Formatter(log_file_format)
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)

    if kwargs.get("disable_file_handler", False) is False:
        logs_directory = kwargs.get("logs_directory", "logs")
        when = kwargs.get("rolling_when", "midnight")
        interval = kwargs.get("rolling_interval", 1)
        backup_count = kwargs.get("rolling_backupcount", 10)

        Path(logs_directory).mkdir(exist_ok=True)

        logger.info(f"Started Writing Logs To {os.path.abspath(logs_directory)}")

        logHandler = handlers.TimedRotatingFileHandler(
            f"{logs_directory}/{app_name}.log",
            when=when,
            interval=interval,
            backupCount=backup_count,
        )
        logHandler.setLevel(logging.INFO)
        logHandler.setFormatter(formatter)
        logger.addHandler(logHandler)
    return logger