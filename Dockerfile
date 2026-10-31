FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir uv==0.13.6
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY app ./app
COPY data ./data
EXPOSE 8000
CMD ["uv", "run", "--frozen", "--no-dev", "uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
