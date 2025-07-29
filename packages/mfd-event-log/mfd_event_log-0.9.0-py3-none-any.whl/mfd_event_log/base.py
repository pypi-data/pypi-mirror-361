# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Event Log module."""

import logging
from typing import List, Optional, Dict, TYPE_CHECKING

from mfd_common_libs import add_logging_level, log_levels, os_supported
from mfd_connect.util.powershell_utils import parse_powershell_list
from mfd_typing import OSName

from .data_structures import EventType
from .exceptions import EventLogExecutionError

if TYPE_CHECKING:
    from mfd_connect import RPyCConnection

logger = logging.getLogger(__name__)
add_logging_level("MODULE_DEBUG", log_levels.MODULE_DEBUG)


class EventLog:
    """Class to handle EventLog in Windows."""

    @os_supported(OSName.WINDOWS)
    def __init__(self, *, connection: "RPyCConnection") -> None:
        """
        Initialize connection.

        :param connection: mfd_connect object for remote connection handling
        """
        self._connection = connection

    def get_event_log(
        self, logger_name: str = "System", source: str = "", event_type: EventType = EventType.ALL, event_id: str = ""
    ) -> List[Optional[Dict[str, str]]]:
        """Get Windows Event Log.

        :param source: Source from which logs to be fetched
        :param event_type: Type of event logs to be fetched.
        :param logger_name: Specify the System, Security or any other Event log
        :param event_id: Specific Event ID to be fetched
        :return: Eventlog in key-value pairs as per user input.
        """
        cmd = f"get-eventlog -LogName {logger_name}"
        if source:
            cmd += f" -Source {source}"
        if event_type is not EventType.ALL:
            cmd += f" -EntryType {event_type.value}"
        if event_id:
            cmd += f"|where {{$_.eventID -eq {event_id}}}"

        cmd += " -EA silentlyContinue|Format-List"

        logger.log(level=log_levels.MODULE_DEBUG, msg=f"Get Event Log command: {cmd}")
        output = self._connection.execute_powershell(cmd, custom_exception=EventLogExecutionError).stdout

        return parse_powershell_list(output)

    def clear_event_log(self) -> None:
        """Clear Windows Event Log."""
        logger.log(level=log_levels.MODULE_DEBUG, msg="Clear Event Viewer Logs: Windows Logs->System)")
        self._connection.execute_powershell(
            "Get-EventLog -LogName * | ForEach { Clear-EventLog $_.Log }", custom_exception=EventLogExecutionError
        )

    def get_and_verify_event_log(
        self, failure_entry_types: List[str] = None, ignored_event_ids: List[str] = None
    ) -> bool:
        """Get Windows Event Log and check if it contains any unwanted entries.

        :param failure_entry_types: Entry types that will be checked during verification
        :param ignored_event_ids: List of Event IDs to be be ignored while verifying event log
        :return: result of event log verification
        """
        if failure_entry_types is None:
            failure_entry_types = ["Error"]
        if ignored_event_ids is None:
            ignored_event_ids = []

        logs = self.get_event_log(logger_name="System", source="", event_type=EventType.ALL)
        failures = [entry for entry in logs if entry["EntryType"] in failure_entry_types]
        return self.verify_event_log(event_log_entries=failures, ignored_event_ids=ignored_event_ids)

    def verify_event_log(self, event_log_entries: List[Dict[str, str]], ignored_event_ids: List[str] = None) -> bool:
        """Verify Event Log entries.

        :param event_log_entries: List of Event Log entries
        :param ignored_event_ids: List of Event IDs to be be ignored while verifying event log
        :return: result of event log verification
        """
        if ignored_event_ids is None:
            ignored_event_ids = []

        filtered_logs = [entry for entry in event_log_entries if entry["InstanceId"] not in ignored_event_ids]
        if filtered_logs:
            logger.log(
                level=log_levels.MODULE_DEBUG,
                msg=f"Events after filtering ignored events {ignored_event_ids}:",
            )
            for entry in filtered_logs:
                logger.log(
                    level=log_levels.MODULE_DEBUG,
                    msg=f"({entry['EntryType']}, {entry['Source']}) {entry['InstanceId']}: {entry['Message']}",
                )
            return False
        else:
            logger.log(level=log_levels.MODULE_DEBUG, msg="No unwanted events in Event Log")
            return True

    def verify_log(self, driver: str) -> str:
        """
        Check the system log for errors.

        :param driver: driver name
        :return: empty string if no errors found, error content otherwise
        """
        from mfd_event_log.data_structures import EventType

        logger.log(level=log_levels.MODULE_DEBUG, msg=f"Driver service name: {driver}")
        output = ""
        errors = self.get_event_log(source=driver, event_type=EventType.ERROR)
        if errors is not None:
            for error in errors:
                output += error["Message"]
                output += "\n"
            logger.log(level=log_levels.MODULE_DEBUG, msg=f"Error(s) found in event log.\n{output}")
        return output
