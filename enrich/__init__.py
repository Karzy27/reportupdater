import argparse
import requests
import logging
import os
import sys
import json
import csv


logger = logging.getLogger(__name__)

AUTH_KEY_CLEARBIT = 'sk_f684554b14daff33940a73c80fa134fb'
FIELDNAMES = ['date','company_name','company_domain','spend','currency_code','spend_converted','currency_code_converted']

def get_currencies():
    '''
    Provides avaliable currencies for conversion from frankfurter app
    Return:
        - Dict containing currency symbol as key and description as value
    '''
    try:
        response = requests.get(f'https://api.frankfurter.app/currencies')
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.error(f'Currency list is unavaliable: {err}')
    return response.json()

def parse_args(args):
    '''
    Parser for parameters recieved by reportupdater CLI
    Parameters:
        - args : arguments recieved to parse
    Returns:
        - populated namespace for args

    '''
    # Getting avaliable currencies to convert
    currencies = get_currencies()
    currency_symbols = list(currencies.keys())

    # Creating parser
    parser = argparse.ArgumentParser(
        prog='enrich',
        description=f'''
        Reportupdater enriches information companies, generates a file
        with updated company’s name, domain and converts its spend into a currency of your choosing.

        - avaliable currencies are :
        {currency_symbols}

        - requires input file to be .csv

        - writes updated information in .csv or .jsonl file

        - output file contains fieldnames :
        {FIELDNAMES}
        
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    # Adding arguments to parser
    parser.add_argument(
        '--input',
        '-i',
        type=str,
        help='File path to the report you want to enrich'
    )
    parser.add_argument(
        '--currency',
        '-c',
        type=str,
        choices=currency_symbols,
                    default='USD', required=False,
        help='Currency to wich convert spend'
    )
    parser.add_argument(
        '--output',
        '-o',
        type=str,
        help='File path in wich the updated report will be saved'
    )
    parser.add_argument(
        '--type',
        '-t',
        type=str,
        choices=['CSV','JSONL'],
                    default='CSV', required=False,
        help='File type of the updated report'
    )

    # Parsing args
    args = parser.parse_args(args)

    # Checking the input report provided is a valid file
    try: 
        with open(args.input, newline='') as csvfile:
            reader = csv.DictReader(csvfile)       
    except Exception as err:
        parser.error(str(err))

    directory,filename = os.path.split(args.input)
    root,ext = os.path.splitext(filename)
    if ext != '.csv' :
        parser.error(f'{filename} is not a csv file')

    # Checking the output path is a valid path
    directory,filename = os.path.split(args.output)
    if not os.path.isdir(directory) and directory != '':
        parser.error(f'{directory} is not a valid directory')
    root,ext = os.path.splitext(filename)
    if ext not in ['.csv','.jsonl'] :
        parser.error(f'{filename} is not a valid file name')

    return args

def frankfurter_call(currency,row):
    '''
    Provides a spend conversion from a determined currency to another currency
    Uses Frankfurter API
    Parameters:
        - currency (String) : Symbol of the currency to convert spend to
        - row (Dict) : Entry from a csv containing data from a company
            expected {key:value} :
            - currency_code(String) : Current spend currency symbol
            - spend(Int) : Amount of money expressed in currency_code
    Returns:
        - Dict containing spend in converted currency and converted currency symbol
    '''

    params = {'amount':row['spend'], 'to':currency, 'from':row['currency_code']}
    
    # Check if both currencies are the same
    if currency == row['currency_code']:
        same_data = {'spend':row['spend'],'currency_code':row['currency_code']}
        return same_data

    try:
        response = requests.get(f'https://api.frankfurter.app/latest?',params = params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.warning(f'''Could not convert company ({row['company_name']}) spend to desired currency {currency}:
         {err}''')
        failed_data = {'spend':'','currency_code':'ERROR'}
        return failed_data
    
    converted_data = response.json()
    converted_data = {'spend':converted_data['rates'][currency],'currency_code':currency}
    return converted_data


def clearbit_call(search_selection,row):
    '''
    Provides a company’s name and domain update
    Uses Clearbit API
    Parameters:
        - search_selection (String) : Flag that determines the type of search
            - 'domain' : search using the company’s domain
            - 'name'   : search using the company’s name
        - row (Dict) : Entry from a csv containing data from a company
            expected {key:value} :
            - company_name(String) : name of the company
            - company_domain(String) : domain of the company
    Returns:
        - Dict containing updated company name and company domain
    '''  
    headers = {'Authorization': f'Bearer {AUTH_KEY_CLEARBIT}'}
    params = {search_selection:row[f'company_{search_selection}']}

    if search_selection == 'domain':
        http_path = 'https://company.clearbit.com/v2/companies/find?'
    else:
        http_path = 'https://company.clearbit.com/v1/domains/find?'

    try:
        response = requests.get(http_path,headers=headers,params = params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        # A http error means the name/domain provided is from an unknown company 
        # so we return the original data name and domain without updates
        original_data = {'name':row['company_name'],'domain':row['company_domain']}
        return original_data

    return response.json()

def updater_and_converter(currency,row):
    '''
    Updates entries company’s name, domain and converts company’s spend to a provided currency 
    Parameters:
        - currency (String) : Symbol of the currency to convert spend to
        - row (Dict) : Entry from a csv containing data from a company
    Returns:
        - Updated entry of company’s data (if posible)
        - Flag indicating if entry could be updated
    '''
    # Calling the name and domain updating function
    updated = False
    if row['company_name'] == '':
        results = clearbit_call('domain',row)
    else:
        results = clearbit_call('name',row)

    # Calling the spend conversion function
    conversion = frankfurter_call(currency,row)

    # Checking if entry was updated
    if row['company_name'] != results['name'] or row['company_domain'] != results['domain'] or (row['currency_code'] != conversion['currency_code'] and conversion['currency_code'] != 'ERROR'):
        updated = True
    # Generating updated entry with new fields  
    updated_row = row
    updated_row['company_name'] = results['name']
    updated_row['company_domain'] = results['domain']
    updated_row['spend_converted'] = conversion['spend']
    updated_row['currency_code_converted'] = conversion['currency_code']
    return updated_row,updated

def csv_file_writer(output_file,fieldnames,reader,currency):
    '''
    Generates the output csv file containing the updated company entries 
    Parameters:
        - output_file (String) : Path where the output file will be generated
        - fieldnames (String) : Fieldnames of the output file
        - reader (Reader) : Reader object for the input file
        - currency (String) : Symbol of the currency to convert spend to
    Returns:
        - Number of updated entries in the output file with respect to the input file
    '''
    updated_rows=0
    with open(output_file,'w', newline='') as csv_out_file:
        writer = csv.DictWriter(csv_out_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            updated_row,updated = updater_and_converter(currency,row)
            if updated:
                updated_rows += 1
            writer.writerow(updated_row)
    return updated_rows

def jsonl_file_writer(output_file,reader,currency):
    '''
    Generates the output jsonl file containing the updated company entries 
    Parameters:
        - output_file (String) : Path where the output file will be generated
        - fieldnames (String) : Fieldnames of the output file
        - reader (Reader) : Reader object for the input file
        - currency (String) : Symbol of the currency to convert spend to
    Returns:
        - Number of updated entries in the output file with respect to the input file
    '''
    updated_rows=0
    with open(output_file, 'w') as jsonl_out_file:
        for row in reader:
            updated_row,updated = updater_and_converter(currency,row)
            if updated:
                updated_rows += 1
            json.dump(updated_row, jsonl_out_file)
            jsonl_out_file.write('\n')
    return updated_rows

def enrich_report(input_file,currency,output_file,file_type):
    '''
    Starts the enrichment process, reads input file and calls writer 
    Parameters:
        - output_file (String) : Path where the output file will be generated
        - currency (String) : Symbol of the currency to convert spend to
        - input_file (String) : Path to the input file
        - file_type (String) : Type of the input file
        
    Returns:
        - None
    ''' 
    with open(input_file, newline='') as csv_in_file:
        reader = csv.DictReader(csv_in_file)
        # Checking type of the input file
        if file_type == 'CSV':
            output_file = output_file.replace('.jsonl','.csv')
            updated_rows = csv_file_writer(output_file,FIELDNAMES,reader,currency)
        else:
            output_file = output_file.replace('.csv','.jsonl')
            updated_rows = jsonl_file_writer(output_file,reader,currency)
    print(f'Rows updated : {updated_rows}')
    print(f'Output file written to {output_file} in {file_type}')
        


def entrypoint():
    '''
    Entry point to reportupdater CLI
    Returns:
        - None
    '''
    args = parse_args(sys.argv[1:])
    enrich_report(args.input,args.currency,args.output,args.type)



if __name__ == '__main__':
    entrypoint()