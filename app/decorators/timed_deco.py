import functools
import time
from typing import Callable, Any
from app.log import get_log

log = get_log()


def timed(func: Callable) -> Callable:
    """Measure elapsed time of functions execution."""
    @functools.wraps(func)
    async def wrapped(*args, **kwargs) -> Any:
        try:
            start_time = time.time()
            res = await func(*args, **kwargs)
            elapsed_time = time.time() - start_time

            log.debug("Function executed; module=%s; function=%s; "
                      "elapsed_time=%s; args=%s; kwargs=%s; res=%s;" % (
                          func.__module__, func.__qualname__, elapsed_time,
                          str(args), str(kwargs), str(res)))

            return res

        except Exception as e:
            elapsed_time = time.time() - start_time

            log.error(
                "Function failed; module=%s; function=%s; elapsed_time=%s; "
                "args=%s; kwargs=%s; e=%s;" % (
                    func.__module__, func.__qualname__,
                    "{0:.10f}".format(elapsed_time), str(args), str(kwargs),
                    str(e)))

            raise e

    return wrapped
