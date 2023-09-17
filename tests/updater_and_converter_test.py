import pytest
import os
from enrich import updater_and_converter
from common_test import *

@pytest.fixture()
def ok_output_data():
    return [
        {'company_name': 'Intel', 'company_domain': 'intel.com','spend': '10432.56', 'currency_code': 'USD','currency_code_converted': 'EUR'},
        {'company_name': 'Intel', 'company_domain': 'intel.com','spend': '10865.12', 'currency_code': 'AUD','currency_code_converted': 'USD'},
        {'company_name': 'Shopify', 'company_domain': 'shopify.com','spend': '8753.89', 'currency_code': 'EUR','currency_code_converted': 'AUD'},
        {'company_name': 'IBM', 'company_domain': 'ibm.com','spend': '98723.45', 'currency_code': 'USD','currency_code_converted': 'EUR'}
    ]

@pytest.fixture()
def wrong_output_data():
    return [
        {'company_name': '', 'company_domain': '','spend': 'no_numeric_value', 'currency_code': 'BGN','currency_code_converted': 'ERROR'},
        {'company_name': 'fffffffff', 'company_domain': '','spend': '10432.12', 'currency_code': '','currency_code_converted': 'ERROR'},
        {'company_name': '', 'company_domain': 'ffffffff','spend': 'no_numeric_value', 'currency_code': 'CAD','currency_code_converted': 'ERROR'},
        {'company_name': 'ffffffff', 'company_domain': 'fffffffff','spend': '98723.45', 'currency_code': 'NOSYMBOL','currency_code_converted': 'ERROR'}
    ]

@pytest.fixture()
def ok_mocks():
    return [
        {'name': 'Intel', 'domain': 'intel.com','currency_code': 'EUR'},
        {'name': 'Intel', 'domain': 'intel.com','currency_code': 'USD'},
        {'name': 'Shopify', 'domain': 'shopify.com','currency_code': 'AUD'},
        {'name': 'IBM', 'domain': 'ibm.com','currency_code': 'EUR'}
    ]

@pytest.fixture()
def wrong_mocks():
    return [
        {'name': '', 'domain': '','currency_code': 'ERROR'},
        {'name': 'fffffffff', 'domain': '','currency_code': 'ERROR'},
        {'name': '', 'domain': 'ffffffff','currency_code': 'ERROR'},
        {'name': 'ffffffff', 'domain': 'fffffffff','currency_code': 'ERROR'}
    ]

def test_ok_updater_and_converter(ok_entries_data,currencies,ok_output_data,ok_mocks,mocker):

    for input_data,output_data,currency,mock in zip (ok_entries_data,ok_output_data,currencies,ok_mocks):

        mocker.patch(
        "enrich.frankfurter_call",
        return_value={'spend' : '' ,'currency_code' : mock['currency_code']},
        )
        mocker.patch(
        "enrich.clearbit_call",
        return_value={'name' : mock['name'],'domain' : mock['domain']},
        )

        updated_row,updated = updater_and_converter(currency,input_data)

        updated_row.pop('spend_converted')

        assert updated
        assert updated_row == output_data

def test_wrong_updater_and_converter(wrong_entries_data,currencies,wrong_output_data,wrong_mocks,mocker):

    for input_data,output_data,currency,mock in zip (wrong_entries_data,wrong_output_data,currencies,wrong_mocks):

        mocker.patch(
        "enrich.frankfurter_call",
        return_value={'spend' : '' ,'currency_code' : mock['currency_code']},
        )
        mocker.patch(
        "enrich.clearbit_call",
        return_value={'name' : mock['name'],'domain' : mock['domain']},
        )

        updated_row,updated = updater_and_converter(currency,input_data)

        updated_row.pop('spend_converted')

        assert not updated
        assert updated_row == output_data
