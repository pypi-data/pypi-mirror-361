import functools
from bdb import BdbQuit
from collections.abc import Callable

from rra_tools.logging import SupportsLogging


def handle_exceptions[**P, T](
    func: Callable[P, T],
    logger: SupportsLogging,
    *,
    with_debugger: bool,
) -> Callable[P, T]:
    """Drops a user into an interactive debugger if func raises an error."""

    @functools.wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:  # type: ignore[return]
        try:
            return func(*args, **kwargs)
        except (BdbQuit, KeyboardInterrupt):
            raise
        except Exception:
            msg = "Uncaught exception"
            logger.exception(msg)
            if with_debugger:
                import pdb  # noqa: T100
                import traceback

                traceback.print_exc()
                pdb.post_mortem()
            else:
                raise

    return wrapped
