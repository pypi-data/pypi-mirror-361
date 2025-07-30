# fastapi_csv_download

A simple FastAPI utility to generate downloadable CSV responses.

## Installation

```bash
pip install fastapi-csv-download
```

## Usage

```
from fastapi import FastAPI
from fastapi_csv_downloader import generate_csv_response

app = FastAPI()

@app.get("/download")
async def download_csv():
    data = [{"id": 1, "name": "Laptop", "price": 1000}]
    return generate_csv_response(data, filename="products.csv")
```
