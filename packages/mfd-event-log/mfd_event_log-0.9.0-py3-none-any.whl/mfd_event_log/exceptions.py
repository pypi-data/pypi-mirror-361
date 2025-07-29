# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Exceptions for Event Log."""

import subprocess


class EventLogException(Exception):
    """Handle EventLog Exceptions."""


class EventLogExecutionError(EventLogException, subprocess.CalledProcessError):
    """Handle EventLog Execution errors."""
