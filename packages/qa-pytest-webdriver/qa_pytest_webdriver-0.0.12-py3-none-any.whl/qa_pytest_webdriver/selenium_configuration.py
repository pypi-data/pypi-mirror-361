# SPDX-FileCopyrightText: 2025 Adrian Herscu
#
# SPDX-License-Identifier: Apache-2.0

from functools import cached_property
from typing import final

from qa_pytest_commons.base_configuration import BaseConfiguration
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumConfiguration(BaseConfiguration):
    """
    SeleniumConfiguration extends BaseConfiguration to provide Selenium-specific configuration options.

    This class exposes properties for retrieving the UI URL and initializing the Selenium WebDriver Service,
    leveraging configuration values and dynamic driver management.
    """

    @cached_property
    @final
    def landing_page(self) -> str:
        """
        Returns the UI URL from the configuration parser.

        Returns:
            str: The URL string specified under the "selenium/base" in the configuration.

        Raises:
            KeyError: If the "selenium" section or "base" key is not present in the configuration parser.
        """
        return self.parser["selenium"]["landing_page"]

    # FIXME Service here is imported from selenium.webdriver.chrome.service
    # which makes this method specific to ChromeDriver.
    @cached_property
    @final
    def service(self) -> Service:
        """
        Creates and returns a Selenium WebDriver Service instance using the ChromeDriverManager.

        Returns:
            Service: An instance of Selenium's Service class, initialized with the path to the ChromeDriver executable
            installed by ChromeDriverManager.

        Note:
            This method currently supports only ChromeDriver, but may be extended to support different services
            based on configuration in the future.
        """
        # NOTE may add support for providing different services per configuration
        return Service(ChromeDriverManager().install())
