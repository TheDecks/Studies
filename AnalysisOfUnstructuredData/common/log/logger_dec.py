import datetime
import AnalysisOfUnstructuredData.common.log.logger as ulog
import functools


class _LogDebugTime:
    def __init__(self, name_of_func: str, logger: ulog.LoggerUtil):
        self.name_of_func = name_of_func
        self.logger = logger

    def __enter__(self):
        self.logger.debug('Started function: {func}'.format(func=self.name_of_func))
        self.init_time = datetime.datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.logger.debug(
            'Finished: {func} in: {time} seconds'.format(
                func=self.name_of_func, time=datetime.datetime.now() - self.init_time
            )
        )


def debug_timer_dec(function=None, *, logger=None):

    def __decor(func):
        @functools.wraps(func)
        def f_wrapper(*args, **kwargs):
            with _LogDebugTime(func.__name__, logger):
                return func(*args, **kwargs)
        return f_wrapper

    if function:
        return __decor(function)

    return __decor
