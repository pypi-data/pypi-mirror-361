# This file is part of fm-weck: executing fm-tools in containerized environments.
# https://gitlab.com/sosy-lab/software/fm-weck
#
# SPDX-FileCopyrightText: 2024 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import contextlib
import os
from pathlib import Path
from tempfile import mkdtemp


class NTempFile:
    """
    Custom temporary file context manager.
    It creates a temporary file and deletes it after the context manager is closed.
    The file is not kept open in order to achieve compatibility with Windows.

    Inspired by https://stackoverflow.com/a/63173312
    """

    def __init__(self, name, mode="wb"):
        self.__tmp_dir = mkdtemp()
        self.name = Path(self.__tmp_dir) / name
        self._mode = mode
        self._file = None

    def __enter__(self):
        """Enter the context manager and return the file object."""
        self._file = open(self.name, self._mode)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and clean up."""
        if self._file is not None:
            self._file.close()
        self._cleanup()

    def write(self, data):
        """Write data to the temporary file."""
        if self._file is None:
            # If not in context manager, open the file temporarily
            with open(self.name, self._mode) as f:
                f.write(data)
        else:
            self._file.write(data)
            self._file.flush()  # Ensure data is written immediately

    def _cleanup(self):
        """Clean up the temporary file and directory."""
        with contextlib.suppress(OSError):
            if self.name.exists():
                os.unlink(self.name)
        with contextlib.suppress(OSError):
            if Path(self.__tmp_dir).exists():
                os.rmdir(self.__tmp_dir)

    def __del__(self):
        """Cleanup when object is garbage collected."""
        self._cleanup()
