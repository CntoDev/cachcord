# -*- coding: utf-8 -*-

"""INI settings wrapper module."""

import configparser


class CachcordConfigParser(configparser.ConfigParser):  # pylint: disable=R0901
    """ConfigParser that requires a file to be loaded before use."""

    _loaded = False

    def get(self, *args, **kwargs):  # pylint: disable=W0221
        if not self._loaded:
            raise RuntimeError('Settings requested before configuration load.')
        return super().get(*args, **kwargs)

    def _read(self, *args, **kwargs):  # pylint: disable=W0221
        self._loaded = True
        return super()._read(*args, **kwargs)

CONFIG = CachcordConfigParser()

#  vim: set tabstop=4 shiftwidth=4 expandtab autoindent :
