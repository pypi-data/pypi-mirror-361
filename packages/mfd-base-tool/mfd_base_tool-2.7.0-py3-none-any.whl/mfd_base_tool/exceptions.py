# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for exceptions."""

import subprocess


class ToolException(subprocess.CalledProcessError):
    """Handle tool exceptions."""


class ToolNotAvailable(ToolException):
    """Handle tool not available exception."""
