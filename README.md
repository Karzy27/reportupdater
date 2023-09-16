#Reportupdater

## About The Project

Reportupdater is a CLI that uses Clearbit API and Frankfurter API to update information about companies. It generates a file with updated company’s name, domain and converts its spend into a currency of your choosing.


## Getting Started

### Installation

- install the CLI from github
   ```sh
   pip install "git+https://github.com/Karzy27/reportupdater"
   ```
### CLI Help

```sh
>enrich -h
usage: enrich [-h] [--input INPUT] [--currency {AUD,BGN,BRL,CAD,CHF,CNY,CZK,DKK,EUR,GBP,HKD,HUF,IDR,ILS,INR,ISK,JPY,KRW,MXN,MYR,NOK,NZD,PHP,PLN,RON,SEK,SGD,THB,TRY,USD,ZAR}] [--output OUTPUT]
                     [--type {CSV,JSONL}]

        Reportupdater enriches information companies, generates a file
        with updated company’s name, domain and converts its spend into a currency of your choosing.

        - avaliable currencies are :
        ['AUD', 'BGN', 'BRL', 'CAD', 'CHF', 'CNY', 'CZK', 'DKK', 'EUR', 'GBP', 'HKD', 'HUF', 'IDR', 'ILS', 'INR', 'ISK', 'JPY', 'KRW', 'MXN', 'MYR', 'NOK', 'NZD', 'PHP', 'PLN', 'RON', 'SEK', 'SGD', 'THB', 'TRY', 'USD', 'ZAR']

        - requires input file to be .csv

        - writes updated information in .csv or .jsonl file

        - output file contains fieldnames :
        ['date', 'company_name', 'company_domain', 'spend', 'currency_code', 'spend_converted', 'currency_code_converted']



options:
  -h, --help            show this help message and exit
  --input INPUT, -i INPUT
                        File path to the report you want to enrich
  --currency {AUD,BGN,BRL,CAD,CHF,CNY,CZK,DKK,EUR,GBP,HKD,HUF,IDR,ILS,INR,ISK,JPY,KRW,MXN,MYR,NOK,NZD,PHP,PLN,RON,SEK,SGD,THB,TRY,USD,ZAR}, -c {AUD,BGN,BRL,CAD,CHF,CNY,CZK,DKK,EUR,GBP,HKD,HUF,IDR,ILS,INR,ISK,JPY,KRW,MXN,MYR,NOK,NZD,PHP,PLN,RON,SEK,SGD,THB,TRY,USD,ZAR}
                        Currency to wich convert spend
  --output OUTPUT, -o OUTPUT
                        File path in wich the updated report will be saved
  --type {CSV,JSONL}, -t {CSV,JSONL}
                        File type of the updated report
```

## Example usage

```sh
>cat input.csv
date,company_name,company_domain,spend,currency_code
2023-09-01,,intel.com,10432.56,USD
2023-09-02,,intel.com,9354.02,USD
2023-09-01,Shopify,shopify.com.com,6778.45,EUR
2023-09-01,IBM,,14876.78,USD
2023-09-01,,,21375.65,EUR
```

```sh
>enrich -i input.csv -o output.csv
Rows updated : 5
Output file written to output.csv in CSV
```

```sh
>cat output.csv
date,company_name,company_domain,spend,currency_code,spend_converted,currency_code_converted
2023-09-01,Intel,intel.com,10432.56,USD,10432.56,USD
2023-09-02,Intel,intel.com,9354.02,USD,9354.02,USD
2023-09-01,Shopify,shopify.com,6778.45,EUR,7224,USD
2023-09-01,IBM,ibm.com,14876.78,USD,14876.78,USD
2023-09-01,,,21375.65,EUR,22782,USD
```

