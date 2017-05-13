Carpe Noctem Tactical Operations Cachet to Discord integration script
=====================================================================

.. image:: https://travis-ci.org/CntoDev/cachcord.svg?branch=master
    :target: https://travis-ci.org/CntoDev/cachcord
    :alt: Build Status
.. image:: https://api.codacy.com/project/badge/Grade/84a90d0ce9854b288aa237eeb09b6054
    :target: https://www.codacy.com/app/CNTODev/cachcord?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CntoDev/cachcord&amp;utm_campaign=Badge_Grade
    :alt: Codacy Grade
.. image:: https://api.codacy.com/project/badge/Coverage/84a90d0ce9854b288aa237eeb09b6054
    :target: https://www.codacy.com/app/CNTODev/cachcord?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CntoDev/cachcord&amp;utm_campaign=Badge_Coverage
    :alt: Codacy Coverage
.. image:: https://requires.io/github/CntoDev/cachcord/requirements.svg?branch=master
    :target: https://requires.io/github/CntoDev/cachcord/requirements/?branch=master
    :alt: Requirements Status

Cachcord is an utility script used by the Carpe Noctem Tacical Operations
community (http://carpenoctem.co) to provide Cachet component status updates
to a given Discord channel, using the Cachet API in one side,
and a Discord Webhook in the other.

Requirements
------------

- Python 3.5
- Third-party libraries defined in the ``setup.py`` file.

Installation
------------

To install the script in your environment (using a ``virtualenv`` is
recommended), download the source code and run the following command from
the source's root directory.

.. code-block:: bash

    $ pip install .

Usage
-----

.. code-block:: bash

    $ cachcord --help

    usage: cachcord [-h] [--debug] --config-path CONFIG_PATH --persist-path
                PERSIST_PATH

    Cachet to Discord synchronisation script

    optional arguments:
      -h, --help            show this help message and exit
      --debug               Set debugging on
      --config-path CONFIG_PATH
                            Path of the configuration file
      --persist-path PERSIST_PATH
                            Path of the persistence file

Configuration
-------------

To properly configure the script you must create a configuration file following
a ini-like syntax. An example is available in the `cachcord.ini.dist` file.

Please refer to Cachet's API documentation as well as Discord's developper
documentation in order to configure the API URL as well as the webhook
url, respectively.
======================
