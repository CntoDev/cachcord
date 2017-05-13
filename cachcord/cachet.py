# -*- coding: utf-8 -*-

"""Cachet interactions module."""

import logging

import arrow
import requests


class CachetAPI(object):  # pylint: disable=R0903
    """Provides an abstraction to a given Cachet installation's Web API."""

    def __init__(self, token, base_url="https://demo.cachethq.io/api/v1"):
        self.token = token
        self.base_url = base_url

    def _method(self, name, endpoint, *args, **kwargs):
        """Injects authentication, executes the request and verify response status code."""

        if 'headers' not in kwargs:
            kwargs['headers'] = dict()
        kwargs['headers']['X-Cachet-Token'] = self.token

        url = self.base_url + endpoint
        response = requests.__dict__[name](url, *args, **kwargs)
        response.raise_for_status()
        logging.debug("CachetAPI.%s(%s): %s", name, endpoint, response)
        return response

    def get(self, endpoint, *args, **kwargs):
        """Provides access to the HTTP GET method on the API."""

        return self._method('get', endpoint, *args, **kwargs)


class CachetComponentUpdateFeed(object):
    """Provides an interface for fetching component updates since last run."""

    def __init__(self, api, storage, last_update=None):
        self.api = api
        self.storage = storage

        if last_update is None:
            last_update = arrow.now()
        self.last_update = last_update

    @property
    def components(self):
        """Generator which yields all components."""

        current_page = 1
        finished = False
        while not finished:
            response = self.api.get(
                '/components',
                params={
                    'page': current_page,
                },
            )
            data = response.json()

            for component in data['data']:
                yield component

            if data['meta']['pagination']['total_pages'] <= current_page:
                finished = True
            else:
                current_page = current_page + 1

    @property
    def updates(self):
        """Generator which yields any component update that happened since last run."""

        if 'components' not in self.storage:
            self.storage['components'] = dict()
        for current_component in self.components:
            self.last_update = arrow.get(current_component['created_at'])
            current_id = str(current_component['id'])
            if current_id not in self.storage['components']:
                self.storage['components'][current_id] = current_component
                continue
            old_component = self.storage['components'][current_id]
            previous_status = old_component['status']
            if previous_status != current_component['status']:
                self.storage['components'][current_id] = current_component
                yield current_component

#  vim: set tabstop=4 shiftwidth=4 expandtab autoindent :
