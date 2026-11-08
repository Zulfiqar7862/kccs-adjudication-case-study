FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY prototype/pyproject.toml prototype/requirements.txt ./prototype/
COPY prototype/src ./prototype/src
RUN python -m pip install --no-cache-dir ./prototype \
    && groupadd --gid 10001 sentinel \
    && useradd --uid 10001 --gid sentinel --no-create-home sentinel
USER 10001:10001
ENTRYPOINT ["python", "-m", "sentinel"]
CMD ["demo"]
