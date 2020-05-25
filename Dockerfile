FROM python:3-alpine

RUN pip install --upgrade sphinx
COPY LICENSE README.md /
COPY entrypoint.py /entrypoint.py

ENTRYPOINT ["python", "/entrypoint.py"]
