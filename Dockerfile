FROM python:3.9.13

ENV TOKEN=********************************************

WORKDIR /app/bot

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "bot_tg.py" ]
