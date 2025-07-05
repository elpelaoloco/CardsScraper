# Usar imagen base de Python
FROM python:3.11-slim

# Instalar dependencias mínimas para Chromium
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/chromium /usr/bin/google-chrome

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias (incluyendo dependencias de test)
COPY requirements.txt* ./
COPY requirements-test.txt* ./

# Instalar dependencias Python
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi
RUN if [ -f requirements-test.txt ]; then pip install --no-cache-dir -r requirements-test.txt; fi

# Copiar el contenido de app/ directamente a /app/
COPY app/ ./

# Copiar carpeta de tests
COPY tests/ ./tests/

# Exponer puerto
EXPOSE 8000

# Establecer el entrypoint por defecto para tests
ENTRYPOINT ["python", "-m", "pytest"]