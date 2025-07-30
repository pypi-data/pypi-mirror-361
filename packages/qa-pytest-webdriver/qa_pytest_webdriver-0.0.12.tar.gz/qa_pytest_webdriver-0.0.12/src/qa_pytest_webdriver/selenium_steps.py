# SPDX-FileCopyrightText: 2025 Adrian Herscu
#
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from typing import (
    Callable,
    Iterator,
    List,
    Optional,
    Protocol,
    Self,
    Tuple,
    Union,
    final,
    overload,
)

from hamcrest.core.matcher import Matcher
from qa_pytest_commons.generic_steps import GenericSteps
from qa_pytest_webdriver.selenium_configuration import SeleniumConfiguration
from qa_testing_utils.logger import Context
from selenium.webdriver.common.by import By as _By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


class SearchContext(Protocol):
    """
    Protocol for Selenium search contexts (e.g., WebDriver, WebElement).

    Provides methods to find single or multiple elements using Selenium's locator strategy.
    """

    def find_element(self, by: str, value: Optional[str]) -> WebElement: ...

    def find_elements(
        self, by: str, value: Optional[str]) -> List[WebElement]: ...


@dataclass(frozen=True)
class Locator:
    """
    Represents a Selenium locator as a (by, value) pair.

    Attributes:
        by (str): The Selenium locator strategy (e.g., By.ID, By.XPATH).
        value (str): The locator value.
    """
    by: str
    value: str

    def as_tuple(self) -> Tuple[str, str]:
        """
        Returns the locator as a tuple (by, value), suitable for Selenium APIs.

        Returns:
            Tuple[str, str]: The locator as a tuple.
        """
        return (self.by, self.value)


class By:
    """
    Factory for Selenium locators, matching Selenium's By API.

    Provides static methods to create Locator objects for each Selenium locator strategy.
    """

    @staticmethod
    def id(value: str) -> Locator:
        """
        Creates a locator for elements with the given id attribute.

        Args:
            value (str): The id value.
        Returns:
            Locator: The locator object.
        """
        return Locator(_By.ID, value)

    @staticmethod
    def xpath(value: str) -> Locator:
        """
        Creates a locator for elements matching the given XPath expression.

        Args:
            value (str): The XPath expression.
        Returns:
            Locator: The locator object.
        """
        return Locator(_By.XPATH, value)

    @staticmethod
    def link_text(value: str) -> Locator:
        """
        Creates a locator for elements with the given link text.

        Args:
            value (str): The link text.
        Returns:
            Locator: The locator object.
        """
        return Locator(_By.LINK_TEXT, value)

    @staticmethod
    def partial_link_text(value: str) -> Locator:
        """
        Creates a locator for elements with the given partial link text.

        Args:
            value (str): The partial link text.
        Returns:
            Locator: The locator object.
        """
        return Locator(_By.PARTIAL_LINK_TEXT, value)

    @staticmethod
    def name(value: str) -> Locator:
        """
        Creates a locator for elements with the given name attribute.

        Args:
            value (str): The name value.
        Returns:
            Locator: The locator object.
        """
        return Locator(_By.NAME, value)

    @staticmethod
    def tag_name(value: str) -> Locator:
        """
        Creates a locator for elements with the given tag name.

        Args:
            value (str): The tag name.
        Returns:
            Locator: The locator object.
        """
        return Locator(_By.TAG_NAME, value)

    @staticmethod
    def class_name(value: str) -> Locator:
        """
        Creates a locator for elements with the given class name.

        Args:
            value (str): The class name.
        Returns:
            Locator: The locator object.
        """
        return Locator(_By.CLASS_NAME, value)

    @staticmethod
    def css_selector(value: str) -> Locator:
        """
        Creates a locator for elements matching the given CSS selector.

        Args:
            value (str): The CSS selector.
        Returns:
            Locator: The locator object.
        """
        return Locator(_By.CSS_SELECTOR, value)


type ElementSupplier = Callable[[], WebElement]
type LocatorOrSupplier = Union[Locator, ElementSupplier]


class SeleniumSteps[TConfiguration: SeleniumConfiguration](
    GenericSteps[TConfiguration]
):
    """
    BDD-style step definitions for Selenium-based UI operations.

    Type Parameters:
        TConfiguration: The configuration type, must be a SeleniumConfiguration.

    Attributes:
        _web_driver (WebDriver): The Selenium WebDriver instance used for browser automation.
    """
    _web_driver: WebDriver

    @final
    @Context.traced
    def clicking_once(self, element_supplier: ElementSupplier) -> Self:
        """
        Clicks the element supplied by the given callable.

        Args:
            element_supplier (ElementSupplier): Callable returning a WebElement.
        Returns:
            Self: The current step instance for chaining.
        """
        element_supplier().click()
        return self

    @overload
    def clicking(self, element: Locator) -> Self: ...

    @overload
    def clicking(self, element: ElementSupplier) -> Self: ...

    @final
    def clicking(self, element: LocatorOrSupplier) -> Self:
        """
        Clicks the element specified by a locator or supplier, with retry logic.

        Args:
            element (LocatorOrSupplier): Locator or callable returning a WebElement.
        Returns:
            Self: The current step instance for chaining.
        """
        return self.retrying(lambda: self.clicking_once(self._resolve(element)))

    @final
    @Context.traced
    def typing_once(self, element_supplier: ElementSupplier, text: str) -> Self:
        """
        Types the given text into the element supplied by the callable.

        Args:
            element_supplier (ElementSupplier): Callable returning a WebElement.
            text (str): The text to type.
        Returns:
            Self: The current step instance for chaining.
        """
        element = element_supplier()
        element.clear()
        element.send_keys(text)
        return self

    @overload
    def typing(self, element: Locator, text: str) -> Self: ...

    @overload
    def typing(self, element: ElementSupplier, text: str) -> Self: ...

    @final
    def typing(self, element: LocatorOrSupplier, text: str) -> Self:
        """
        Types the given text into the element specified by a locator or supplier, with retry logic.

        Args:
            element (LocatorOrSupplier): Locator or callable returning a WebElement.
            text (str): The text to type.
        Returns:
            Self: The current step instance for chaining.
        """
        return self.retrying(lambda: self.typing_once(self._resolve(element), text))

    @final
    def the_element(self, locator: Locator, by_rule: Matcher[WebElement], context: Optional[SearchContext] = None) -> Self:
        """
        Asserts that the element found by the locator matches the given matcher.

        Args:
            locator (Locator): The locator to find the element.
            by_rule (Matcher[WebElement]): Matcher for the element.
            context (Optional[SearchContext]): Optional search context.
        Returns:
            Self: The current step instance for chaining.
        """
        return self.eventually_assert_that(lambda: self._element(locator, context), by_rule)

    @final
    def the_elements(self, locator: Locator, by_rule: Matcher[Iterator[WebElement]], context: Optional[SearchContext] = None) -> Self:
        """
        Asserts that the elements found by the locator match the given matcher.

        Args:
            locator (Locator): The locator to find the elements.
            by_rule (Matcher[Iterator[WebElement]]): Matcher for the elements iterator.
            context (Optional[SearchContext]): Optional search context.
        Returns:
            Self: The current step instance for chaining.
        """
        return self.eventually_assert_that(lambda: self._elements(locator, context), by_rule)

    @final
    @Context.traced
    def _elements(
        self, locator: Locator, context: Optional[SearchContext] = None
    ) -> Iterator[WebElement]:
        return iter((context or self._web_driver).find_elements(*locator.as_tuple()))

    @final
    @Context.traced
    def _element(
        self, locator: Locator, context: Optional[SearchContext] = None
    ) -> WebElement:
        return self._scroll_into_view(
            (context or self._web_driver).find_element(*locator.as_tuple())
        )

    def _scroll_into_view(self, element: WebElement) -> WebElement:
        self._web_driver.execute_script(  # type: ignore
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        return element

    @final
    def _resolve(self, element: LocatorOrSupplier) -> ElementSupplier:
        if isinstance(element, Locator):
            return lambda: self._element(element)
        return element
