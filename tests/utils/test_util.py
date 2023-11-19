import datetime
import json
import logging
from unittest.mock import mock_open, patch

import pytest

from bumper.utils import utils

# Assuming _LOGGER is a logger instance, you can use a test logger for capturing logs in tests
test_logger = logging.getLogger("test_logger")


def test_default_log_warn_not_impl(caplog: pytest.LogCaptureFixture):
    caplog.set_level(logging.DEBUG)

    func_name = "some_function"
    utils.default_log_warn_not_impl(func_name)

    assert f"POSSIBLE THIS API IS NOT (FULL) IMPLEMENTED :: {func_name}" in caplog.text


def test_default_exception_str_builder():
    exception_msg = "An error occurred"
    info_msg = "Some additional info"
    e = Exception(exception_msg)

    result = utils.default_exception_str_builder(e, info_msg)

    assert f"Unexpected exception occurred :: {info_msg} :: {e}" == result


def test_default_exception_str_builder_no_info():
    exception_msg = "An error occurred"
    e = Exception(exception_msg)

    result = utils.default_exception_str_builder(e)

    assert f"Unexpected exception occurred :: {e}" == result


# ******************************************************************************


def test_get_milli_time():
    assert utils.convert_to_millis(datetime.datetime(2018, 1, 1, 1, 0, 0, 0, tzinfo=datetime.UTC).timestamp()) == 1514768400000


def test_get_current_time_as_millis():
    # Get the current time in milliseconds using the function
    current_time = utils.get_current_time_as_millis()

    # Get the current time using Python's datetime module
    expected_time = int(datetime.datetime.now(datetime.UTC).timestamp() * 1000)

    # Assert that the current time obtained from the function is close to the expected time
    # This is to account for potential slight variations due to the time it takes to execute the test
    assert abs(current_time - expected_time) < 1000, "Current time in milliseconds is not within an acceptable range."


def test_str_to_bool_true():
    assert utils.str_to_bool("True") is True
    assert utils.str_to_bool("true") is True
    assert utils.str_to_bool("1") is True
    assert utils.str_to_bool("t") is True
    assert utils.str_to_bool("y") is True
    assert utils.str_to_bool("on") is True
    assert utils.str_to_bool("yes") is True


def test_str_to_bool_false():
    assert utils.str_to_bool("False") is False
    assert utils.str_to_bool("false") is False
    assert utils.str_to_bool("0") is False
    assert utils.str_to_bool("f") is False
    assert utils.str_to_bool("n") is False
    assert utils.str_to_bool("off") is False
    assert utils.str_to_bool("no") is False


def test_str_to_bool_random():
    # Test with any random values
    invalid_values = ["", "random", "123", "abc", None, 123, False]
    for value in invalid_values:
        assert utils.str_to_bool(value) is False


def test_str_to_bool_none():
    # Test with None
    assert utils.str_to_bool(None) is False  # Assuming you want to treat None as False


# ******************************************************************************


def test_is_valid_url_valid_urls():
    valid_urls = ["http://example.com", "https://www.example.com", "ftp://ftp.example.com"]
    for url in valid_urls:
        assert utils.is_valid_url(url) is True


def test_is_valid_url_invalid_urls():
    invalid_urls = ["not_a_url", "www.example.com", None, ""]
    for url in invalid_urls:
        assert utils.is_valid_url(url) is False


def test_is_valid_ip_valid_ips():
    valid_ips = ["192.168.0.1", "2001:db8::1"]
    for ip in valid_ips:
        assert utils.is_valid_ip(ip) is True


def test_is_valid_ip_invalid_ips():
    invalid_ips = ["not_an_ip", "256.256.256.256", "invalid:ip::address", None, ""]
    for ip in invalid_ips:
        assert utils.is_valid_ip(ip) is False


def test_is_valid_ip_empty_string():
    # Test an empty string
    assert utils.is_valid_ip("") is False


def test_is_valid_ip_none():
    # Test None as input
    assert utils.is_valid_ip(None) is False


# ******************************************************************************

# Mock data for testing
MOCK_JSON_DATA = {
    "00": "dc",
    "cn": "ap",
    "tw": "ap",
    "my": "ap",
    "jp": "ap",
    "sg": "ap",
    "de": "eu",
    "at": "eu",
    "li": "eu",
    "fr": "eu",
}


def test_get_dc_code_existing_area():
    with patch("bumper.utils.utils.get_area_code_map", return_value=MOCK_JSON_DATA):
        assert utils.get_dc_code("cn") == "ap"
        assert utils.get_dc_code("de") == "eu"
        assert utils.get_dc_code("00") == "dc"


def test_get_dc_code_non_existing_area():
    with patch("bumper.utils.utils.get_area_code_map", return_value=MOCK_JSON_DATA):
        assert utils.get_dc_code("nonexistent") == "na"
        assert utils.get_dc_code("iwashere") == "na"


def test_get_dc_code_empty_map():
    with patch("bumper.utils.utils.get_area_code_map", return_value={}):
        assert utils.get_dc_code("cn") == "na"


def test_get_area_code_map_valid_json():
    with patch("builtins.open", mock_open(read_data=json.dumps(MOCK_JSON_DATA)), create=True):
        assert utils.get_area_code_map() == MOCK_JSON_DATA


def test_get_area_code_map_invalid_json():
    invalid_json = "invalid_json"
    with patch("builtins.open", mock_open(read_data=invalid_json), create=True):
        assert utils.get_area_code_map() == {}


def test_get_area_code_map_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError):
        assert utils.get_area_code_map() == {}


def test_get_area_code_map_empty_file():
    with patch("builtins.open", mock_open(read_data="{}"), create=True):
        assert utils.get_area_code_map() == {}


def test_get_area_code_map_exception():
    with patch("builtins.open", side_effect=Exception):
        assert utils.get_area_code_map() == {}


# ******************************************************************************


def test_check_url_not_used_multiple_patterns():
    urls = [
        "/api/appsvr/app.do",
        "/api/appsvr/some_endpoint",
        "/api/some_other_endpoint",
        "",
        "/api/appsvr/app[.]do",
    ]

    results = [utils.check_url_not_used(url) for url in urls]
    assert results == [True, False, False, False, False]


def test_check_url_not_used_none_url():
    with pytest.raises(TypeError):
        utils.check_url_not_used(None)
