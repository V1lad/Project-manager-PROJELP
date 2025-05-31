FROM python:3.11.6-slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY Web Web
COPY Main.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP=Main

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]