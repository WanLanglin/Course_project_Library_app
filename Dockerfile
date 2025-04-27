FROM python:3.11

WORKDIR /app

# Install debugging tools
RUN pip install debugpy

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . . 