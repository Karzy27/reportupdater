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


def parse_args(args):
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
        choices=['USD'],
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
    except Exception as e:
        parser.error(str(e))

    # Checking the output path is a valid path
    #if not os.path.isdir(args.output):
     #   parser.error(f"{args.output} is not a valid directory")

    return args
    

def enrich_report(input_file,currency,output_file,file_type):
    headers = {'Authorization': f'Bearer {AUTH_KEY_CLEARBIT}'}
    updated_rows = 0
    fieldnames = ['date','company_name','company_domain','spend','currency_code']
    with open(input_file, newline='') as csv_in_file:
        reader = csv.DictReader(csv_in_file)
        with open(output_file,'w', newline='') as csv_out_file:
            writer = csv.DictWriter(csv_out_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                params = {'name':row['company_name']}
                company_data = requests.get(f'https://company.clearbit.com/v1/domains/find?',headers=headers,params = params)
                company_data.raise_for_status()
                results = company_data.json()
                if row['company_name'] != results['name'] or row['company_domain'] != results['domain']:
                    updated_rows += 1
                row['company_name'] = results['name']
                row['company_domain'] = results['domain']
                writer.writerow(row)
    print(f'Rows updated : {updated_rows}')
    print(f'Output file written to {output_file} in {file_type}')
        


def entrypoint():
    args = parse_args(sys.argv[1:])
    enrich_report(args.input,args.currency,args.output,args.type)



if __name__ == '__main__':
    entrypoint()