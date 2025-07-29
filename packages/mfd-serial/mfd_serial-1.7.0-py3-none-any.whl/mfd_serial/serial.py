# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for Serial driver."""

import logging
import threading
import serial

from mfd_common_libs import TimeoutCounter, add_logging_level, log_levels


logger = logging.getLogger(__name__)
add_logging_level("MODULE_DEBUG", log_levels.MODULE_DEBUG)


class SerialConnection:
    """Class for serial communication."""

    def __init__(self, serial_port: str, baud: int, encoding: str = "UTF-8") -> None:
        """Open serial connection.

        :param serial_port: serial port for opening connection
        :param baud: baud rate - connection speed
        :param encoding: string encoding / decoding method

        Usage example:
        >>> conn = SerialConnection(serial_port='/dev/ttyUSB0', baud=115200)
        >>> conn.read()
        >>> conn.send('Text to send')
        >>> conn.close()
        """
        self._serial_port = serial_port
        self._encoding = encoding
        self._data = ""
        self._stop = False
        self._serial_connection = serial.Serial(serial_port, baud, timeout=10)
        self._thread = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # noqa
        self.close()

    def send(self, msg: str) -> None:
        """Send message via serial console.

        :param msg: Message to be sent via serial port
        """
        logger.log(level=log_levels.MODULE_DEBUG, msg=f"Sending uart message: {msg}")
        self._serial_connection.write(msg.encode(self._encoding))

    def close(self) -> None:
        """Close serial connection."""
        self._serial_connection.flushOutput()
        self._serial_connection.close()

    def read(self) -> str:
        """Read output from serial console.

        :return: console output
        """
        data = ""
        buff = self._serial_connection.in_waiting
        if buff > 0:
            data = self._serial_connection.read(buff).decode(self._encoding)
        return data

    def read_until(
        self,
        until: str,
        timeout: int = 60,
    ) -> str:
        """Read console output until some expression appear.

        :param until: expression to be appeared
        :param timeout: time method shall wait for expression
        :return: output from serial console
        """
        timeout = TimeoutCounter(timeout, first_check_start=False)
        data = ""
        while until not in data:
            line = self._serial_connection.readline()
            if line:
                data += line.decode(self._encoding)
            if timeout:
                logger.log(level=log_levels.MODULE_DEBUG, msg=f"Read until timeout occurred! Phrase {until} not found!")
                break
        return data

    def read_in_background(self) -> None:
        """Start reading in background from serial, as a thread and reads until thread is killed."""
        logger.log(level=log_levels.MODULE_DEBUG, msg=f"Start reading from serial console: {self._serial_port}")
        self._thread = threading.Thread(target=self._read_in_background, args=[])
        self._thread.start()

    def _read_in_background(self) -> None:
        """Read output from serial console until <stop> param is set on True."""
        self._stop = False
        self._data = ""
        while not self._stop:
            line = self._serial_connection.readline()
            if line:
                line = line.decode(self._encoding)
                self._data += line

    def get_result(self) -> str:
        """Stop reading from serial console thread and returns captured output.

        :return: captured output from serial console
        """
        self._stop = True
        self._thread.join()
        self.close()
        return self._data
