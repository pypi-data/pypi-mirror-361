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
    on_retry_error: str | None = None,
):
    def decorator(func: Callable) -> Callable:
        sig = inspect.signature(func)

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
            retry_count = 0



            while True:
                try:
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

                    self.logger.error(f"❌ {msg}")
                    self.logger.error(f"{get_full_class_name(e)}: {str(e)}")

                    tb = traceback.extract_tb(e.__traceback__)
                    if tb:
                        last = tb[-1]
                        self.logger.error(
                            f"📍 В {last.filename}:{last.lineno} — {last.name} → {last.line}"
                        )

                    # ⛑ Вызов пользовательского обработчика ошибки
                    if on_retry_error:
                        hook = getattr(self, on_retry_error, None)
                        if callable(hook):
                            try:
                                await hook(e, retry_count=retry_count, **kwargs)
                            except Exception as hook_error:
                                self.logger.warning(
                                    f"⚠️ Ошибка в on_retry_error: {hook_error}"
                                )

                    self.logger.info(
                        f"🔁 Повтор #{retry_count} через {current_delay:.1f} сек..."
                    )
                    await asyncio.sleep(current_delay)
                    current_delay = min(current_delay * backoff, max_delay)

        return wrapper

    return decorator
