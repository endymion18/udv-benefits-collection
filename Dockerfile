FROM python:3.11

RUN mkdir /udv-benefits-collection

WORKDIR /udv-benefits-collection

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
