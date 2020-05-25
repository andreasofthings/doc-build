FROM python:3-alpine

COPY LICENSE README.md /
COPY entrypoint.py /entrypoint.py

ENTRYPOINT ["python", "/entrypoint.py"]
