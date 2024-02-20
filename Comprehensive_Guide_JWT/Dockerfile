FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /home

COPY ./requirements.txt .

COPY * .

RUN pip install -r requirements.txt

RUN pip install -r requirements.txt && adduser --disabled-password --no-create-home doe

USER doe

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
