import typing

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from je_web_runner.utils.exception.exceptions import WebRunnerAssertException


def _make_webdriver_check_dict(webdriver_to_check: WebDriver) -> dict:
    """
    use to check webdriver current info
    :param webdriver_to_check: what webdriver we want to check
    :return: webdriver detail dict
    """
    webdriver_detail_dict = dict()
    webdriver_detail_dict.update(
        {
            "mobile": webdriver_to_check.mobile,
            "name": webdriver_to_check.name,
            "title": webdriver_to_check.title,
            "current_url": webdriver_to_check.current_url,
            "page_source": webdriver_to_check.page_source,
            "current_window_handle": webdriver_to_check.current_window_handle,
            "window_handles": webdriver_to_check.window_handles,
            "switch_to": webdriver_to_check.switch_to,
            "timeouts": webdriver_to_check.timeouts,
            "capabilities": webdriver_to_check.capabilities,
            "file_detector": webdriver_to_check.file_detector,
            "application_cache": webdriver_to_check.application_cache,
            "virtual_authenticator_id": webdriver_to_check.virtual_authenticator_id
        }
    )
    return webdriver_detail_dict


def _make_web_element_check_dict(web_element_to_check: WebElement) -> dict:
    """
    use to check web element current info
    :param web_element_to_check: what web element we want to check
    :return: web element detail dict
    """
    web_element_detail_dict = dict()
    web_element_detail_dict.update(
        {
            "tag_name": web_element_to_check.tag_name,
            "text": web_element_to_check.text,
            "location_once_scrolled_into_view": web_element_to_check.location_once_scrolled_into_view,
            "size": web_element_to_check.size,
            "location": web_element_to_check.location,
            "parent": web_element_to_check.parent,
            "id": web_element_to_check.id,
        }
    )
    return web_element_detail_dict


def check_value(element_name: str, element_value: typing.Any, result_check_dict: dict) -> None:
    """
    use to check state
    :param element_name: the name of element we want to check
    :param element_value: what value element should be
    :param result_check_dict: the dict include data name and value to check check_dict is valid or not
    :return: None
    """
    if result_check_dict.get(element_name) != element_value:
        raise WebRunnerAssertException(
            "value should be {right_value} but value was {wrong_value}".format(
                right_value=element_value, wrong_value=result_check_dict.get(element_name)
            )
        )


def check_values(check_dict: dict, result_check_dict: dict) -> None:
    """
    :param check_dict: dict include data name and value to check
    :param result_check_dict: the dict include data name and value to check check_dict is valid or not
    :return: None
    """
    for key, value in result_check_dict.items():
        if check_dict.get(key) != value:
            raise WebRunnerAssertException(
                "value should be {right_value} but value was {wrong_value}".format(
                    right_value=value, wrong_value=check_dict.get(key)
                )
            )


def check_webdriver_value(element_name: str, element_value: typing.Any, webdriver_to_check: WebDriver) -> None:
    """
    :param element_name: the name of element we want to check
    :param element_value: what value element should be
    :param webdriver_to_check: the dict include data name and value to check result_dict is valid or not
    :return: None
    """
    check_dict = _make_webdriver_check_dict(webdriver_to_check)
    check_value(element_name, element_value, check_dict)


def check_webdriver_details(webdriver_to_check: WebDriver, result_check_dict: dict) -> None:
    """
    :param webdriver_to_check: what webdriver we want to check
    :param result_check_dict: the dict include data name and value to check result_dict is valid or not
    :return: None
    """
    check_dict = _make_webdriver_check_dict(webdriver_to_check)
    check_values(check_dict, result_check_dict)


def check_web_element_value(element_name: str, element_value: typing.Any, web_element_to_check: WebElement) -> None:
    """
    :param element_name: the name of element we want to check
    :param element_value: what value element should be
    :param web_element_to_check: the dict include data name and value to check result_dict is valid or not
    :return: None
    """
    check_dict = _make_web_element_check_dict(web_element_to_check)
    check_value(element_name, element_value, check_dict)


def check_web_element_details(web_element_to_check: WebElement, result_check_dict: dict) -> None:
    """
    :param web_element_to_check: what web element we want to check
    :param result_check_dict: the dict include data name and value to check result_dict is valid or not
    :return: None
    """
    check_dict = _make_web_element_check_dict(web_element_to_check)
    check_values(check_dict, result_check_dict)
