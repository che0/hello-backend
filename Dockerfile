FROM python:3
MAINTAINER Petr Novák 2 <petr.novak2@firma.seznam.cz>

RUN pip install flask mysqlclient
COPY src /app

EXPOSE 80
CMD ["python3", "/app/backend.py"]
