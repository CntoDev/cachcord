# -*- coding: utf-8 -*-

"""cachcord unit tests."""

import argparse
import logging
import os

import cachcord as unit
import cachcord.persistence as persistence

from test_cachet import api_components

_ = api_components


def test_main_function(mocker, api_components, tmpdir_factory):  # pylint: disable=W0621
    """Asserts the main function if working properly."""

    mocker.patch('cachcord.PARSER')
    mocker.patch('cachcord.LOGGER')
    mocker.patch('cachcord.discord.DiscordWebhook.send_message')

    persist_file_path = str(tmpdir_factory.mktemp('data').join('database.pickle3'))
    with persistence.persistent_storage(persist_file_path) as storage:
        last_component = api_components[-1].copy()
        last_component['status'] = 4
        last_component['status_name'] = "Major Outage"
        storage['last_update'] = last_component['updated_at']
        storage['components'] = {
            str(last_component['id']): last_component,
        }

    unit.PARSER.parse_args = mocker.Mock(return_value=argparse.Namespace(
        config_path=os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'fixtures',
            'cachcord.ini'
        ),
        persist_path=persist_file_path,
        debug=True,
    ))

    unit.entry_point()
    unit.LOGGER.setLevel.assert_called_with(logging.DEBUG)  # pylint: disable=E1101
    unit.cachet.CachetAPI.get.assert_called_with(  # pylint: disable=E1101
        mocker.ANY,
        params=mocker.ANY,
    )
    unit.discord.DiscordWebhook.send_message.assert_called_with(  # pylint: disable=E1101
        mocker.ANY
    )


#  vim: set tabstop=4 shiftwidth=4 expandtab autoindent :
