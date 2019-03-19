FROM python:3
MAINTAINER Petr Novák 2 <petr.novak2@firma.seznam.cz>

RUN pip install flask
COPY backend.py /app/backend.py

EXPOSE 80
CMD ["python3", "/app/backend.py"]
