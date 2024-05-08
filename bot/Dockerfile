FROM python

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "/app/pt_telegram_bot.py" ]