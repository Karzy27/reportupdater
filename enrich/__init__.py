import argparse
import requests
import logging
import os
import sys
import json
import csv
from datetime import datetime


logger = logging.getLogger(__name__)

AUTH_KEY_CLEARBIT = 'sk_f684554b14daff33940a73c80fa134fb'
FIELDNAMES = ['date','company_name','company_domain','spend','currency_code','spend_converted','currency_code_converted']

def get_currencies():
    try:
        response = requests.get(f'https://api.frankfurter.app/currencies')
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.error(f'Currency list is unavaliable: {err}')
    return response.json()

def parse_args(args):
    currencies = get_currencies()
    currency_symbols = list(currencies.keys())
    parser = argparse.ArgumentParser(
        prog='enrich',
        description=f"""
        Updates information about company names, company domains and spend in different currencies from a csv report
        """,
        formatter_class=argparse.RawTextHelpFormatter
    )
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
    args = parser.parse_args(args)
    # Checking the input report provided is a valid file
    try: 
        with open(args.input, newline='') as csvfile:
            reader = csv.DictReader(csvfile)       
    except Exception as err:
        parser.error(str(err))
    # Checking the output path is a valid path
    directory,filename = os.path.split(args.output)
    if not os.path.isdir(directory) and directory != '':
        parser.error(f"{directory} is not a valid directory")
    root,ext = os.path.splitext(filename)
    if ext not in ['.csv','.jsonl'] :
        parser.error(f"{filename} is not a valid file name")

    return args

def frankfurter_call(row,currency):
    params = {'amount':row['spend'], 'to':currency, 'from':row['currency_code']}
    if currency == row['currency_code']:
        same_data = {'spend':row['spend'],'currency_code':row['currency_code']}
        return same_data
    try:
        response = requests.get(f'https://api.frankfurter.app/latest?',params = params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.warning(f'''Could not convert company ({row['company_name']}) spend to desired currency {currency}:
         {err}
    Moving to next entry conversion''')
        failed_data = {'spend':'','currency_code':'ERROR'}
        return failed_data
    converted_data = response.json()
    converted_data = {'spend':converted_data['rates'][currency],'currency_code':currency}
    return converted_data


def clearbit_call(row,search_selection):  
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
        ''' A http error means the name/domain provided is from an unknown company 
            so we return the original data name and domain without updates '''
        original_data = {'name':row['company_name'],'domain':row['company_domain']}
        return original_data
    return response.json()

def updater_and_converter(row,currency):
    updated = False
    if row['company_name'] == '':
        results = clearbit_call(row,'domain')
    else:
        results = clearbit_call(row,'name')
    conversion = frankfurter_call(row,currency)
    if row['company_name'] != results['name'] or row['company_domain'] != results['domain'] or (row['currency_code'] != conversion['currency_code'] and conversion['currency_code'] != 'ERROR'):
        updated = True
    updated_row = row
    updated_row['company_name'] = results['name']
    updated_row['company_domain'] = results['domain']
    updated_row['spend_converted'] = conversion['spend']
    updated_row['currency_code_converted'] = conversion['currency_code']
    return updated_row,updated

def csv_file_writer(output_file,fieldnames,reader,currency):
    updated_rows=0
    with open(output_file,'w', newline='') as csv_out_file:
        writer = csv.DictWriter(csv_out_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            updated_row,updated = updater_and_converter(row,currency)
            if updated:
                updated_rows += 1
            writer.writerow(updated_row)
    return updated_rows

def jsonl_file_writer(output_file,reader,currency):
    updated_rows=0
    with open(output_file, 'w') as jsonl_out_file:
        for row in reader:
            updated_row,updated = updater_and_converter(row,currency)
            if updated:
                updated_rows += 1
            json.dump(updated_row, jsonl_out_file)
            jsonl_out_file.write('\n')
    return updated_rows

def enrich_report(input_file,currency,output_file,file_type):  
       
    with open(input_file, newline='') as csv_in_file:
        reader = csv.DictReader(csv_in_file)
        if file_type == 'CSV':
            output_file = output_file.replace('.jsonl','.csv')
            updated_rows = csv_file_writer(output_file,fieldnames,reader,currency)
        else:
            output_file = output_file.replace('.csv','.jsonl')
            updated_rows = jsonl_file_writer(output_file,reader,currency)
    print(f'Rows updated : {updated_rows}')
    print(f'Output file written to {output_file} in {file_type}')
        


def entrypoint():
    args = parse_args(sys.argv[1:])
    enrich_report(args.input,args.currency,args.output,args.type)



if __name__ == '__main__':
    entrypoint()