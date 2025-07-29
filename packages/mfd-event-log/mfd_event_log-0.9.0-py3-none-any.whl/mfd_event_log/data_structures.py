# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Enum for EventLog module."""

from enum import Enum


class EventType(Enum):
    """Enum class for event type of EventLog."""

    ALL = "All"
    ERROR = "Error"
    INFORMATION = "Information"
    SUCCESSAUDIT = "SuccessAudit"
    FAILUREAUDIT = "FailureAudit"
    WARNING = "Warning"
