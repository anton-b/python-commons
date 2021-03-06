"""Common logging classes for centralized logging at Wikia"""

import json
import logging
import logging.handlers
import sys


class Logger(logging.getLoggerClass()):
    """Represents a logging channel"""

    def __init__(self, name):
        super(Logger, self).__init__(name)
        Logger.__use(self, overwrite_make_record=False)

    def makeRecord(self, name, lvl, fn, lno, msg, args, exc_info, func=None, extra=None):
        return Logger.__make_record(name, lvl, fn, lno, msg, args, exc_info, func, extra)

    @staticmethod
    def __make_record(name, lvl, fn, lno, msg, args, exc_info, func=None, extra=None):
        record = LogRecord(name, lvl, fn, lno, msg, args, exc_info, func)
        record.set_extra(extra)
        return record

    @staticmethod
    def use(logger, level=None):
        return Logger.__use(logger, level)

    @staticmethod
    def __use(logger, level=None, overwrite_make_record=True):

        # check for platform to allow for use on other non-linux os
        platform = sys.platform.lower()
        if platform == 'darwin':
            # specific for mac os X
            address = '/var/run/syslog'
        else:
            # for most linux distros
            address = '/dev/log'

        handler = logging.handlers.SysLogHandler(address=address)
        handler.setFormatter(LogFormatter())

        if level is not None:
            handler.setLevel(level)

        logger.addHandler(handler)

        if overwrite_make_record:
            logger.makeRecord = Logger.__make_record

        return logger

    @staticmethod
    def get(name='WikiaLogger', app_name=None, level=None):
        current = logging.getLoggerClass()
        logging.setLoggerClass(Logger)
        logger = logging.getLogger(name)
        if app_name is not None:
            LogRecord.app_name = app_name

        if level is not None:
            logger.setLevel(level)

        logging.setLoggerClass(current)
        return logger


class LogFormatter(logging.Formatter):
    """Converts a LogRecord to text"""

    def format(self, record):
        log_obj = {'@message': record.msg}

        if record.extra is not None:
            log_obj['@fields'] = record.extra

        result = ''.join([LogRecord.app_name, ': ', json.dumps(log_obj)])
        return result


class LogRecord(logging.LogRecord):
    """Represents an event being logged"""

    app_name = 'python'

    def __init__(self, *args, **kwargs):
        logging.LogRecord.__init__(self, *args, **kwargs)
        self.extra = None

    def set_extra(self, extra):
        self.extra = extra
