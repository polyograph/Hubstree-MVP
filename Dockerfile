# Hubstree: frontend estático + verificação GuruDev num único serviço (Cloud Run).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8080

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY servidor.py .
COPY api ./api
COPY public ./public

# Gera as tabelas do parser da GuruDev (PLY) na imagem, para não refazer a cada requisição.
RUN python -c "import sys; sys.path.insert(0, 'api/_lib'); from gurudev.parser import build_parser; build_parser(debug=False, outputdir='api/_lib/gurudev')" \
    && useradd --uid 10001 --no-create-home hubstree

USER hubstree
EXPOSE 8080
CMD ["python", "servidor.py"]
