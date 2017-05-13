#!/bin/env python3
# -*- coding: utf-8 -*-

"""Main entrypoint for cachcord."""

import argparse
import logging

import arrow

from . import cachet
from . import discord
from . import persistence
from . import settings

PARSER = argparse.ArgumentParser(
    description="Cachet to Discord synchronisation script",
)
PARSER.add_argument(
    '--debug',
    const=True,
    default=False,
    action='store_const',
    help="Set debugging on",
)
PARSER.add_argument(
    '--config-path',
    required=True,
    help="Path of the configuration file",
)
PARSER.add_argument(
    '--persist-path',
    required=True,
    help="Path of the persistence file",
)

LOGGER = logging.getLogger()


def main(config_path, persist_path, debug=False):
    """Main function."""

    if debug:
        LOGGER.setLevel(logging.DEBUG)
    logging.info("Setting debug to %s", debug)

    settings.CONFIG.read(config_path)

    last_update = arrow.now()
    with persistence.persistent_storage(persist_path, writeback=True) as storage:
        if 'last_update' in storage:
            last_update = arrow.get(storage['last_update'])
            logging.info('Last run detected, was on %s', last_update.isoformat())
        api = cachet.CachetAPI(
            token=settings.CONFIG.get('Cachet', 'api_token'),
            base_url=settings.CONFIG.get('Cachet', 'api_url'),
        )
        feed = cachet.CachetComponentUpdateFeed(
            api=api,
            storage=storage,
            last_update=last_update,
        )
        try:
            for component in feed.updates:
                new_status = component['status_name']
                symbol = ":warning: :warning:"
                if new_status == 'Operational':
                    symbol = ":ballot_box_with_check: :ballot_box_with_check:"
                webhook = discord.DiscordWebhook(settings.CONFIG.get('Discord', 'webhook_url'))
                message = settings.CONFIG.get('Discord', 'message_template').format(
                    symbol=symbol,
                    component=component,
                )
                webhook.send_message(message)
                last_update = feed.last_update
        finally:
            storage['last_update'] = last_update.isoformat()


def entry_point():
    """Setuptools' CLI entry point."""

    args = PARSER.parse_args()
    LOGGER.setLevel(logging.WARNING)
    main(**args.__dict__)

if __name__ == '__main__':  # pragma: no cover
    entry_point()


#  vim: set tabstop=4 shiftwidth=4 expandtab autoindent :
