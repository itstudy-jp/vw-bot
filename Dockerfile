FROM python:3.13.3-slim

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/ /usr/src/app/

CMD ["python", "main.py"]
