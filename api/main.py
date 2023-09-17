from fastapi import FastAPI,File, UploadFile
import csv
from enrich import updater_and_converter

app = FastAPI()

@app.post("/enrich",response_model=list[dict])
async def enrich(currency: str = 'USD', file: UploadFile = File(...)):
    with open(file.filename,encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        updated = 0
        updated_data = []
        for row in reader:
            updated_row,updated = updater_and_converter(currency,row)
            updated_data.append(updated_row)
        return updated_data

