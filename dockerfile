FROM  python:3.11-slim
WORKDIR  /app
COPY /flask  /app/
RUN  pip install -r requirements.txt
