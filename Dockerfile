FROM alpine:3.10

COPY LICENSE README.md /

COPY entrypoint.py /entrypoint.py

ENTRYPOINT ["/entrypoint.py"]
