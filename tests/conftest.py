# -*- coding: utf-8 -*-

"""Project-wide testing configuration module."""


def pytest_collection_modifyitems(config, items):
    """pytest item modification hook.

    Filters out items marked with ignore_on_fixturematch and whose `matches` kwargs return true.
    """

    _ = config

    filtered_items = list()
    for item in items:
        marker = item.get_marker("ignore_on_fixturematch")
        if marker is not None:
            if any(match(item.callspec.params) for match in marker.kwargs['matches']):
                continue
        filtered_items.append(item)
    items.clear()
    items.extend(filtered_items)

#  vim: set tabstop=4 shiftwidth=4 expandtab autoindent :
