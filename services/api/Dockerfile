FROM python:3.13-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN addgroup --system app && adduser --system --ingroup app app
COPY services/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/api/app ./app
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.getenv('PORT',os.getenv('API_PORT','8000'))+'/health/live',timeout=3)"
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-${API_PORT:-8000}} --no-proxy-headers"]
