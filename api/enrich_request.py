import requests
import os
import sys
import json
import csv


def main():
    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    type_file = sys.argv[3]
    currency = sys.argv[4]
    

    fieldnames = ['date','company_name','company_domain','spend','currency_code','spend_converted','currency_code_converted']

    url = f'http://127.0.0.1:8000/enrich'
    input_file = {'file': open(input_file_path, 'rb')}
    params = {'currency': currency}     
    resp = requests.post(url=url, files=input_file,params=params)
    

    with open(output_file_path, 'w',newline='') as out_file:
        if type_file == 'JSONL':
            for row in resp.json():
                json.dump(row, out_file)
                out_file.write('\n')
        else:
            writer = csv.DictWriter(out_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in resp.json():
                writer.writerow(row)

    




if __name__ == '__main__':
    main()