FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
RUN uv pip install --system .

COPY offloading_manager/ ./offloading_manager/

EXPOSE 8000

CMD ["uvicorn", "offloading_manager.main:app", "--host", "0.0.0.0", "--port", "8000"]