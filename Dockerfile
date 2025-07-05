FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/chromium /usr/bin/google-chrome

WORKDIR /app

COPY requirements.txt* ./
COPY requirements-test.txt* ./

RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi
RUN if [ -f requirements-test.txt ]; then pip install --no-cache-dir -r requirements-test.txt; fi

COPY app/ ./

COPY tests/ ./tests/

EXPOSE 8000

ENTRYPOINT ["python", "-m", "pytest"]