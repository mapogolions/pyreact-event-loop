FROM python:3.7
RUN apt-get update && apt-get upgrade -y && apt-get clean
RUN apt-get install libev-dev -y
RUN apt-get install libuv1-dev -y

COPY . /tmp
WORKDIR /tmp 

RUN pip install --upgrade pip && \
    pip install -r requirements.txt
RUN python /tmp/setup.py install

WORKDIR /tmp/examples

ENTRYPOINT ["python"]

CMD ["./timers.py"]
