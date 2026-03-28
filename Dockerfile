FROM python:3.7-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        libev-dev \
        libuv1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . /tmp
WORKDIR /tmp 

RUN pip install --upgrade pip && \
    pip install -r requirements.txt
RUN python /tmp/setup.py install

WORKDIR /tmp/examples

ENTRYPOINT ["python"]
CMD ["./timers.py"]