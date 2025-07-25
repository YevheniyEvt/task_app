FROM python:3.13-alpine

RUN pip install --upgrade pip setuptools wheel

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000



