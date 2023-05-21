FROM python:3.11.3-alpine

COPY ../app /app
WORKDIR /app

RUN pip install -r ./requirements.txt

CMD ["python", "conn_monitor.py"]