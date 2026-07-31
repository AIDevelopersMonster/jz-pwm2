"""Минимальный драйвер JZ-PWM2.

Поддерживает только документированные диапазоны до 99,9 кГц.
Для работы с портом установите pyserial: pip install pyserial
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


class JZPWM2Error(RuntimeError):
    """Ошибка протокола или устройства."""


def _validate_channel(channel: int) -> None:
    if channel not in (1, 2):
        raise ValueError("channel должен быть 1 или 2")


def build_frequency_command(channel: int, frequency_hz: float) -> str:
    """Сформировать команду частоты в подтвержденном диапазоне 1..99900 Гц."""
    _validate_channel(channel)
    if not 1 <= frequency_hz <= 99_900:
        raise ValueError(
            "Поддерживается только 1..99900 Гц. Формат 100..150 кГц пока не подтвержден."
        )

    if frequency_hz <= 999 and float(frequency_hz).is_integer():
        value = f"{int(frequency_hz):03d}"
    else:
        khz = frequency_hz / 1000.0
        rounded = round(khz, 1)
        if abs(khz - rounded) > 1e-9:
            raise ValueError("В диапазоне кГц доступен шаг 0,1 кГц")
        value = f"{rounded:.1f}"

    return f"S{channel}F{value}T"


def build_duty_command(channel: int, duty_percent: int) -> str:
    """Сформировать команду заполнения 1..100%."""
    _validate_channel(channel)
    if not 1 <= duty_percent <= 100:
        raise ValueError("Документированный диапазон duty: 1..100%")
    return f"S{channel}D{duty_percent:03d}T"


@dataclass
class Reply:
    raw: str
    success: bool
    known: bool


def parse_reply(text: str) -> Reply:
    normalized = text.strip().upper()
    if normalized in {"DOWN", "DONE"}:
        return Reply(raw=text, success=True, known=True)
    if normalized in {"FALL", "FAIL"}:
        return Reply(raw=text, success=False, known=True)
    return Reply(raw=text, success=False, known=False)


class JZPWM2:
    def __init__(self, port: str, timeout: float = 1.0) -> None:
        try:
            import serial
        except ImportError as exc:
            raise RuntimeError("Установите pyserial: pip install pyserial") from exc

        self._serial = serial.Serial(
            port=port,
            baudrate=9600,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=timeout,
        )

    def close(self) -> None:
        self._serial.close()

    def __enter__(self) -> "JZPWM2":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _send(self, command: str) -> Reply:
        self._serial.reset_input_buffer()
        self._serial.write(command.encode("ascii"))
        self._serial.flush()
        raw = self._serial.readline().decode("ascii", errors="replace")
        reply = parse_reply(raw)
        if not reply.known:
            raise JZPWM2Error(f"Неизвестный ответ: {raw!r}")
        if not reply.success:
            raise JZPWM2Error(f"Модуль отклонил команду {command!r}: {raw!r}")
        return reply

    def set_frequency(self, channel: int, frequency_hz: float) -> Reply:
        return self._send(build_frequency_command(channel, frequency_hz))

    def set_duty(self, channel: int, duty_percent: int) -> Reply:
        return self._send(build_duty_command(channel, duty_percent))
