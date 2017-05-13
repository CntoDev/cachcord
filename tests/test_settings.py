# -*- coding: utf-8 -*-

"""cachcord.settings unit tests."""

import pytest

from cachcord import settings as unit


def test_unloaded_configurator():
    """Asserts that CachcordConfigParser raises when used without having loaded a file."""

    config_parser = unit.CachcordConfigParser()
    with pytest.raises(RuntimeError):
        config_parser.get('dummy_section', 'dummy_value')


@pytest.fixture(scope="module")
def config_file(tmpdir_factory):
    """Fixture that generates a useable configuration file."""
    tmpfile = tmpdir_factory.mktemp('data').join('config.ini')
    tmpfile.write(
        "[TestSection]\n"
        "key = value\n"
    )
    return tmpfile.strpath


def test_configurator_loading(config_file):  # pylint: disable=W0621
    """Asserts that CachcordConfigParser successfully loads a configuration file."""

    config_parser = unit.CachcordConfigParser()
    config_parser.read(config_file)


def test_configurator_fetching(config_file):  # pylint: disable=W0621
    """Asserts that CachcordConfigParser successfully fetches a given setting."""

    config_parser = unit.CachcordConfigParser()
    config_parser.read(config_file)
    assert config_parser.get('TestSection', 'key') == "value"

#  vim: set tabstop=4 shiftwidth=4 expandtab autoindent :
