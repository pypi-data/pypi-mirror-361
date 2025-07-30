import logging
import time

class MyFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = time.time()

    def format(self, record):
        total_seconds = int(time.time() - self.start_time)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        record.elapsed_time = f"{hours:02}:{minutes:02}:{seconds:02}"
        return super().format(record)


class Logger():
    # class variables
    logger = logging.getLogger('Full-DIA')
    logger.setLevel(logging.DEBUG)
    logger.propagate = False # no forward transfer

    @classmethod
    def set_logger(cls, dir_out, is_time_name=True):
        logging._startTime = time.time() # reset relative time

        # fh
        logtime = time.strftime("%Y_%m_%d_%H_%M")
        if is_time_name:
            fname = logtime + '.log.txt'
        else:
            fname = 'report.log.txt'
        fh = logging.FileHandler(dir_out / fname, mode='w')
        fh.setLevel(logging.INFO)

        # ch
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # format to handler
        formatter = MyFormatter(fmt = '%(elapsed_time)s: %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # handler binding to logger
        for handler in cls.logger.handlers:
            if type(handler) is logging.FileHandler:
                cls.logger.removeHandler(handler)
        cls.logger.addHandler(fh)

        for handler in cls.logger.handlers:
            if type(handler) is logging.StreamHandler:
                cls.logger.removeHandler(handler)
        cls.logger.addHandler(ch)

    @classmethod
    def get_logger(cls):
        return cls.logger
