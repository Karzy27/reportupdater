import pytest
import os

@pytest.fixture()
def currencies():
    return  ['EUR','USD','AUD','EUR']

@pytest.fixture()
def ok_entries_data():
    return [
        {'company_name': 'Intel', 'company_domain': '','spend': '10432.56', 'currency_code': 'USD'},
        {'company_name': '', 'company_domain': 'intel.com','spend': '10865.12', 'currency_code': 'AUD'},
        {'company_name': 'Shopify', 'company_domain': 'shopify.com.com','spend': '8753.89', 'currency_code': 'EUR'},
        {'company_name': 'IBM', 'company_domain': 'ibm.com','spend': '98723.45', 'currency_code': 'USD'}
    ]

@pytest.fixture()
def wrong_entries_data():
    return [
        {'company_name': '', 'company_domain': '','spend': 'no_numeric_value', 'currency_code': 'BGN'},
        {'company_name': 'fffffffff', 'company_domain': '','spend': '10432.12', 'currency_code': ''},
        {'company_name': '', 'company_domain': 'ffffffff','spend': 'no_numeric_value', 'currency_code': 'CAD'},
        {'company_name': 'ffffffff', 'company_domain': 'fffffffff','spend': '98723.45', 'currency_code': 'NOSYMBOL'}
    ]