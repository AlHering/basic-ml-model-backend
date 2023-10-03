# -*- coding: utf-8 -*-
"""
****************************************************
*                  EntityProtocol                  *
*            (c) 2022 Alexander Hering             *
****************************************************
"""


class PluginImportException(Exception):
    """
    PluginImportException class.
    """

    def __init__(self, plugin: str, plugin_type: str,  message: str = "exception occurred while importing plugin ") -> None:
        """
        Initiation method for Plugin Import Exception.
        :param plugin: Plugin name, that caused exception
        :param plugin_type: Plugin type.
        :param message: Message to include in exception.
        """
        self.plugin = plugin
        self.plugin_type = plugin_type
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        """
        Method for encoding exception as string.
        :return: Exception string.
        """
        return f"{self.message} : {self.plugin} as {self.plugin_type}"


class JobHandlerException(Exception):
    """
    JobHandlerException class.
    """

    def __init__(self, handler: str, job_id: int,  message: str = "exception occurred while setting up Job Handler ") -> None:
        """
        Initiation method for Job Handler Exception.
        :param handler: Job Handler name.
        :param job_id: Job ID.
        :param message: Message to include in exception.
        """
        self.handler = handler
        self.job_id = job_id
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        """
        Method for encoding exception as string.
        :return: Exception string.
        """
        return f"{self.message} : {self.handler} with {str(self.job_id)}"


class WrongFilterMaskStructureException(Exception):
    """
    WrongFilterMaskStructureException class
    """

    def __init__(self, mask: list,  message: str = "exception occurred while checking filter masks ") -> None:
        """
        Initiation method for Wrong Filter Mask Structure Exception.
        :param mask: Filter mask, that caused exception.
        :param message: Message to include in exception.
        """
        self.mask = mask
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        """
        Method for encoding exception as string.
        :return: Exception string.
        """
        return f"{self.message} : {str(self.mask)}"


class NotSupportedByFrameworkException(Exception):
    """
    NotSupportedByFrameworkException class.
    """

    def __init__(self, framework: str, task: str,  message: str = "exception occurred while running general scraper ") -> None:
        """
        Initiation method for Not Supported By Framework Exception.
        :param framework: Framework, that caused the exception.
        :param task: Task, that caused the exception.
        :param message: Message to include in exception.
        """
        self.framework = framework
        self.task = task
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        """
        Method for encoding exception as string.
        :return: Exception string.
        """
        return f"{self.message} : {self.framework} -> {self.task}"


class InvalidCFAConfigurationException(Exception):
    """
    InvalidCFAConfigurationException class.
    """

    def __init__(self, config: dict, message: str = "exception occurred in configuration ") -> None:
        """
        Initiation method for Invalid CFA Configuration Exception.
        :param config: Full config which caused the exception.
        :param message: Message to include in exception.
        """
        self.config = config
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        """
        Method for encoding exception as string.
        :return: Exception string.
        """
        return f"{self.message} : {self.config}"
