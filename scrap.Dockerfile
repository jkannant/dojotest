FROM python:latest

RUN mkdir -p /var/html

WORKDIR /var/html

COPY scrap.py .

RUN pip install requests && pip install schedule

RUN touch index.html

CMD ["python","./scrap.py"]
