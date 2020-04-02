import logging
import traceback
from logging import handlers


class Logger:
    def __init__(self, name):

        if not len(logger.handlers):
            self.name = name

            logger.setLevel(logging.DEBUG)
            handler = logging.handlers.WatchedFileHandler("stackl.log")
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('[[[%(asctime)s|%(message)s',
                                          "%d.%m.%y|%H:%M:%S")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    # Intended usage: if you, for instance, want everything from module utils, enter [Utils] and it will also be printed instead of just logged
    def log(self, raw_message, event=None):
        message = self._format_message(raw_message,
                                       log_type='debug',
                                       event=event)
        if "PLACEHOLDER_FOR_SPECIAL_PRINTS1" or "PLACEHOLDER_FOR_SPECIAL_PRINTS2" in raw_message:
            print(message)
        logger.debug(message)

    def info(self, raw_message, event=None):
        message = self._format_message(raw_message,
                                       log_type='info',
                                       event=event)
        print(message)
        logger.info(message)

    def error(self, raw_message, event=None):
        message = self._format_message(raw_message,
                                       log_type='error',
                                       event=event)
        print(message)
        print(traceback.format_exc())
        logger.error(message)
        logger.error(traceback.format_exc())

    def warning(self, raw_message, event=None):
        message = self._format_message(raw_message,
                                       log_type='warning',
                                       event=event)
        print(message)
        logger.warning(message)

    def _format_message(self, raw_message, log_type='info', event=None):
        return "{0}]{1}".format(log_type, raw_message)
