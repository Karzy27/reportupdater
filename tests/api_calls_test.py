import pytest
import os
from enrich import clearbit_call,frankfurter_call
from common_test import *



@pytest.fixture()
def ok_output_data():
    return [
        { 'company_name': 'Intel', 'company_domain': 'intel.com','currency_code': 'EUR'},
        { 'company_name': 'Intel', 'company_domain': 'intel.com','currency_code': 'USD'},
        { 'company_name': 'Shopify', 'company_domain': 'shopify.com','currency_code': 'AUD'},
        { 'company_name': 'IBM', 'company_domain': 'ibm.com','currency_code': 'EUR'}
    ]

@pytest.fixture()
def wrong_output_data():
    return [
        {'company_name': '', 'company_domain': '','spend': '', 'currency_code': 'ERROR'},
        {'company_name': 'fffffffff', 'company_domain': '','spend': '', 'currency_code': 'ERROR'},
        {'company_name': '', 'company_domain': 'ffffffff','spend': '', 'currency_code': 'ERROR'},
        {'company_name': 'ffffffff', 'company_domain': 'fffffffff','spend': '', 'currency_code': 'ERROR'}
    ]

@pytest.fixture()
def search_selection():
    return  ['name','domain','name','name']


def test_clearbit_api_ok(ok_entries_data,ok_output_data,search_selection):
    
    for selection,input_data,output_data in zip(search_selection,ok_entries_data,ok_output_data):
        response_data = clearbit_call(selection,input_data)
        assert response_data['name'] == output_data['company_name']
        assert response_data['domain'] == output_data['company_domain']

def test_clearbit_api_error(wrong_entries_data,wrong_output_data,search_selection):
    
    for selection,input_data,output_data in zip(search_selection,wrong_entries_data,wrong_output_data):
        response_data = clearbit_call(selection,input_data)
        assert response_data['name'] == output_data['company_name']
        assert response_data['domain'] == output_data['company_domain']

def test_frankfurter_api_ok(ok_entries_data,ok_output_data,currencies):
    
    for currency,input_data,output_data in zip(currencies,ok_entries_data,ok_output_data):
        response_data = frankfurter_call(currency,input_data)
        assert response_data['currency_code'] == output_data['currency_code']
        

def test_frankfurter_api_error(wrong_entries_data,wrong_output_data,currencies):
    
    for currency,input_data,output_data in zip(currencies,wrong_entries_data,wrong_output_data):
        print(currency)
        print(input_data)
        response_data = frankfurter_call(currency,input_data)
        assert response_data['currency_code'] == output_data['currency_code']
        



    
