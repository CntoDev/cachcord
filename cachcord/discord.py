# -*- coding: utf-8 -*-

"""Discord-related operations module."""

import logging
import time

import arrow
import requests


class DiscordWebhook(object):  # pylint: disable=R0903
    """Discord webhook-based interaction class."""

    def __init__(self, url):
        self.url = url

        self.rate_exhausted = False
        self.next_reset = None

    def send_message(self, message):
        """Send a message through the Discord webhook.

        See https://discordapp.com/developers/docs/resources/webhook#execute-webhook
        """

        logging.debug("DiscordWebhook.send_message(%s)", message)
        message_submitted = False
        request_delay = 0
        if self.rate_exhausted:
            request_delay = self.next_reset - arrow.now().timestamp
            logging.debug('DiscordWebhook.send_message(%s), rate was exhausted, delay=%d',
                          message, request_delay)
            if request_delay < 0:
                request_delay = 0
        response = None
        while not message_submitted:
            if request_delay:
                time.sleep(request_delay)
                request_delay = 0
                self.rate_exhausted = False
                self.next_reset = None
            response = requests.post(
                self.url,
                params={
                    'wait': True,
                },
                data={
                    'content': message,
                },
            )
            if response.status_code == 429:
                request_delay = int(response.headers['Retry-After'])
                logging.debug(
                    'DiscordWebhook.send_message(%s):Rate limited, retrying in %ds',
                    message,
                    request_delay,
                )
                continue
            else:
                message_submitted = True
        if response.headers['X-RateLimit-Remaining'] == 0:
            self.rate_exhausted = True
            self.next_reset = int(response.headers['X-RateLimit-Reset'])
            logging.debug(
                'DiscordWebhook.send_message(%s):Last request exhausted rate, reset=%d',
                message,
                self.next_reset,
            )
        response.raise_for_status()
        return response.json()

#  vim: set tabstop=4 shiftwidth=4 expandtab autoindent :
