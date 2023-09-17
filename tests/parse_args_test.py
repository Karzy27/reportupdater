import pytest
import os
from enrich import parse_args

@pytest.fixture
def ok_args():
    
    return [
        "--input ./test_files/test_input.csv --output ./test_files/test_output.csv",
        "--input ./test_files/test_input.csv --output ./test_files/test_output.csv --type CSV",
        "--input ./test_files/test_input.csv --output ./test_files/test_output.jsonl --type JSONL",
        "--input ./test_files/test_input.csv --output ./test_files/test_output.jsonl --type CSV",
        "--input ./test_files/test_input.csv --output ./test_files/test_output.csv --type JSONL",
        "--input ./test_files/test_input.csv --output ./test_files/test_output.csv --currency USD",
        "--input ./test_files/test_input.csv --output ./test_files/test_output.csv --currency EUR"
    ]

@pytest.fixture
def wrong_input():
    return [
        "--input ./test_files/test_input.fff --output ./test_files/test_output.csv",
        "--input wrong_directory/test_input.csv --output ./test_files/test_output.csv",
        "--input ./test_files/no_exixting_file.csv --output ./test_files/test_output.csv"
    ]

@pytest.fixture
def wrong_output():
    return [
        "--input ./test_files/test_input.csv --output ./test_files/test_output.fff",
        "--input ./test_files/test_input.csv --output wrong_directory/test_output.csv",
        "--input ./test_files/test_input.csv --output ./test_files/"
    ]



def test_ok_args(ok_args):
    for item in ok_args:
        parse_args(item.split())


def test_wrong_type_file():
    wrong_type = "--input ./test_files/test_input.csv --output ./test_files/test_output.csv --type FFF"
    with pytest.raises(SystemExit):
        parse_args(wrong_type.split())

def test_wrong_currency_symbol():
    wrong_currency = "--input ./test_files/test_input.csv --output ./test_files/test_output.csv --currency FFF"
    with pytest.raises(SystemExit):
        parse_args(wrong_currency.split())

def test_wrong_input_file(wrong_input):
    for item in wrong_input:
        with pytest.raises(SystemExit):
            parse_args(item.split())

def test_wrong_output_file(wrong_output):
    for item in wrong_output:
        with pytest.raises(SystemExit):
            parse_args(item.split())


