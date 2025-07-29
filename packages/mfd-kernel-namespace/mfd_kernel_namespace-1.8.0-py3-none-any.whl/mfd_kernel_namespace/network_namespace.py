# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Main module."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def add_namespace_call_command(command: str, namespace: Optional[str]) -> str:
    """
    Add namespace call command to passed command if required.

    :param command: Command to extend
    :param namespace: Namespace name
    :return: Extended command
    """
    if namespace is not None:
        command = f"sh -c '{command}'" if "echo" in command else command
        command = f"ip netns exec {namespace} {command}"
    return command
