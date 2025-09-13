# -*- coding: utf-8 -*-
import os
import traceback
from time import sleep
from time import time
from typing import Optional, List, Union, Any, Tuple

from selenium import common
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from . import file_system_utility, environment_utility


def setup_selenium_window(driver: WebDriver) -> None:
    """
    Function for setting size of selenium driver window to 2/3 of width.
    :param driver: Webdriver.
    """
    driver.fullscreen_window()
    size_dict = driver.get_window_size(driver.current_window_handle)
    driver.set_window_size(size_dict["width"] / 1.33, size_dict["height"])
    driver.set_window_position(size_dict["width"] / 1.33, 0)


def close_new_window(driver: WebDriver, main_handle: Union[int, List[Union[int, str]]]) -> None:
    """
    Function for closing a new window, e.g. a popup window.
    :param driver: Webdriver.
    :param main_handle: Main window handle.
    """
    new_handle = None
    for handle in driver.window_handles:
        if handle != main_handle:
            new_handle = handle
            break
    if new_handle:
        driver.switch_to.window(new_handle)
        driver.close()
        driver.switch_to(main_handle)


def close_new_windows(driver: WebDriver, keep: str) -> None:
    """
    Function for closing new windows, e.g. a popup windows.
    :param driver: Webdriver.
    :param keep: Substring of url to keep.
    """
    if len(driver.window_handles) > 1:
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            if keep not in driver.current_url:
                driver.close()
    driver.switch_to.window(driver.window_handles[0])


def get_chrome_driver(**kwargs) -> WebDriver:
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver


def get_firefox_driver(**kwargs) -> WebDriver:
    """
    Function for getting firefox driver.
    :param kwargs: Keyword arguments
        'useragent': Sets webdriver instance useragent to given string.
        'proxy': Proxy IP or 'torsocks'.
        'addons': List of paths to addons.
        'headless': Headless mode setting as bool.
        'hide_bot_status': Flag, declaring whether to hide bot status.
        'binary': Path to binaries.
        'profile': Path to profile folder.
        'driver': Path to driver.
    :return: Webdriver instance.
    """
    imported_profile = webdriver.FirefoxProfile(kwargs["profile"])
    imported_profile.set_preference("app.update.auto", False)
    if kwargs.get("hide_bot_status"):
        imported_profile.set_preference("dom.webdriver.enabled", False)
        imported_profile.set_preference("useAutomationExtension", False)

    additional_settings = setup_anonymized_connection(
        kwargs.get("useragent", ""), kwargs.get("proxy", ""))
    options = set_driver_configuration(
        imported_profile, additional_settings, **kwargs)

    if kwargs.get("binary"):
        options.binary_location = kwargs["binary"]
    service = Service(executable_path=kwargs["driver"])
    driver = webdriver.Firefox(
        options=options, service=service)

    return driver


def safely_open_url(driver: WebDriver, url: str) -> None:
    """
    Function for safely opening url.
    :param driver: Selenium web driver.
    :param url: URL to open in driver.
    """
    if os.popen("echo $no_proxy").read() == "localhost,127.0.0.0/8,::1\n":
        print("changing no_proxy")
        os.system('export no_proxy="localhost,127.0.0.1"')
    driver.get(url)
    sleep(1)
    close_new_windows(driver, url)


def check_tor_connection(driver: WebDriver) -> bool:
    """
    Function for checking TOR connection.
    :return: True, if driver is connected via TOR, else False.
    """
    driver.get("https://check.torproject.org/")
    sleep(3)
    if safely_get_element(driver, "//body/div[@class='content']/h1[@class='on']"):
        return True
    else:
        return False


def setup_anonymized_connection(useragent: str = "", proxy: str = "", additional_settings: List[Tuple[str, Any]] = []) -> List[Tuple[str, str]]:
    """
    Function for setting up anonymized connections.
    :param useragent: Useragent string to use. Defaults to empty string in which case real useragent is taken.
    :param proxy: Proxy IP or 'torsocks' to use. Defaults to empty string in which case no proxy is used.
    :param additional_settings: List of additional settings. Defaults to empty list.
    :return: Updated list of additional settings.
    """
    # additional_settings.append(("browser.link.open_newwindow", 3))
    if useragent:
        additional_settings.append(("general.useragent.override", useragent))
    if proxy:
        if proxy == "torsocks":
            additional_settings.extend([("network.proxy.type", 1), ("network.proxy.socks_remote_dns", True),
                                        ("network.proxy.socks_port", 9050),
                                        ("network.proxy.socks", "127.0.0.1")])
        else:
            webdriver.DesiredCapabilities.FIREFOX["proxy"] = {
                'proxyType': "MANUAL",
                'httpProxy': proxy,
                'ftpProxy': proxy,
                'sslProxy': proxy
            }
    return additional_settings


def set_driver_configuration(imported_profile: webdriver.FirefoxProfile, additional_settings: List[Tuple[str, str]],
                             **kwargs: Optional[Any]) -> Options:
    """
    Function for setting driver configuration.
    :param imported_profile: Firefox profile.
    :param additional_settings: List of additional settings.
    :param kwargs: Arbitrary keyword arguments, e.g.
        'profile': Path to firefox profile to use.
        'headless': Starts browser in headless mode.
    :return: Options
    """
    options = Options()
    options.profile = imported_profile
    options.headless = kwargs.get("headless", False)
    for setting in additional_settings:
        imported_profile.set_preference(setting[0], setting[1])
        options.profile.set_preference(setting[0], setting[1])
    return options


def get_driver(browser: str, **kwargs: Optional[Any]) -> Optional[WebDriver]:
    """
    Function for creating a webdriver instance.
    :param browser: Browser to use, e.g. 'firefox', 'chrome', 'edge', ...
    :param kwargs: Keyword arguments
        'useragent': Sets webdriver instance useragent to given string.
        'proxy': Proxy IP or 'torsocks'.
        'addons': List of paths to addons.
        'headless': Headless mode setting as bool.
        'hide_bot_status': Flag, declaring whether to hide bot status.
        'binary': Path to binaries.
        'profile': Path to profile folder.
        'driver': Path to driver.
    :return: Webdriver instance.
    """
    driver = {"firefox": get_firefox_driver}[browser](**kwargs)

    if "addons" in kwargs:
        for addon in kwargs["addons"]:
            driver.install_addon(addon)

    if kwargs.get("proxy", "") == "torsocks" and not check_tor_connection(driver):
        return None

    driver.get("https://www.startpage.com/")
    close_new_windows(driver, "www.startpage.com")

    return driver


def get_anonymous_firefox_driver(binary: str, profile: str, driver: str, **kwargs) -> WebDriver:
    """
    Function for getting anonymous driver.
    :param binary: Path to binaries.
    :param profile: Path to profile folder.
    :param driver: Path to driver.
    :param kwargs: Keyword arguments
        'useragent': Sets webdriver instance useragent to given string.
        'proxy': Proxy IP or 'torsocks'.
        'addons': List of paths to addons.
        'headless': Headless mode setting as bool.
        'hide_bot_status': Flag, declaring whether to hide bot status.
    :return: Anonymous Webdriver.
    """
    return get_driver(browser="firefox", binary=binary, profile=profile, driver=driver, proxy="torsocks", hide_bot_status=True)


def wait_for_cloudflare(driver: WebDriver) -> None:
    """
    Function for waiting for cloudflare protection to finish probing.
    :param driver: Webdriver or selection element.
    """
    try:
        while (driver.find_element(By.XPATH, "//div[@id='cf-content']/h1/span")).get_attribute(
                "data-translate") == "checking_browser":
            print("browser check detected...")
            sleep(10)
    except common.exceptions.NoSuchElementException:
        print("no browser check detected...")


def wait_for_element(driver: Union[WebDriver, WebElement], xpath: str, time: float) -> bool:
    """
    Function for waiting until element is present.
    :param driver: Webdriver or selection element.
    :param xpath: XPath to element.
    :param time: Maximum waiting time in seconds.
    :return True, if element exists, else False after timeout.
    """
    try:
        WebDriverWait(driver, time).until(
            ec.presence_of_element_located((By.XPATH, xpath)))
        return True
    except common.exceptions.TimeoutException:
        return False


def switch_to_iframe(driver: Union[WebDriver, WebElement], iframe_path: str) -> List[int]:
    """
    Function for switching to iframe.
    :param driver: Webdriver or selection element.
    :param iframe_path: XPath for target iframe.
    :return Coordinates of iframe relative to driver.
    """
    iframes = [iframe for iframe in driver.find_elements(By.XPATH, iframe_path) if
               iframe.location["x"] > 0 and iframe.location["y"] > 0]
    iframe_location = get_coordinates_of_element(driver, iframes[0], "root")
    driver.switch_to.frame(iframes[0])
    sleep(0.1)
    return iframe_location


def wait_for_captcha(driver: WebDriver, captcha_profile: dict) -> None:
    """
    Function for waiting for captcha to be solved.
    :param driver: Webdriver.
    :param captcha_profile: Captcha profile.
    """
    sleep(2)
    if "iframe" in captcha_profile:
        if isinstance(captcha_profile["iframe"], list):
            for iframe in captcha_profile["iframe"]:
                switch_to_iframe(driver, iframe)
        else:
            switch_to_iframe(driver, captcha_profile["iframe"])
    captcha_solved = False
    while not captcha_solved:
        # check for active captcha element
        try:
            if driver.find_element(By.XPATH, captcha_profile["active"]):
                print("Active Captcha found...")
                captcha_solved = False
                sleep(captcha_profile["delay"])
        except common.exceptions.NoSuchElementException:
            if captcha_profile["reload_when_wrong"]:
                # if not found, check if captcha answer was wrong
                try:
                    if driver.find_element(By.XPATH, captcha_profile["wrong"]):
                        captcha_solved = False
                        print("wrong answer - try again")
                        driver.get(driver.current_url)
                        sleep(captcha_profile["delay"])
                        sleep(captcha_profile["delay"])
                        wait_for_captcha(driver, captcha_profile)
                except common.exceptions.NoSuchElementException:
                    # captcha was not answered wrongly
                    pass
            # check if captcha was just in reloading state
            sleep(0.2)
            try:
                driver.find_element(By.XPATH, captcha_profile["active"])
                captcha_solved = False
            except common.exceptions.NoSuchElementException:
                # no captcha in whatsoever state found
                print("Captcha solved...")
                captcha_solved = True
                if "iframe" in captcha_profile:
                    driver.switch_to.default_content()
        except common.exceptions.WebDriverException:
            # no captcha in whatsoever state found
            print("Captcha solved...")
            captcha_solved = True
            if "iframe" in captcha_profile:
                driver.switch_to.default_content()


def handle_barrier(driver: WebDriver, barrier_profile: dict) -> None:
    """
    Function for handling barrier.
    :param driver: Webdriver.
    :param barrier_profile: Captcha profile.
    """
    sleep(barrier_profile["delay"])
    if "iframe" in barrier_profile:
        if isinstance(barrier_profile["iframe"], list):
            for iframe in barrier_profile["iframe"]:
                switch_to_iframe(driver, iframe)
        else:
            switch_to_iframe(driver, barrier_profile["iframe"])
    captcha_solved = False
    while not captcha_solved:
        # check for active captcha element
        if get_targets_by_declaration(driver, barrier_profile["active"]):
            sleep(barrier_profile["delay"])

            solve_barrier(driver, barrier_profile)

            if get_targets_by_declaration(driver, barrier_profile["fail"]):
                captcha_solved = False
            else:
                # no captcha in whatsoever state found
                captcha_solved = True
                if "iframe" in barrier_profile["iframe"]:
                    driver.switch_to.default_content()
        else:
            captcha_solved = True
            if "iframe" in barrier_profile["iframe"]:
                driver.switch_to.default_content()


def solve_barrier(driver: WebDriver, barrier_profile: dict) -> None:
    """
    Function for solving barrier.
    :param driver: Webdriver.
    :param barrier_profile: Captcha profile.
    """
    if barrier_profile["solve"] == "wait":
        sleep(barrier_profile["solution"])
    elif barrier_profile["solve"] == "click":
        get_targets_by_declaration(driver, barrier_profile["solution"]).click()
    elif barrier_profile["solve"] == "call":
        environment_utility.get_function_from_path(
            barrier_profile["solution"])(driver)


def wait_for_removal(driver: Union[WebDriver, WebElement], xpath: str) -> None:
    """
    Function for waiting for single element to be removed.
    :param driver: Webdriver or selection element.
    :param xpath: XPath to element.
    """
    try:
        driver.find_element(By.XPATH, xpath)
        driver.refresh()
        sleep(2)
        wait_for_removal(driver, xpath)
    except common.exceptions.NoSuchElementException:
        print("blocking element not found ...")


def collect(driver: Union[WebDriver, WebElement], data: dict) -> dict:
    """
    Function for collecting data by xpath into dictionary.
    :param driver: Webdriver or selection element.
    :param data: Data collection dictionary.
    :return: In dict collected data.
    """
    return_data = {}
    for elem in data:
        if isinstance(data[elem], dict):
            if "#meta_xpath" in data[elem] and "#meta_lambda" in data[elem]:
                web_element = driver.find_element(
                    By.XPATH, data[elem]["#meta_xpath"])
                lambda_function = eval(data[elem]["#meta_lambda"])
                return_data[elem] = lambda_function(web_element)
            else:
                return_data[elem] = collect(driver, data[elem])
        else:
            if isinstance(data[elem], list):
                module = file_system_utility.get_module(
                    data[elem][1].split(":")[0])
                web_element = driver.find_element(By.XPATH, data[elem][0])
                return_data[elem] = eval(
                    "module." + data[elem][1].split(":")[1] + "(web_element)")
            else:
                if data[elem].startswith("eval("):
                    return_data[elem] = eval(data[elem].replace('eval(', '')[:-1],
                                             {"driver": driver, "data": data, "elem": elem})
                if "@" == data[elem].split("/")[-1][0]:
                    attribute = data[elem].split("/")[-1][1:]
                    return_data[elem] = safely_get_attribute(driver, data[elem].replace(
                        "/@" + attribute, ""), data[elem].split("/")[-1][1:])
                else:
                    return_data[elem] = driver.find_element(
                        By.XPATH, data[elem]).text
    return return_data


def safely_collect(driver: Union[WebDriver, WebElement], data: dict) -> dict:
    """
    Function for safely collecting data by xpath into dictionary, meaning not found elements get skipped. In later cases
    the collected value will be None. Does not support dynamic cleaning method calls! Use collect function if necessary.
    :param driver: Web driver or selection element.
    :param data: Data collection dictionary.
    :return: In dict collected data.
    """
    return_data = {}
    for elem in data:
        if isinstance(data[elem], dict):
            return_data[elem] = safely_collect(driver, data[elem])
        elif isinstance(data[elem], str):
            return_data[elem] = safely_get_elements(driver, data[elem])
        else:
            return_data[elem] = get_targets_by_declaration(driver, data[elem])
    return return_data


def safely_get_elements(driver: Union[WebDriver, WebElement], xpath: str) -> List[Any]:
    """
    Function for safely searching for elements in a Selenium WebElement.
    :param driver: Webdriver or selection element.
    :param xpath: XPath of the elements to find.
    :return: List of elements if found, else empty list.
    """
    try:
        elements = driver.find_elements(By.XPATH, xpath)
        return elements
    except common.exceptions.NoSuchElementException:
        return []


def safely_get_element(driver: Union[WebDriver, WebElement], xpath: str) -> Optional[WebElement]:
    """
    Function for safely searching for element in a Selenium WebElement.
    :param driver: Webdriver or selection element.
    :param xpath: XPath of the element to find.
    :return: First element if found, else None.
    """
    try:
        element = driver.find_element(By.XPATH, xpath)
        return element
    except common.exceptions.NoSuchElementException:
        return None


def safely_get_text_content(driver: Union[WebDriver, WebElement], xpath: str) -> str:
    """
    Function for safely getting text content of a Selenium WebElement defined through given xpath.
    :param driver: Webdriver or selection element.
    :param xpath: XPath of the target element.
    :return: Content text, if found, else empty string.
    """
    web_element = safely_get_element(driver, xpath)
    if web_element and hasattr(web_element, "text"):
        return web_element.text
    else:
        return ""


def safely_get_attribute(driver: Union[WebDriver, WebElement], xpath: str, attribute: str) -> str:
    """
    Function for safely getting attribute content of a given Selenium WebElement.
    :param driver: Webdriver or selection element.
    :param xpath: XPath of the target element.
    :param attribute: Attribute name to search for.
    :return: Attribute content, if found, else empty string.
    """
    if attribute[0] == "@":
        attribute = attribute[1:]
    web_element = safely_get_element(driver, xpath)
    if web_element:
        try:
            attribute_value = web_element.get_attribute(attribute)
            return "" if attribute_value is None else attribute_value
        except common.exceptions.NoSuchAttributeException as ex:
            print(ex)
            traceback.print_exc()
            return ""
    else:
        return ""


def get_standard_root_height(driver: WebDriver) -> int:
    """
    Function for getting standard root window height offset.
    :param driver: Webdriver.
    :return: Standard root window height offset.
    """
    driver.maximize_window()
    return driver.execute_script('return window.outerHeight - window.innerHeight;') + 17


def get_coordinates_of_element(driver: WebDriver, target_element: WebElement, target_point: str = "center", root_width: int = 0, root_height: int = -1) -> List[int]:
    """
    Function for getting center coordinates of a target element.
    Extended with @https://stackoverflow.com/a/56693949.
    :param driver: Webdriver.
    :param target_element: Target element.
    :param target_point: 'center' for center point (default), 'root' for root point.
    :param root_width: Root width to be added to local width, defaults to 0.
    :param root_height: Root height to be added to local height, defaults to global window root height.
    :return: Coordinates of target element center.
    """
    if root_height == -1:
        root_height = get_standard_root_height(driver)
    if target_point == "center":
        return [target_element.location["x"] + target_element.size["width"]//2 + root_width, target_element.location["y"] + target_element.size["height"]//2 + root_height]
    elif target_point == "root":
        return [target_element.location["x"] + root_width, target_element.location["y"] + root_height]


def wait_for_downloads_to_finish(driver: WebDriver, max_time: float = None) -> True:
    """
    Function for waiting for downloads to finish.
    :param driver: Selenium Webdriver.
    :param max_time: Maximal time to wait in seconds.
    :return: True, if downloads finished successfully, False if time runs out.
    """
    ActionChains(driver).key_down(Keys.COMMAND).send_keys(
        "t").key_up(Keys.COMMAND).perform()
    driver.get("about:downloads")
    start_time = time()
    sleep(1)
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    ActionChains(driver).send_keys(Keys.HOME).perform()
    while safely_get_elements(driver, "//richlistbox[@id='downloadsRichListBox']/richlistitem[@state='0']"):
        sleep(4)
        end_time = time()
        if max_time:
            if end_time - start_time > max_time:
                return False
    if not safely_get_elements(driver, "//richlistbox[@id='downloadsRichListBox']/richlistitem[@state='3']"):
        return True
    else:
        return False


def scroll_to(driver: WebDriver, target: Union[List[int], int, WebElement]) -> None:
    """
    Function for scrolling to target position by location, height or Selenium web element.
    :param driver: Selenium web driver.
    :param target: Target to scroll to.
    """
    if isinstance(target, list):
        driver.execute_script(f"window.scrollTo({target[0]},{target[1]});")
    elif isinstance(target, int):
        driver.execute_script(f"window.scrollTo(0,{target});")
    elif isinstance(target, WebElement):
        ActionChains(driver).move_to_element(target).perform()


def open_tab(driver: WebDriver) -> None:
    """
    Function for opening new tab.
    :param driver: Selenium web driver.
    """
    ActionChains(driver).key_down(Keys.COMMAND).send_keys(
        "t").key_up(Keys.COMMAND).perform()
    driver.switch_to.window(driver.window_handles[-1])


def close_tab(driver: WebDriver) -> None:
    """
    Function for opening new tab.
    :param driver: Selenium web driver.
    """
    ActionChains(driver).key_down(Keys.COMMAND).send_keys(
        "w").key_up(Keys.COMMAND).perform()
    driver.switch_to.default_content()


def change_settings(driver: WebDriver, settings: List[Union[List[str], Tuple[str]]]) -> None:
    """
    Function for changing firefox settings at runtime.
    :param driver: Selenium web driver.
    :param settings: List of tuples of setting name and value.
    """
    open_tab(driver)
    driver.get("about:config")
    sleep(1)
    driver.find_element(By.XPATH, "//button[@id='warningButton']").click()
    input_box = driver.find_element(
        By.XPATH, "//input[@id='about-config-search']")
    for setting in settings:
        sleep(0.2)
        input_box.clear()
        input_box.send_keys(setting[0])
        sleep(0.2)
        entry = safely_get_element(driver, "//table[@id='prefs']/tr")
        if entry:
            entry_edit = safely_get_element(entry, "//td[@class='cell-edit']")
            entry_value = safely_get_text_content(
                entry, ".//td[@class='cell-value']/span/span")
            if entry_edit and entry_value:
                if entry_value != str(setting[1]).lower():
                    if isinstance(setting[1], bool):
                        entry_edit.find_element(By.XPATH, ".//button").click()
                        sleep(0.2)
                    else:
                        entry_edit.find_element(By.XPATH, ".//button").click()
                        sleep(0.2)
                        value_input = entry.find_element(
                            By.XPATH, ".//td[@class='cell-value']/form[@id='form-edit']/input")
                        value_input.send_keys(str(setting[1]))
                        value_input.send_keys(Keys.ENTER)
                        sleep(0.2)
    close_tab(driver)


def hover_over_element(driver: WebDriver, element: WebElement) -> None:
    """
    Function for hovering over element.
    :param driver: Selenium web driver or parent element.
    :param element: Web element to hover over.
    """
    ActionChains(driver).move_to_element(element).perform()


def get_targets_by_declaration(driver: WebDriver, declaration: Union[list, str]) -> Any:
    """
    Function for getting targets by declaration.
    :param driver: Selenium web driver or parent element.
    :param declaration: Target declaration.
    :return: Targets.
    """
    if isinstance(declaration, str):
        return safely_get_elements(driver, declaration)
    else:
        elements = safely_get_elements(driver, declaration[0])
        def func(x): return x
        if declaration[1].startwith("eval:"):
            func = declaration[1].replace("eval:", "")
        elif declaration[1].startswith("lambda"):
            func = eval(declaration[1])
        elif ".py" in declaration[1] and ":" in declaration[1]:
            func = environment_utility.get_function_from_path(declaration[1])
        return func(elements)
