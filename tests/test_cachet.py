# -*- coding: utf-8 -*-

"""cachcord.cachet unit tests."""

import json
import os
import re
import unittest.mock

import pytest
import requests

from cachcord import cachet as unit


def _load_from_json(file_name):
    file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures', file_name)
    with open(file_path, 'r') as json_file:
        return json.load(json_file)


@pytest.fixture(scope="module")
def api_config():
    """Returns basic Cachet API configuration."""

    return {
        'url': "https://dummy.tld/api/v1",
        'token': 'aaaaaaaaaaaaaaaaaaaa',
    }


@pytest.fixture(scope="module")
def api(api_config):  # pylint: disable=W0621
    """Returns a ready to use CachetAPI instance"""

    return unit.CachetAPI(
        token=api_config['token'],
        base_url=api_config['url'],
    )


def test_api_authentication(mocker, api_config, api):  # pylint: disable=W0621
    """Asserts that CachetAPI properly format requests credentials to the Cachet instance's API."""

    mocker.patch('requests.get')
    endpoint = '/components'

    api.get(endpoint)

    requests.get.assert_called_with(  # pylint: disable=E1101
        api_config['url'] + endpoint,
        headers={
            'X-Cachet-Token': api_config['token'],
        },
    )


@pytest.fixture(scope="function", params=_load_from_json('cachcord_storage_states.json'))
def storage(request):  # pylint: disable=W0621
    """Fixture providing a persistent database storage mockup, with varying state."""

    return request.param.copy()


@pytest.fixture(scope="function")
def feed(api, storage):  # pylint: disable=W0621
    """Returns a ready to use CachetComponentUpdateFeed instance"""

    return unit.CachetComponentUpdateFeed(
        api=api,
        storage=storage,
    )


@pytest.fixture(scope="function")
def api_components(mocker):
    """Fixture generating and mocking Cachet's API endpoint for components."""

    components = _load_from_json('cachet_api_components.json')

    original_get = unit.CachetAPI.get

    def side_effect(endpoint, *args, **kwargs):
        """Endpoint router side effect."""

        match = re.match(r'\/components', endpoint)
        if match:
            inner = unittest.mock.Mock()
            inner.json = unittest.mock.Mock(return_value=components)
            return inner
        return original_get(endpoint, *args, **kwargs)  # pragma: no cover

    mocker.patch('cachcord.cachet.CachetAPI.get', side_effect=side_effect)

    return components['data']


def test_components_fetching(feed, api_components):  # pylint: disable=W0621
    """Asserts that CachetComponentUpdateFeed properly manages fetching Cachet components."""

    assert len(list(feed.components)) == len(list(api_components))


@pytest.fixture(scope="function")
def api_paginated_components(mocker):
    """Fixture generating and mocking Cachet's API endpoint for components."""

    components_pages = [
        _load_from_json('cachet_api_components_pagination_1.json'),
        _load_from_json('cachet_api_components_pagination_2.json'),
    ]

    original_get = unit.CachetAPI.get

    def side_effect(endpoint, *args, **kwargs):
        """Endpoint router side effect."""

        match = re.match(r'\/components', endpoint)
        if match:
            inner = unittest.mock.Mock()
            inner.json = unittest.mock.Mock(
                return_value=components_pages[side_effect.current_page],
            )
            side_effect.current_page += 1
            return inner
        return original_get(endpoint, *args, **kwargs)  # pragma: no cover

    mocker.patch('cachcord.cachet.CachetAPI.get', side_effect=side_effect)
    side_effect.current_page = 0

    return [component for components in components_pages for component in components['data']]


def test_components_pagination(feed, api_paginated_components):  # pylint: disable=W0621
    """Asserts that CachetComponentUpdateFeed properly manages fetching paginated components."""

    assert len(list(feed.components)) == len(list(api_paginated_components))


@pytest.fixture(scope="function", params=_load_from_json('cachet_api_components.json')['data'])
def api_component(mocker, request):
    """Fixture providing a single Cachet component."""

    component = request.param.copy()

    components_property = unittest.mock.PropertyMock(return_value=(elem for elem in [component]))
    mocker.patch(
        'cachcord.cachet.CachetComponentUpdateFeed.components',
        new_callable=components_property
    )

    return component


@pytest.mark.ignore_on_fixturematch(
    matches=[
        lambda params: 'components' in params['storage'],
    ],
)
def test_component_update_fresh(feed, api_component):  # pylint: disable=W0621
    """Asserts that CachetComponentUpdateFeed does not detect any update upon initialization."""

    _ = api_component

    assert not any(feed.updates)


@pytest.mark.ignore_on_fixturematch(
    matches=[
        lambda params: 'components' not in params['storage'],
        lambda params: str(params['api_component']['id']) not in params['storage']['components'],
        lambda params: (
            params['storage']['components'][str(params['api_component']['id'])]['status'] !=
            params['api_component']['status']
        ),
    ],
)
def test_component_update_unchanged(feed, api_component):  # pylint: disable=W0621
    """Asserts that CachetComponentUpdateFeed does not detect updates on an unchanged component."""

    _ = api_component

    assert not any(feed.updates)


@pytest.mark.ignore_on_fixturematch(
    matches=[
        lambda params: 'components' not in params['storage'],
        lambda params: str(params['api_component']['id']) not in params['storage']['components'],
        lambda params: (
            params['storage']['components'][str(params['api_component']['id'])]['status'] ==
            params['api_component']['status']
        ),
    ],
)
def test_component_update_changed(feed, api_component):  # pylint: disable=W0621
    """Asserts that CachetComponentUpdateFeed detects updates on a changed component."""

    assert api_component in feed.updates

#  vim: set tabstop=4 shiftwidth=4 expandtab autoindent :
