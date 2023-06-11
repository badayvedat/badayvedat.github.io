FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    curl rsync build-essential git

RUN curl -o smu.tar.gz https://git.sr.ht/~bt/smu/archive/1544a3321b77255e193f0c044a8c32b09be99c50.tar.gz
RUN tar xzf smu.tar.gz

RUN cd smu-1544a3321b77255e193f0c044a8c32b09be99c50 && make install

WORKDIR /app

COPY . .

RUN make build