FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install flask flask-cors python-dotenv psycopg2-binary flask-sqlalchemy flask-migrate

CMD ["python", "app.py"]