FROM ubuntu:18.04
LABEL Maintainer="Masaya Kamioka <kenkman0427@gmail.com>"

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH /usr/local/bin:$PATH
ENV LANG C.UTF-8
ENV PYTHON_VERSION 3.7.3

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential checkinstall openssl tk-dev wget apt-utils git \
        libffi-dev libssl-dev libsqlite3-dev \
	&& rm -rf /var/lib/apt/lists/* \
  && mkdir /tmp/python3

WORKDIR /tmp/Python3
RUN wget --no-check-certificate https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-${PYTHON_VERSION%%[a-z]*}.tar.xz \
    && tar xvf Python-${PYTHON_VERSION%%[a-z]*}.tar.xz \
    && cd Python-${PYTHON_VERSION%%[a-z]*} \
    && ./configure --enable-optimizations \
    && make altinstall

RUN cd /usr/local/bin \
	&& ln -s python3.7 python \
    && ln -s python3.7 python3 \
    && ln -s pip3.7 pip \
    && ln -s pip3.7 pip3

WORKDIR /work
RUN rm -rf /tmp/Python3
COPY requirements.txt /work/requirements.txt

RUN pip3 install -r requirements.txt
EXPOSE 8888
