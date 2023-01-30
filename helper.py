from contextlib import contextmanager
import threading
import _thread

#https://stackoverflow.com/questions/366682/how-to-limit-execution-time-of-a-function-call - user2283347
class TimeoutException(Exception):
    def __init__(self, msg=''):
        self.msg = msg

@contextmanager
def time_limit(seconds, msg=''):
    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    # print(timer.enumerate())
    try:
        yield
    except KeyboardInterrupt:
        raise TimeoutException("Timed out for operation {}".format(msg))
    except RuntimeError:
        raise TimeoutException("Timed out for operation {}".format(msg))
    except ValueError:
        raise TimeoutException("Timed out for operation {}".format(msg))
    finally:
        # if the action ends in specified time, timer is canceled
        timer.cancel()

def run_function_with_timeout(time, msg, func, **kwargs):
    try:
        with time_limit(time, msg):
            return func(**kwargs)
    except TimeoutException as e:
        print(e.msg)
        return False
    except Exception as e:
        return False

def to_readable_string(var):
    if var in [False, 0]:
        return "❌"
    else:
        return "✅"
