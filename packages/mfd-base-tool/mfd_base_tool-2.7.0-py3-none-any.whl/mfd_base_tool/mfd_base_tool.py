# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Main module."""

import logging
import typing
from abc import ABC, abstractmethod
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Optional, Union, Dict
from mfd_typing import OSType
from mfd_common_libs import add_logging_level, log_levels

if typing.TYPE_CHECKING:
    from mfd_connect import Connection

logger = logging.getLogger(__name__)
add_logging_level("MODULE_DEBUG", log_levels.MODULE_DEBUG)


class ToolTemplate(ABC):
    """
    Class for abstraction for Tool.

    eg.
    >>>class MyTool(ToolTemplate):
    ...
    ...tool_executable_name = {OSType.WINDOWS : "samplew64e.exe", OSType.POSIX : "sample64e"}
    or
    >>>tool_executable_name = "sample64e"
    ...    def __init__(self, *args, **kwargs):
    ...        super().__init__(*args, **kwargs)
    ...
    ...    def _get_tool_exec_factory(self) -> str:
    ...        return self.tool_executable_name
    ...
    ...    def check_if_available(self) -> None:
    ...        if not "if statement for check":
    ...            raise MyToolNotAvailable()
    ...
    ...    def get_version(self) -> str:
    ...        return "my read tool version"
    ...
    ...    def my_tool_method(self):
    ...        pass
    """

    tool_executable_name: Union[str, Dict] = None

    def __init__(
        self, *, connection: "Connection", absolute_path_to_binary_dir: Optional[Union[Path, str]] = None
    ) -> None:
        """
        Initialize tool.

        :param connection: Connection object
        :param absolute_path_to_binary_dir: path to dir where binary of tool is stored
                                            if None tool should be added to $PATH
        """
        assert self.tool_executable_name is not None, "tool_executable_name must be defined."
        self._connection = connection
        self._tool_exec = self._get_tool_exec(absolute_path_to_binary_dir)
        self.check_if_available()

        logger.log(
            level=log_levels.MODULE_DEBUG,
            msg=f"{self.__class__.__name__} tool class uses {self._tool_exec}. Tool version: {self.get_version()}.",
        )

    @abstractmethod
    def _get_tool_exec_factory(self) -> str:
        """
        Get correct tool name.

        Eg. depended by OSType via tool_executable_name
        >>> return self.tool_executable_name
        or
        >>> return self.tool_executable_name[self._connection.get_os_type()]

        :return: Tool exec name
        """
        raise NotImplementedError

    def _get_tool_exec(self, absolute_path_to_binary_dir: Optional[Union[Path, str]]) -> str:
        """
        Create path to tool.

        :param absolute_path_to_binary_dir: Path to binary directory
        :return: Tool executable name
        """

        def _stringify_path_with_executable() -> str:
            try:
                os_type = self._connection.get_os_type()
            except NotImplementedError as e:
                raise TypeError("Type of connection not supported.") from e

            if os_type == OSType.POSIX:
                return str(PurePosixPath(absolute_path_to_binary_dir) / executable_name)
            else:
                return str(PureWindowsPath(absolute_path_to_binary_dir) / executable_name)

        executable_name = self._get_tool_exec_factory()
        if absolute_path_to_binary_dir:
            return _stringify_path_with_executable()
        else:
            return executable_name

    @abstractmethod
    def check_if_available(self) -> None:
        """
        Check if tool is available in system.

        eg.
        >>> _ = self._connection.execute_command(f"{self._tool_exec} /help", custom_exception = ToolNotAvailable)
        :raises ToolNotAvailable when tool not available.
        """
        raise NotImplementedError

    @abstractmethod
    def get_version(self) -> str:
        """
        Get version of tool.

        eg.
        >>> return self._connection.execute_command(f"{self._tool_exec} /version").stdout

        :return: Version of tool
        """
        raise NotImplementedError
