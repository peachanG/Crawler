FROM ubuntu:18.04
LABEL Maintainer="Masaya Kamioka <kenkman0427@gmail.com>"

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH /usr/local/bin:$PATH
ENV LANG C.UTF-8
ENV PYTHON_VERSION 3.7.3

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential checkinstall openssl tk-dev wget apt-utils git \
        libffi-dev libssl-dev libsqlite3-dev curl unzip \
        sudo swig mecab libmecab-dev mecab-ipadic-utf8 \
        language-pack-ja \
    && curl -sL https://deb.nodesource.com/setup_9.x | bash - \
    && apt-get install -y nodejs npm \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir /tmp/python3

# Install Python37
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

# Support Japanese
RUN update-locale LANG=ja_JP.UTF-8
ENV LANG ja_JP.UTF-8

# Install Python library
COPY requirements.txt /work/requirements.txt
RUN pip3 install -r requirements.txt

# JupyterLab extensions
RUN jupyter labextension install "@lckr/jupyterlab_variableinspector"
RUN jupyter labextension install "@krassowski/jupyterlab_go_to_definition"
RUN jupyter labextension install "@jupyterlab/toc"
EXPOSE 8888

# Install mecab
RUN git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git\
    && mecab-ipadic-neologd/bin/install-mecab-ipadic-neologd -n -y -p /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd \
    && rm -rf mecab-ipadic-neologd
RUN sed -i 's/dicdir = \/var\/lib\/mecab\/dic\/debian/dicdir = \/usr\/lib\/x86_64-linux-gnu\/mecab\/dic\/mecab-ipadic-neologd/' /etc/mecabrc
RUN pip3 install mecab-python3

# Install Ginza
RUN git clone 'https://github.com/peachanG/ginza.git' \
    && cd ginza \
    && git submodule update --init \
    && ./setup.sh \
    && pip3 install "https://github.com/megagonlabs/ginza/releases/download/v1.0.2/ja_ginza_nopn-1.0.2.tgz"

# Install fastText
RUN git clone --depth 1 https://github.com/facebookresearch/fastText.git
RUN pip3 install fastText/. \
    && rm -rf fastText

CMD jupyter lab --port=8888 --allow-root --ip=0.0.0.0 \
    --NotebookApp.password='sha1:d64ab5e4f2b3:2557966e4a31adb9fdf4ab66172db2aa6e64df9b'
