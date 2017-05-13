# -*- coding: utf-8 -*-

"""cachcord.discord unit tests."""

import datetime
import time

from unittest.mock import ANY

import arrow
import pytest
import requests

from dateutil import tz as dateutil_tz

from cachcord import discord as unit


@pytest.fixture()
def webhook():
    """Returns a configured DiscordWebhook instance"""

    url = "https://dummy.tld/api/webhooks/000000000000000000" \
          "/aaaaaaaaaaaa-aaaaaaaaaaaaaaaaaaa-aaaaaaa-aaaaaaaaaaaaaaaaaaaa_aaaaaa"

    fixture = unit.DiscordWebhook(url=url)

    return fixture


class TimeMock(object):
    """Time-related operations mocking class."""

    def __init__(self, mocker):
        self.mocker = mocker
        self.mocked_timestamp = arrow.now().timestamp

        self.mocker.patch('time.sleep', side_effect=self.sleep)
        self.mocker.patch('arrow.now', side_effect=self.arrow_now)

    def arrow_now(self, tzinfo=None):
        """Mocks arrow.now()."""

        utc = datetime.datetime.fromtimestamp(self.mocked_timestamp).replace(
            tzinfo=dateutil_tz.tzutc()
        )
        dtime = utc.astimezone(dateutil_tz.tzlocal() if tzinfo is None else tzinfo)

        return arrow.Arrow(dtime.year, dtime.month, dtime.day, dtime.hour, dtime.minute,
                           dtime.second, dtime.microsecond, dtime.tzinfo)

    def sleep(self, delay):
        """Mocks time.sleep(delay)."""

        self.mocked_timestamp = self.mocked_timestamp + delay


@pytest.fixture(name="time_mock")
def time_mock(mocker):
    """Ensures all time-related oprations are mocked"""

    TimeMock(mocker)


def test_webhook_message_sending(mocker, webhook):  # pylint: disable=W0621
    """Asserts that DiscordWebhook properly formats messages to DiscordApp's API."""

    mocker.patch('requests.post')

    message = "test_webhook_message_sending"

    webhook.send_message(message)

    requests.post.assert_called_with(  # pylint:disable=E1101
        ANY,
        data={'content': message},
        params=ANY,
    )


def _side_effects_gen(side_effects):
    for func, arg, kwargs in side_effects:
        yield func(*arg, **kwargs)


def _generate_response(mocker, remaining=3, retry_after=1):
    """Mocks a requests.Response to contain Discord ratelimit headers"""

    response = mocker.Mock()
    response.headers = {
    }
    response.reason = "OK"
    response.raise_for_status = response.Response.raise_for_status
    response.status_code = 200

    response.headers['X-RateLimit-Limit'] = 5
    response.headers['X-RateLimit-Reset'] = arrow.now().shift(seconds=retry_after).timestamp

    if remaining == 0:
        response.headers['X-RateLimit-Remaining'] = 0
        response.headers['Retry-After'] = retry_after
        response.status_code = 429
        response.reason = "TOO MANY REQUESTS"
    else:
        response.headers['X-RateLimit-Remaining'] = remaining - 1

    return response


@pytest.mark.usefixtures("time_mock")
def test_webhook_ratelimit(mocker, webhook):  # pylint: disable=W0621
    """Asserts that DiscordWebhook supports rate limited requests."""

    mocker.patch('requests.post', side_effect=_side_effects_gen(
        (
            (_generate_response, (mocker,), {'remaining': 0}),
            (_generate_response, (mocker,), {'remaining': 3}),
        ),
    ))

    message = "test_webhook_ratelimit"

    webhook.send_message(message)

    assert requests.post.call_count == 2  # pylint:disable=E1101


class _DelayViolation(Exception):
    pass


def _generate_delaylimited_response(mocker, retry_after=3, reinitialize=False):
    """Mocks a requests.Response to raise an error if called too early."""

    now = arrow.now().timestamp
    if reinitialize:
        _generate_delaylimited_response.next_allowed = None
    elif now < _generate_delaylimited_response.next_allowed:  # pragma: no cover
        next_allowed = _generate_delaylimited_response.next_allowed
        raise _DelayViolation("Called at %s, next_allowed was %s" % (now, next_allowed))
    response = _generate_response(mocker, remaining=0, retry_after=retry_after)

    _generate_delaylimited_response.next_allowed = arrow.now().shift(seconds=retry_after).timestamp
    return response


@pytest.mark.usefixtures("time_mock")
def test_webhook_retrydelay(mocker, webhook):  # pylint: disable=W0621
    """Asserts that DiscordWebhook is a good internet citizen and respects Retry-After delay."""

    mocker.patch('requests.post', side_effect=_side_effects_gen(
        (
            (_generate_delaylimited_response, (mocker,), {'retry_after': 3, 'reinitialize': True}),
            (_generate_delaylimited_response, (mocker,), {'retry_after': 1}),
            (_generate_response, (mocker,), {}),
        ),
    ))

    message = "test_webhook_retrydelay"

    webhook.send_message(message)

    assert requests.post.call_count == 3  # pylint:disable=E1101


class _ResetViolation(Exception):
    pass


def _generate_resetlimited_response(mocker, retry_after=3, reinitialize=False, remaining=1):
    """Mocks a requests.Response to raise an error if X-RateLimit-Reset is violated."""

    now = arrow.now().timestamp
    if reinitialize:
        _generate_resetlimited_response.reset_time = None
    elif now < _generate_resetlimited_response.reset_time:  # pragma: no cover
        reset_time = _generate_resetlimited_response.reset_time
        raise _ResetViolation("Called at %s, reset was %s" % (now, reset_time))
    response = _generate_response(mocker, remaining=remaining)
    response.headers['Retry-After'] = retry_after

    reset_time = arrow.now().shift(seconds=retry_after).timestamp
    response.headers['X-RateLimit-Reset'] = reset_time
    _generate_resetlimited_response.reset_time = reset_time
    return response


@pytest.mark.usefixtures("time_mock")
def test_webhook_buffering(mocker, webhook):  # pylint: disable=W0621
    """Asserts that DiscordWebhook waits for the next X-RateLimit-Reset interval."""

    mocker.patch('requests.post', side_effect=_side_effects_gen(
        (
            (_generate_resetlimited_response, (mocker,), {'retry_after': 3, 'reinitialize': True}),
            (_generate_resetlimited_response, (mocker,), {'retry_after': 1, 'remaining': 5}),
            (_generate_resetlimited_response, (mocker,), {'retry_after': 3, 'reinitialize': True}),
            (_generate_resetlimited_response, (mocker,), {'retry_after': 1, 'remaining': 5}),
        ),
    ))

    message = "test_webhook_buffering"

    # First call: will go through but will be the last allowed request until reset is reached.
    webhook.send_message(message + "_1")

    # Second call: will trigger blocking call
    webhook.send_message(message + "_2")

    assert requests.post.call_count == 2  # pylint:disable=E1101
    requests.post.reset_mock()  # pylint:disable=E1101

    # Third call: will go through but will be the last allowed request until reset is reached.
    webhook.send_message(message + "_3")

    # Fourth call: will be buffered but next_reset will have already be reached.
    time.sleep(5)
    webhook.send_message(message + "_4")

    assert requests.post.call_count == 2  # pylint:disable=E1101


#  vim: set tabstop=4 shiftwidth=4 expandtab autoindent :
