import pytest
import os
import json
from enrich import csv_file_writer,jsonl_file_writer


@pytest.fixture()
def reader_data():
    return [
        {'date': '2023-09-01', 'company_name': '', 'company_domain': 'intel.com', 'spend': '10432.56', 'currency_code': 'USD'},
        {'date': '2023-09-01', 'company_name': 'Intel', 'company_domain': '', 'spend': '10432.56', 'currency_code': 'USD'}
    ]
@pytest.fixture()  
def jsonl_result():
    return [
        {'date': '2023-09-01', 'company_name': 'Intel', 'company_domain': 'intel.com', 'spend': '10432.56', 'currency_code': 'USD', 'currency_code_converted': 'USD'},
        {'date': '2023-09-01', 'company_name': 'Intel', 'company_domain': 'intel.com', 'spend': '10432.56', 'currency_code': 'USD', 'currency_code_converted': 'USD'}
    ]

@pytest.fixture()  
def csv_result():
    return ["date,company_name,company_domain,spend,currency_code,spend_converted,currency_code_converted",
            "2023-09-01,Intel,intel.com,10432.56,USD,USD",
            "2023-09-01,Intel,intel.com,10432.56,USD,USD"
    ]
    
    
def test_jsonl_file_writer(reader_data,jsonl_result,tmp_path):
    temp_dir = tmp_path / 'test_writer_dir'
    temp_dir.mkdir()
    output_file = temp_dir / 'test_output.jsonl'
    currency = 'USD'
    updated_rows = jsonl_file_writer(output_file,reader_data,'USD')
    assert os.path.isfile(output_file)
    with open(output_file, 'r') as output_test_file:
        data = []
        for row in output_test_file:
            json_row = json.loads(row)
            json_row.pop('spend_converted')
            data.append(json_row)
        assert data == jsonl_result
    assert updated_rows == 2

def test_csv_file_writer(reader_data,csv_result,tmp_path):
    fieldnames = ['date','company_name','company_domain','spend','currency_code','spend_converted','currency_code_converted']
    temp_dir = tmp_path / 'test_writer_dir'
    temp_dir.mkdir()
    output_file = temp_dir / 'test_output.csv'
    currency = 'USD'
    updated_rows = csv_file_writer(output_file,fieldnames,reader_data,'USD')
    assert os.path.isfile(output_file)
    with open(output_file, 'r') as output_test_file:
        data = []
        for row in output_test_file:
            clean_row = row.strip()
            if clean_row.split(',') == fieldnames:
                data.append(clean_row)
            else:
                csv_row = clean_row.split(',')
                csv_row.pop(5)
                data.append(','.join(csv_row))
        assert data == csv_result
    assert updated_rows == 2
    