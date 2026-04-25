FROM python:3.11-slim

WORKDIR /app

# Install Python deps first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt python-telegram-bot==22.7

# Copy source
COPY . .

# Telegram bot is long-running; no port needed
CMD ["python", "telegram_bot.py"]
