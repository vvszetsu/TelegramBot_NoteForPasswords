import logging
import datetime
import logging
import threading

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def setup_logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


info_logger = None
error_logger_with_stack_trace = None
default_error_logger = None


def set_loggers():
    global info_logger
    global error_logger_with_stack_trace
    global default_error_logger
    info_logger = setup_logger("INFO-logger",
                               f'./logs/INFO_log_{datetime.datetime.now().year}-'
                               f'{datetime.datetime.now().month}-{datetime.datetime.now().day}.log')

    error_logger_with_stack_trace = setup_logger("ERROR-logger",
                                                 f'./logs/ERROR_STACK_log_{datetime.datetime.now().year}-'
                                                 f'{datetime.datetime.now().month}-{datetime.datetime.now().day}.log')

    default_error_logger = setup_logger("ERROR-logger",
                                        f'./logs/ERROR_log_{datetime.datetime.now().year}-'
                                        f'{datetime.datetime.now().month}-{datetime.datetime.now().day}.log')


set_loggers()


class MyThread(threading.Thread):
    def __init__(self, event_to_do, func_to_do, time=10):
        threading.Thread.__init__(self)
        self.stopped = event_to_do
        self.func = func_to_do
        self.time = time

    def run(self):
        now = datetime.datetime.today()
        next_day = datetime.datetime(now.year, now.month, now.day + 1)
        time_to_sleep = (next_day - now).seconds
        while not self.stopped.wait(time_to_sleep):
            self.func()


stopFlag = threading.Event()
s = MyThread(stopFlag, set_loggers)
s.start()


def log_warn(message):
    default_error_logger.warning(message)


def log_info(message):
    info_logger.info(message)


def log_err(message):
    default_error_logger.error(message.args, exc_info=False)
    error_logger_with_stack_trace.error(message, exc_info=True)


def log_crit_err(message):
    default_error_logger.critical(message, exc_info=False)
    error_logger_with_stack_trace.critical(message, exc_info=True)
