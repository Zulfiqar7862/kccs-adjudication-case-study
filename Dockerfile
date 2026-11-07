FROM python:3.13-slim
WORKDIR /app
# Explicit COPY allowlist prevents the local-only workbook, outputs and evidence entering image layers.
COPY pyproject.toml requirements.txt ./
COPY prototype/src ./prototype/src
COPY prototype/tests/fixtures ./prototype/tests/fixtures
RUN pip install --no-cache-dir . && useradd --create-home runner && mkdir -p /app/prototype/output && chown -R runner:runner /app
USER runner
ENTRYPOINT ["python", "-m", "adjudication.cli"]
CMD ["--fixtures", "prototype/tests/fixtures", "--out", "prototype/output"]
