"""PySide6 QIODevice wrapper."""

from pathlib import Path
from typing import Any

from PySide6.QtCore import QFile, QIODevice


class PyQIODevice(QIODevice):
    """QFile subclass that decrypts data on read."""

    def __init__(self, q_device: QIODevice, *args: Any, **kwargs: Any) -> None:
        """Initialize the device."""
        super().__init__(*args, **kwargs)
        self.q_device = q_device

    def atEnd(self) -> bool:  # noqa: N802
        """Check if we are at the end of the file."""
        return self.q_device.atEnd()

    def bytesAvailable(self) -> int:  # noqa: N802
        """Return the number of bytes available for reading."""
        return self.q_device.bytesAvailable()

    def bytesToWrite(self) -> int:  # noqa: N802
        """Return the number of bytes available for writing."""
        return self.q_device.bytesToWrite()

    def canReadLine(self) -> bool:  # noqa: N802
        """Check if we can read a line."""
        return self.q_device.canReadLine()

    def close(self) -> None:
        """Close the device."""
        self.q_device.close()
        return super().close()

    def isSequential(self) -> bool:  # noqa: N802
        """Check if the device is sequential."""
        return self.q_device.isSequential()

    def open(self, mode: QIODevice.OpenModeFlag) -> bool:
        """Open the device."""
        self.q_device.open(mode)
        return super().open(mode)

    def pos(self) -> int:
        """Return the current position in the device."""
        return self.q_device.pos()

    def readData(self, maxlen: int) -> bytes:  # noqa: N802
        """Read data from the device."""
        return bytes(self.q_device.read(maxlen).data())

    def readLineData(self, maxlen: int) -> object:  # noqa: N802
        """Read a line from the device."""
        return self.q_device.readLine(maxlen)

    def reset(self) -> bool:
        """Reset the device."""
        return self.q_device.reset()

    def seek(self, pos: int) -> bool:
        """Seek to a position in the device."""
        return self.q_device.seek(pos)

    def size(self) -> int:
        """Return the size of the device."""
        return self.q_device.size()

    def skipData(self, maxSize: int) -> int:  # noqa: N802, N803
        """Skip data in the device."""
        return self.q_device.skip(maxSize)

    def waitForBytesWritten(self, msecs: int) -> bool:  # noqa: N802
        """Wait for bytes to be written."""
        return self.q_device.waitForBytesWritten(msecs)

    def waitForReadyRead(self, msecs: int) -> bool:  # noqa: N802
        """Wait for the device to be ready to read."""
        return self.q_device.waitForReadyRead(msecs)

    def writeData(self, data: bytes | bytearray | memoryview, len: int) -> int:  # noqa: A002, ARG002, N802
        """Write data to the device."""
        return self.q_device.write(data)


class PyQFile(PyQIODevice):
    """QFile subclass."""

    def __init__(self, path: Path, *args: Any, **kwargs: Any) -> None:
        """Initialize the device."""
        super().__init__(QFile(path), *args, **kwargs)
