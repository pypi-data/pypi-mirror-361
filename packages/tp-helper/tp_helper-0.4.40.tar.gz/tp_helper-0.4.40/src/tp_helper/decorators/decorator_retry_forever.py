import asyncio
import functools
import inspect
import traceback
from typing import Callable, Any

from tp_helper import get_full_class_name


def retry_forever(
    start_message: str,
    error_message: str,
    delay: int = 10,
    backoff: float = 1.2,
    max_delay: int = 60,
):
    def decorator(func: Callable) -> Callable:
        # Анализ сигнатуры один раз
        sig = inspect.signature(func)
        expects_retry_count = "retry_count" in sig.parameters

        @functools.wraps(func)
        async def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            try:
                bound = sig.bind(self, *args, **kwargs)
                bound.apply_defaults()
                context = dict(bound.arguments)
            except Exception:
                context = {"self": self}

            str_context = {k: str(v) for k, v in context.items()}

            try:
                self.logger.debug(start_message.format_map(str_context))
            except Exception:
                self.logger.debug(start_message)

            current_delay = delay
            retry_count = kwargs.get("retry_count", 0)

            while True:
                try:
                    if expects_retry_count:
                        kwargs["retry_count"] = retry_count
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    retry_count += 1
                    str_context_with_exception = {
                        **str_context,
                        "e": str(e),
                        "retry_count": retry_count,
                    }

                    try:
                        msg = error_message.format_map(str_context_with_exception)
                    except Exception:
                        msg = error_message

                    error_type = get_full_class_name(e)
                    error_text = str(e)

                    self.logger.error(f"❌ {msg}")
                    self.logger.error(f"{error_type}: {error_text}")

                    tb = traceback.extract_tb(e.__traceback__)
                    if tb:
                        last = tb[-1]
                        self.logger.error(
                            f"📍 В {last.filename}:{last.lineno} — {last.name} → {last.line}"
                        )

                    self.logger.info(
                        f"🔁 Повтор #{retry_count} через {current_delay:.1f} сек..."
                    )
                    await asyncio.sleep(current_delay)
                    current_delay = min(current_delay * backoff, max_delay)

        return wrapper

    return decorator
