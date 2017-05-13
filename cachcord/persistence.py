# -*- coding: utf-8 -*-

"""Data persistence module."""

import contextlib
import os
import shelve
import stat


@contextlib.contextmanager
def persistent_storage(file_path, *args, **kwargs):
    """Wraps shelve.open and makes a basic check on file permissions."""

    if os.path.isfile(file_path):
        file_mode = os.stat(file_path).st_mode
        if bool(stat.S_IWOTH & file_mode):
            raise RuntimeError('Persistence file %s has insecure permissions', file_path)
    with shelve.open(file_path, *args, **kwargs) as storage:
        yield storage


#  vim: set tabstop=4 shiftwidth=4 expandtab autoindent :
