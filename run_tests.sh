#!/bin/bash
# -*- coding: utf-8 -*-

pytest \
  "$@" \
  --pep8 \
  --pylint \
  --cov=cachcord --cov=tests --cov-report term-missing --cov-report=xml \
