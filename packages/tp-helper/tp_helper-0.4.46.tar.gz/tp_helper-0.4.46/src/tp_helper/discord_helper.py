import inspect
import logging
import traceback
from pathlib import Path

import aiohttp
from typing import Optional


class DiscordHelper:
    RED = 16711680
    GREEN = 5025616
    YELLOW = 16776960

    MAX_DISCORD_CONTENT = 2000
    MAX_DISCORD_EMBED_DESC = 4096
    MAX_DISCORD_EMBED_TITLE = 256

    def __init__(self, url: str):
        self.url: str = url
        self.title: Optional[str] = None
        self.description: Optional[str] = None
        self.color: Optional[int] = None
        self.notify_everyone: bool = False
        self.proxy: Optional[str] = None  # Прокси-сервер (по умолчанию отключен)

    def reset(self) -> "DiscordHelper":
        """Сбрасывает все параметры сообщения к значениям по умолчанию."""
        self.title = None
        self.description = None
        self.color = None
        self.notify_everyone = False
        return self

    def set_proxy(self, proxy_url: str) -> "DiscordHelper":
        """
        Устанавливает прокси-сервер (HTTP, HTTPS, SOCKS5).

        # HTTP-прокси (обычный)
        discord.set_proxy("http://1.1.1.1:1080")

        # HTTPS-прокси
        discord.set_proxy("https://user:password@proxy.example.com:8080")

        # SOCKS5-прокси (например, через Tor)
        discord.set_proxy("socks5h://127.0.0.1:9050")
        """
        self.proxy = proxy_url
        return self

    def set_title(self, title: str) -> "DiscordHelper":
        """Устанавливает заголовок сообщения."""
        self.title = title
        return self

    def set_description(self, description: str) -> "DiscordHelper":
        """Устанавливает описание сообщения."""
        self.description = self._trim(description, self.MAX_DISCORD_EMBED_DESC)
        return self

    def set_color(self, color: int) -> "DiscordHelper":
        """Устанавливает цвет сообщения (в формате int)."""
        self.color = color
        return self

    def set_color_red(self) -> "DiscordHelper":
        """Устанавливает цвет сообщения на красный (ошибка)."""
        return self.set_color(self.RED)

    def set_color_green(self) -> "DiscordHelper":
        """Устанавливает цвет сообщения на зеленый (успех, информация)."""
        return self.set_color(self.GREEN)

    def set_color_yellow(self) -> "DiscordHelper":
        """Устанавливает цвет сообщения на желтый (предупреждение)."""
        return self.set_color(self.YELLOW)

    def set_notify_everyone(self) -> "DiscordHelper":
        """Определяет, следует ли упоминать @everyone в сообщении."""
        self.notify_everyone = True
        return self

    async def send_with_level(
        self, level: str, message: str = None, desc: Optional[str] = None
    ):
        """Отправляет сообщение с заданным уровнем (Error, Warning, Info)."""
        if self.title is None:
            self.set_title(f"[{level}]")
        if desc:
            self.set_description(desc)
        await self.send(message)

    async def send_error(self, message: str = None, desc: Optional[str] = None):
        """Отправляет сообщение об ошибке."""
        self.set_color_red()
        self.set_notify_everyone()
        await self.send_with_level("Error", message, desc)

    async def send_traceback_report(self, e: Exception, desc: str) -> None:
        """
        Отправляет сообщение об ошибке с автоматически сформированным заголовком вида:
        (ClassName) file_name.py
        """
        tb = traceback.extract_tb(e.__traceback__)
        if tb:
            last = tb[-1]
            filename = Path(last.filename).name
            lineno = last.lineno
            line = last.line
        else:
            filename = "unknown.py"
            lineno = -1
            line = ""

            # Пытаемся найти имя класса из стека вызова
        class_name = "UnknownClass"
        stack = inspect.stack()
        for frame_info in stack:
            self_obj = frame_info.frame.f_locals.get("self")
            if self_obj and self_obj.__class__.__name__ != self.__class__.__name__:
                class_name = self_obj.__class__.__name__
                break

        self.set_title(f"({class_name}) {filename}:{lineno}")
        self.set_color_red()
        self.set_notify_everyone()

        # Формируем текст ошибки
        tb_text = "".join(
            traceback.format_exception(type(e), e, e.__traceback__)
        ).strip()
        formatted_message = f"```{tb_text}```"

        await self.send_error(message=formatted_message, desc=desc)

    async def send_warning(self, message: str = None, desc: Optional[str] = None):
        """Отправляет предупреждающее сообщение."""
        self.set_color_yellow()
        await self.send_with_level("Warning", message, desc)

    async def send_info(self, message: str = None, desc: Optional[str] = None):
        """Отправляет информационное сообщение."""
        self.set_color_green()
        await self.send_with_level("Info", message, desc)

    async def send(self, message: Optional[str] = None):
        """Отправляет сообщение с текущими параметрами."""
        if not message:
            message = ""
        await self._send_message(message)

    async def _send_message(self, message: str):
        """Отправляет сообщение в Discord через Webhook с использованием прокси (если задано)."""

        message = self._trim(message, self.MAX_DISCORD_CONTENT)
        self.title = self._trim(self.title, self.MAX_DISCORD_EMBED_TITLE)

        payload = {
            "content": f"{'@everyone ' if self.notify_everyone else ''}{message}",
            "tts": False,
            "username": "🤖️",
            "embeds": [
                {
                    "title": self.title,
                    "description": self.description,
                    "color": self.color,
                }
            ],
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url, json=payload, proxy=self.proxy
                ) as response:
                    if response.status != 204:
                        logging.warning(
                            f"Ошибка отправки в Discord: {response.status} - {await response.text()}"
                        )
        except Exception as e:
            logging.error(traceback.format_exc())
            logging.error(f"Ошибка при отправке сообщения в Discord: {e}")

        self.reset()

    @staticmethod
    def _trim(text: Optional[str], limit: int) -> Optional[str]:
        if text is None:
            return None
        suffix = "\n... [truncated]"
        if len(text) <= limit:
            return text
        return text[: limit - len(suffix)].rstrip() + suffix
